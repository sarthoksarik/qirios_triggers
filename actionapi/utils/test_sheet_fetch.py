import os
import gspread
from google.oauth2.service_account import Credentials

# from ..models import DemandTitle, Demand, PatientType, Action
import traceback  # Import traceback for better error logging

# from collections import defaultdict
from pathlib import Path

# import re

BASE_DIR = Path(__file__).resolve().parent.parent
GOOGLE_SHEET_CREDENTIALS_FILE = BASE_DIR / "utils" / "urlvalidate.json"


def check_values():
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

        sheet_id = "1lfT-hG54DIoPLh-hwuzRDptrCU51b4LMjhXFGqil3Bg"
        print(f"🔑 Extracted Sheet ID: {sheet_id}")
        sheet = client.open_by_key(sheet_id)
        worksheet = sheet.worksheet("detail")  # Make sure worksheet name is correct
        print(f"📖 Worksheet '{worksheet.title}' accessed.")
        all_values = worksheet.get_all_values()
        print(av := all_values[0])
        print(type(av))

    except Exception as e:
        print(f"failed by {e}")


check_values()
