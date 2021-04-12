import os
from dotenv import load_dotenv
from msgraphy.client.graph_client import RequestsGraphClient
from msgraphy.sharepoint_classic import SharePointApi
from office365.runtime.auth.providers.acs_token_provider import ACSTokenProvider

load_dotenv()

provider = ACSTokenProvider(
    f"https://{os.environ['SHAREPOINT_HOSTNAME']}.sharepoint.com/",
    os.environ['SHAREPOINT_CLIENT_ID'],
    os.environ['SHAREPOINT_CLIENT_SECRET']
)


class RequestWrapper:

    def __init__(self):
        self.header = {}

    def set_header(self, header, value):
        self.header[header] = value

    def get_authorization_token(self):
        return self.header['Authorization'].split(' ')[1]


request = RequestWrapper()
provider.authenticate_request(request)

client = RequestsGraphClient(request.get_authorization_token)

SITE_PREFIX = os.environ['SHAREPOINT_SITE']
SITE_URL = f"https://{os.environ['SHAREPOINT_HOSTNAME']}.sharepoint.com{SITE_PREFIX}"
SERVER_RELATIVE_URL = f"{SITE_PREFIX}/SitePages/"
LINK_PREFIX = f"{SITE_URL}/SitePages/"

api = SharePointApi(client, f"{SITE_URL}/", SERVER_RELATIVE_URL)
