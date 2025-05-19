# sariktriggers/settings/prod.py
print("DEBUG: Attempting to load settings from prod.py")
from sariktriggers.settings.base import *  # Imports all settings from base, including SECRET_KEY

print(
    f"DEBUG: Value of STATIC_URL in prod.py (after importing base) is: '{STATIC_URL}'"
)
# DEBUG is set in .env for production, base.py will pick it up.
# If you want to be explicit for prod here:
# DEBUG = False

STATICFILES_DIRS = [
    "/home/sarik/qirios_frontend_build",
]
print(f"DEBUG: STATICFILES_DIRS in prod.py set to: {STATICFILES_DIRS}")
print("DEBUG: End of prod.py parsing attempt.")
