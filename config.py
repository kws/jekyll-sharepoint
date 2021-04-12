import os
from pathlib import Path

import msal
from dotenv import load_dotenv
from msgraphy.auth.graph_auth import FileSystemTokenCache, InteractiveTokenWrapper
from msgraphy.client.graph_client import RequestsGraphClient
from msgraphy.sharepoint_classic import SharePointApi

load_dotenv()

app = msal.PublicClientApplication(
    os.environ['SHAREPOINT_CLIENT_ID'],
    authority=f"https://login.microsoftonline.com/{os.environ['SHAREPOINT_TENANT']}",
    token_cache=FileSystemTokenCache(Path(__file__).parent / ".." / ".auth", save_on_exit=True),
)


client = RequestsGraphClient(InteractiveTokenWrapper(app, [
    f"https://{os.environ['SHAREPOINT_HOSTNAME']}.sharepoint.com/AllSites.Read",
    f"https://{os.environ['SHAREPOINT_HOSTNAME']}.sharepoint.com/AllSites.Write",
]))


SITE_URL = os.environ['SITE_URL']
SERVER_RELATIVE_URL = os.environ['SERVER_RELATIVE_URL']
LINK_PREFIX = os.environ['LINK_PREFIX']

api = SharePointApi(client, SITE_URL, SERVER_RELATIVE_URL)
