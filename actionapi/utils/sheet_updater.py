# actionapi/utils/sheet_updater.py
import re
import traceback  # Import traceback for better error logging
from collections import defaultdict
from pathlib import Path

import gspread
from django.db import transaction
from google.oauth2.service_account import Credentials

from ..models import Action, Demand, DemandTitle, PatientType

BASE_DIR = Path(__file__).resolve().parent.parent
GOOGLE_SHEET_CREDENTIALS_FILE = BASE_DIR / "utils" / "urlvalidate.json"


def update_customer_from_sheet(customer, created):
    """
    Fetches data from the customer's Google Sheet (starting from row 3),
    processes it based on fixed column order, and updates related models.
    """
    with transaction.atomic:
        try:
            # Step 1: Setup Google Sheets client (Unchanged)
            scopes = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
            creds = Credentials.from_service_account_file(
                GOOGLE_SHEET_CREDENTIALS_FILE, scopes=scopes
            )
            client = gspread.authorize(creds)
            print("✅ Google Sheets client authorized.")

            # Step 2: Open the sheet and get the worksheet (Unchanged)
            print(f"📄 Original sheet URL: {customer.sheet_url}")
            sheet_id = customer.sheet_url.split("/d/")[1].split("/")[0]
            print(f"🔑 Extracted Sheet ID: {sheet_id}")
            sheet = client.open_by_key(sheet_id)
            worksheet = sheet.worksheet("detail")  # Make sure worksheet name is correct
            print(f"📖 Worksheet '{worksheet.title}' accessed.")

            # Step 3: Get spreadsheet title and save to customer (Unchanged)
            spreadsheet_title = sheet.title

            sanitized_title = re.sub(r"-\d+$", "", spreadsheet_title)

            customer.filetitle = sanitized_title

            if created:
                customer.save(
                    update_fields=["filetitle"]
                )  # uncomment to update sheetname in each refresh
            print(f"💾 Customer filetitle updated to: {sanitized_title}")

            # --- MODIFIED DATA READING ---
            print(f"📊 Attempting to fetch all values from worksheet...")
            # Step 4: Read all rows as lists using get_values()
            all_values = worksheet.get_values()
            first_row = all_values[0]
            customer_name, customer_address, note1, note2, note3 = first_row[0:5]
            print(
                "additional fields",
                customer_name,
                customer_address,
                note1,
                note2,
                note3,
            )
            update_fields = [
                attr
                for attr, value in [
                    ("name", customer_name),
                    ("address", customer_address),
                    ("note1", note1),
                    ("note2", note2),
                    ("note3", note3),
                ]
                if not setattr(customer, attr, value)
            ]
            customer.save(update_fields=update_fields)
            # Check if sheet has data starting from row 3 (index 2)
            if not all_values or len(all_values) < 3:
                print("⚠️ Sheet does not contain data starting from row 3.")
                customer.demand_titles.all().delete()
                print("🧹 Old data deleted (sheet has less than 3 rows).")
                return {
                    "status": "success",
                    "records_added": 0,
                    "spreadsheet_title": spreadsheet_title,
                    "message": "Sheet processed successfully (No data found starting from row 3).",
                }

            print(f"📊 Total rows fetched: {len(all_values)}")
            # --- Start processing from the 3rd row (index 2) ---
            data_rows = all_values[2:]
            print(f"ℹ️ Processing {len(data_rows)} rows starting from sheet row 3.")

            # --- Column Indices (Based on your confirmation) ---
            title_idx = 0  # Column A
            demand_idx = 1  # Column B
            patient_type_idx = 2  # Column C
            action_desc_idx = 3  # Column D
            dire_text_idx = 4  # Column E
            print(
                f"Using column indices: Title={title_idx}, Demand={demand_idx},"
                f" PatientType={patient_type_idx}, ActionDesc={action_desc_idx},"
                f" DireText={dire_text_idx}"
            )

            # Step 5: Delete old data (Unchanged)
            customer.demand_titles.all().delete()
            print("🧹 Old data deleted.")

            # Step 6: Build nested data structure in memory using indices
            structured_data = defaultdict(
                lambda: defaultdict(lambda: defaultdict(list))
            )
            processed_rows_count = 0
            skipped_rows_count = 0
            for row_idx, row in enumerate(data_rows):
                sheet_row_num = row_idx + 3
                try:
                    # Check if row has enough columns for the first 4 essential fields
                    min_essential_cols = patient_type_idx + 1
                    if len(row) < min_essential_cols:
                        # print(f"⚠️ Skipping sheet row {sheet_row_num} due to insufficient columns for essential data ({len(row)} found, {min_essential_cols} expected). Row: {row}")
                        skipped_rows_count += 1
                        continue

                    title_name = str(row[title_idx]).strip()
                    demand_name = str(row[demand_idx]).strip()
                    patient_type_name = str(row[patient_type_idx]).strip()
                    # action_description = str(row[action_desc_idx]).strip()

                    # --- NEW Condition: Skip row if any of the first 4 columns are empty ---
                    if (
                        not title_name or not demand_name or not patient_type_name
                        # or not action_description
                    ):
                        # print(f"Skipping sheet row {sheet_row_num} due to missing data in one of the first four essential columns.")
                        skipped_rows_count += 1
                        continue

                    if len(row) > action_desc_idx:
                        action_description = str(row[action_desc_idx]).strip()

                    # Safely get dire_text (column E), default to empty string if missing
                    current_dire_text = ""
                    if len(row) > dire_text_idx:
                        current_dire_text = str(row[dire_text_idx]).strip()

                    # Now, append the data. It's okay if action_description is empty.
                    structured_data[title_name][demand_name][patient_type_name].append(
                        {
                            "description": action_description,
                            "dire_text": current_dire_text,
                        }
                    )
                    processed_rows_count += 1

                except (
                    Exception
                ) as inner_ex:  # Catch any other unexpected error for this row
                    print(
                        f"⚠️ Error processing sheet row {sheet_row_num}: {inner_ex}. Row data: {row}"
                    )
                    skipped_rows_count += 1
                    continue

            print(
                f"🏗️ Structured data built with defaultdict. Processed={processed_rows_count}, Skipped={skipped_rows_count}"
            )

            # Step 7: Save to DB with full nesting (Unchanged logic)
            for title_name_db, demands_db in structured_data.items():
                dt = DemandTitle.objects.create(customer=customer, title=title_name_db)
                for demand_name_db, patient_types_db in demands_db.items():
                    d = Demand.objects.create(demand_title=dt, name=demand_name_db)
                    for (
                        patient_type_name_db,
                        actions_list_of_dicts,
                    ) in patient_types_db.items():
                        pt = PatientType.objects.create(
                            demand=d, name=patient_type_name_db
                        )
                        for action_data_dict in actions_list_of_dicts:
                            Action.objects.create(
                                patient_type=pt,
                                description=action_data_dict["description"],
                                dire_text=action_data_dict["dire_text"],
                            )
            print(f"💾 Database updated for customer {customer.did_number}.")

            return {
                "status": "success",
                "records_added": processed_rows_count,
                "spreadsheet_title": spreadsheet_title,
                "message": f"Sheet processed successfully. Processed {processed_rows_count} data rows.",
            }

        # --- Enhanced Error Handling (Keep as is) ---
        # Exception handling (keep enhanced version)
        except gspread.exceptions.APIError as e:
            print(f"❌ gspread API Error: {e}")
            error_details = f"Google Sheets API error ({e.response.status_code} {e.response.reason}). Check permissions/URL or quotas."
            try:
                error_json = e.response.json()
                error_message = error_json.get("error", {}).get("message", "")
                if error_message:
                    error_details = f"Google Sheets API error: {error_message}"
            except Exception:
                pass
            return {"status": "error", "error": error_details}
        except gspread.exceptions.SpreadsheetNotFound:
            print(f"❌ Spreadsheet not found for ID extracted from URL.")
            return {"status": "error", "error": "Google Sheet not found. Check URL."}
        except gspread.exceptions.WorksheetNotFound:
            print(f"❌ Worksheet 'detail' not found in sheet.")
            return {"status": "error", "error": "Worksheet 'detail' not found."}
        except FileNotFoundError:
            print(f"❌ Credentials file not found: {GOOGLE_SHEET_CREDENTIALS_FILE}")
            return {"status": "error", "error": "Server config error: Credentials."}
        except Exception as e:
            print(
                f"❌ Unexpected Exception in update_customer_from_sheet: {type(e).__name__} - {e}"
            )
            print(traceback.format_exc())
            return {
                "status": "error",
                "error": f"Unexpected server error during sheet processing: {str(e)}",
            }
