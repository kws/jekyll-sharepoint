import os

from office365.runtime.auth.providers.acs_token_provider import ACSTokenProvider

from jekpoint.api import AuthorisingClient


class FakeRequest:
    """
    We need a fake request to authorise so we can pick up an authorisation token from the library.
    """
    def __init__(self):
        self.header = {}

    def set_header(self, header, value):
        self.header[header] = value

    def get_authorization_token(self):
        return self.header['Authorization'].split(' ')[1]


def get_authorised_client(config):
    provider = ACSTokenProvider(
        config.site_url,
        os.environ['SHAREPOINT_CLIENT_ID'],
        os.environ['SHAREPOINT_CLIENT_SECRET']
    )
    request = FakeRequest()
    provider.authenticate_request(request)
    return AuthorisingClient(request.get_authorization_token)