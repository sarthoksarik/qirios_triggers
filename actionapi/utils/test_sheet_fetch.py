from sheet_updater import update_customer_from_sheet, BASE_DIR

customer = {
    "name": "2 cab",
    "did_number": "23290",
    "sheet_url": "https://docs.google.com/spreadsheets/d/1lfT-hG54DIoPLh-hwuzRDptrCU51b4LMjhXFGqil3Bg/edit?gid=0#gid=0",
}

update_customer_from_sheet(customer=customer, created=False)
