from pathlib import Path

SCOPES = ["https://www.googleapis.com/auth/youtube"]
CONFIG_DIR = Path.home() / '.config' / 'del-y-subs'
TOKEN_FILE = CONFIG_DIR / 'token.json'
CLIENT_SECRETS_FILE = Path("client_secrets.json")
MAX_SUBS_RESULTS = 50
API_SERVICE_NAME = "youtube"
API_VERSION = "v3"
YT_API_SNIPPET_KEY = "snippet"
YT_API_TITLE_KEY = "title"
YT_API_DESCR_KEY = "description"
YT_API_ITEMS_KEY = "items"
YT_API_ID_KEY = "id"
SELECTION_CHAR = "X"
DESELECTION_CHAR = "_"
