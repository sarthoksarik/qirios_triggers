import os
import gspread
from google.oauth2.service_account import Credentials
from ..models import DemandTitle, Demand, PatientType, Action

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GOOGLE_SHEET_CREDENTIALS_FILE = os.path.join(BASE_DIR, "utils", "urlvalidate.json")


def update_customer_from_sheet(customer):
    try:
        # Step 1: Setup Google Sheets client
        scopes = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
        creds = Credentials.from_service_account_file(
            GOOGLE_SHEET_CREDENTIALS_FILE, scopes=scopes
        )
        client = gspread.authorize(creds)
        print("✅ Google Sheets client authorized.")

        # Step 2: Open the sheet and get the worksheet
        print(f"📄 Original sheet URL: {customer.sheet_url}")
        sheet_id = customer.sheet_url.split("/d/")[1].split("/")[0]
        print(f"🔑 Extracted Sheet ID: {sheet_id}")
        sheet = client.open_by_key(sheet_id)
        worksheet = sheet.worksheet("detail")
        print("📖 Worksheet accessed.")

        # Step 3: Get spreadsheet title and save to customer
        spreadsheet_title = sheet.title
        customer.filetitle = spreadsheet_title
        customer.save()

        # Step 4: Read all rows
        records = worksheet.get_all_records()
        print(f"📊 Total rows fetched: {len(records)}")

        # Step 5: Delete old data
        customer.demand_titles.all().delete()
        print("🧹 Old data deleted.")

        # Step 6: Build nested data structure in memory
        structured_data = {}
        for row in records:
            title = row.get("Title", "").strip()
            demand = row.get("Demande", "").strip()
            patient_type = row.get("Patient Type", "").strip()
            action = row.get("Action", "").strip()

            if not title:
                continue  # Skip if title is missing

            structured_data.setdefault(title, {})
            if demand:
                structured_data[title].setdefault(demand, {})
                if patient_type:
                    structured_data[title][demand].setdefault(patient_type, [])
                    if action:
                        structured_data[title][demand][patient_type].append(action)

        # Step 7: Save to DB with full nesting
        for title_name, demands in structured_data.items():
            dt = DemandTitle.objects.create(customer=customer, title=title_name)

            for demand_name, patient_types in demands.items():
                d = Demand.objects.create(demand_title=dt, name=demand_name)

                for patient_type_name, actions in patient_types.items():
                    pt = PatientType.objects.create(demand=d, name=patient_type_name)

                    for action_desc in actions:
                        Action.objects.create(patient_type=pt, description=action_desc)

        return {
            "status": "success",
            "records_added": len(records),
            "spreadsheet_title": spreadsheet_title,
        }

    except Exception as e:
        print(f"❌ Exception: {e}")
        return {"status": "error", "error": str(e)}
