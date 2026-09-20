# -*- coding: utf-8 -*-

# Sample Python code for youtube.subscriptions.list
# See instructions for running these code samples locally:
# https://developers.google.com/explorer-help/code-samples#python

import os
import asyncio
from pathlib import Path
from pydantic import BaseModel
from google.oauth2.credentials import Credentials as CREDO
from google.auth.external_account_authorized_user import Credentials as CREDA
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.http import HttpRequest
import googleapiclient.discovery
# import googleapiclient.errors
from . import constants

class YouTubeSubscriptionInfo(BaseModel):
    channel_ID: str
    channel_name: str
    channel_descr: str


class UnsubscribeResult(BaseModel):
    subscription_ID: str
    status_code: int


class YouTubeSubscriptions:

    def __init__(self, token_file: Path, secrets_file: Path) -> None:
        self.subs: list[YouTubeSubscriptionInfo] = []
        self.token_file = token_file
        self.secrets_file = secrets_file

    async def get_secure_credentials(self) -> CREDO | CREDA:
        """
        Securely use Google OAuth library to get auth and reset tokens for
        an authenticated YouTube user.  Token info is saved in a file in the
        user's home folder so it can be read later and used future authorization.
        """
        # Disable OAuthlib's HTTPS verification when running locally.
        # *DO NOT* leave this option enabled in production.
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

        creds: CREDA | CREDO | None = None
        if self.token_file.exists():
            creds = await asyncio.to_thread(CREDO.from_authorized_user_file, 
                str(self.token_file),
                constants.SCOPES
            )
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                print("Access token expired. Refreshing...")
                await asyncio.to_thread(creds.refresh, Request())
            else:
                print("No valid tokens found. Initiating login flow...")
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.secrets_file, 
                    constants.SCOPES
                )
                creds = await asyncio.to_thread(
                    flow.run_local_server, 
                    port=0
                )
            # Save tokens
            config_dir = self.token_file.parent
            config_dir.mkdir(parents=True, exist_ok=True)
            with open(self.token_file, 'w') as tf:
                tf.write(creds.to_json())
            os.chmod(self.token_file, 0o600)
            print("Tokens securely saved.")
        return creds

    async def get_subscriptions(self) -> list[YouTubeSubscriptionInfo]:
        """
        Get list of all subscribed channels for authenticated YouTube user
        """
        # Get credentials and create an API client
        credentials = await self.get_secure_credentials()
        youtube = await asyncio.to_thread(
            googleapiclient.discovery.build,
            constants.API_SERVICE_NAME, 
            constants.API_VERSION, 
            credentials=credentials
        )
        results: list[YouTubeSubscriptionInfo] = []
        next_page_token = None
        while True:
            # Use API client to retrieve subscription data
            request = await asyncio.to_thread(
                youtube.subscriptions().list,
                part="snippet",
                mine=True,
                maxResults=constants.MAX_SUBS_RESULTS,
                pageToken=next_page_token
            )
            response = await asyncio.to_thread(request.execute)
            for item in response.get(constants.YT_API_ITEMS_KEY, []):
                results.append(
                    YouTubeSubscriptionInfo(
                        channel_ID=item['id'],
                        channel_name=item[constants.YT_API_SNIPPET_KEY][constants.YT_API_TITLE_KEY],
                        channel_descr=item[constants.YT_API_SNIPPET_KEY][constants.YT_API_DESCR_KEY],
                    )
                )
            next_page_token = response.get("nextPageToken")
            if not next_page_token:
                break
        return results


    async def unsubscribe_from_channel(self, subs_id: str) -> bool:
        """
        Unsubscribe from given subscription ID
        """
        # Get credentials and create an API client
        credentials = await self.get_secure_credentials()
        youtube = await asyncio.to_thread(
            googleapiclient.discovery.build,
            constants.API_SERVICE_NAME, 
            constants.API_VERSION, 
            credentials=credentials
        )
        # Use API client to retrieve subscription data
        request: HttpRequest = await asyncio.to_thread(
            youtube.subscriptions().delete,
            id=subs_id
        )
        try:
            await asyncio.to_thread(request.execute)
            return True
        except Exception as e:
            print(f"Error unsubscribing: {e}")
            return False


def main() -> None:
    pass


if __name__ == "__main__":
    main()
