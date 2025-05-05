# actionapi/utils/sheet_updater.py
import os
import gspread
from google.oauth2.service_account import Credentials
from ..models import DemandTitle, Demand, PatientType, Action
import traceback  # Import traceback for better error logging

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GOOGLE_SHEET_CREDENTIALS_FILE = os.path.join(BASE_DIR, "utils", "urlvalidate.json")


def update_customer_from_sheet(customer):
    """
    Fetches data from the customer's Google Sheet (starting from row 3),
    processes it based on fixed column order, and updates related models.
    """
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
        customer.filetitle = spreadsheet_title
        customer.save(update_fields=["filetitle"])
        print(f"💾 Customer filetitle updated to: {spreadsheet_title}")

        # --- MODIFIED DATA READING ---
        print(f"📊 Attempting to fetch all values from worksheet...")
        # Step 4: Read all rows as lists using get_values()
        all_values = worksheet.get_values()

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
        action_idx = 3  # Column D
        print(
            f"📝 Using column indices: Title={title_idx}, Demand={demand_idx}, PatientType={patient_type_idx}, Action={action_idx}"
        )

        # Step 5: Delete old data (Unchanged)
        customer.demand_titles.all().delete()
        print("🧹 Old data deleted.")

        # Step 6: Build nested data structure in memory using indices
        structured_data = {}
        processed_rows_count = 0
        skipped_rows_count = 0
        for row_idx, row in enumerate(data_rows):
            sheet_row_num = row_idx + 3  # Actual sheet row number (1-based)
            try:
                # Ensure row has enough columns before accessing indices
                # Use max index + 1 for the length check
                required_cols = (
                    max(title_idx, demand_idx, patient_type_idx, action_idx) + 1
                )
                if len(row) < required_cols:
                    # print(f"⚠️ Skipping sheet row {sheet_row_num} due to insufficient columns ({len(row)} needed {required_cols}). Row: {row}")
                    skipped_rows_count += 1
                    continue

                # Get values using indices, default to empty string, convert to string
                title = str(row[title_idx]).strip()
                demand = str(row[demand_idx]).strip()
                patient_type = str(row[patient_type_idx]).strip()
                action = str(row[action_idx]).strip()

                # Skip row if the essential 'Title' field is missing
                if not title:
                    # print(f"Skipping sheet row {sheet_row_num} due to missing Title.")
                    skipped_rows_count += 1
                    continue

                # Build the nested dictionary
                structured_data.setdefault(title, {})
                if demand:
                    structured_data[title].setdefault(demand, {})
                    if patient_type:
                        structured_data[title][demand].setdefault(patient_type, [])
                        if action:
                            structured_data[title][demand][patient_type].append(action)
                processed_rows_count += 1

            except IndexError:
                # Should be less likely with the length check above, but catches edge cases
                print(
                    f"⚠️ Skipping sheet row {sheet_row_num} due to IndexError. Row data: {row}"
                )
                skipped_rows_count += 1
                continue
            except Exception as inner_ex:
                # Catch other potential errors during row processing
                print(
                    f"⚠️ Error processing sheet row {sheet_row_num}: {inner_ex}. Row data: {row}"
                )
                skipped_rows_count += 1
                continue

        print(
            f"🏗️ Structured data built. Processed={processed_rows_count}, Skipped={skipped_rows_count} (starting from row 3)"
        )

        # Step 7: Save to DB with full nesting (Unchanged logic)
        for title_name, demands in structured_data.items():
            dt = DemandTitle.objects.create(customer=customer, title=title_name)
            for demand_name, patient_types in demands.items():
                d = Demand.objects.create(demand_title=dt, name=demand_name)
                for patient_type_name, actions in patient_types.items():
                    pt = PatientType.objects.create(demand=d, name=patient_type_name)
                    for action_desc in actions:
                        Action.objects.create(patient_type=pt, description=action_desc)
        print(f"💾 Database updated for customer {customer.did_number}.")

        # --- Success Response ---
        return {
            "status": "success",
            "records_added": processed_rows_count,
            "spreadsheet_title": spreadsheet_title,
            "message": f"Sheet processed successfully. Processed {processed_rows_count} data rows starting from row 3.",
        }

    # --- Enhanced Error Handling (Keep as is) ---
    except gspread.exceptions.APIError as e:
        print(f"❌ gspread API Error: {e}")
        error_details = f"Google Sheets API error ({e.response.status_code} {e.response.reason}). Check sheet permissions/URL or API quotas."
        try:
            error_json = e.response.json()
            error_message = error_json.get("error", {}).get("message", "")
            if error_message:
                error_details = f"Google Sheets API error: {error_message}"
        except Exception:
            pass
        return {"status": "error", "error": error_details}
    except gspread.exceptions.SpreadsheetNotFound:
        print(f"❌ Spreadsheet not found with ID {sheet_id}.")
        return {
            "status": "error",
            "error": "Google Sheet not found. Check the Sheet URL.",
        }
    except gspread.exceptions.WorksheetNotFound:
        print(f"❌ Worksheet 'detail' not found in sheet ID {sheet_id}.")
        return {
            "status": "error",
            "error": "Worksheet named 'detail' not found in the Google Sheet.",
        }
    except FileNotFoundError:
        print(f"❌ Credentials file not found at {GOOGLE_SHEET_CREDENTIALS_FILE}")
        return {
            "status": "error",
            "error": "Server configuration error: Could not find credentials file.",
        }
    except Exception as e:
        print(f"❌ Unexpected Exception in update_customer_from_sheet: {e}")
        print(traceback.format_exc())
        return {
            "status": "error",
            "error": f"An unexpected server error occurred during sheet processing: {str(e)}",
        }
