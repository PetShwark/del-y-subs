from .app import DelYSubsApp
from .constants import CLIENT_SECRETS_FILE, TOKEN_FILE

def main():
    app = DelYSubsApp(
        token_file_path=TOKEN_FILE, 
        client_secrets_file_path=CLIENT_SECRETS_FILE
    )
    app.run()

if __name__ == "__main__":
    main()