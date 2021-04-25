import os, re

from jekpoint.auth import get_authorised_client


class Config:

    def __init__(self, site_url=None, use_dotenv=True):
        if use_dotenv:
            from dotenv import load_dotenv
            load_dotenv()

        if not site_url:
            site_url = os.getenv('SHAREPOINT_SITE_URL')

        if not site_url:
            raise ValueError("<SHAREPOINT_SITE_URL> must be set")

        match = re.match(
            r'(https?://(\w+)\.sharepoint\.com)(/sites/(\w+))?/?',
            site_url, flags=re.IGNORECASE
        )

        if not match:
            raise ValueError(f"Could not parse <SHAREPOINT_SITE_URL>: {site_url}")

        self._config_url = site_url
        self.site_url = match.group(1)
        self.host_name = match.group(2)
        self.site_prefix = match.group(3)
        self.site_name = match.group(4)

        self.template_file = "_templates/Default.aspx"
        self.site_pages = os.getenv("SHAREPOINT_SITE_PAGES", "SitePages")
        self.site_pages_list = os.getenv("SHAREPOINT_SITE_PAGES_LIST",
                                         "Site Pages" if self.site_pages == "SitePages" else self.site_pages)

        self.site_assets = os.getenv("SHAREPOINT_SITE_ASSETS", "Site Assets")
        self.site_assets_list = os.getenv("SHAREPOINT_SITE_ASSETS_LIST", self.site_assets)

        self.client = get_authorised_client(self)
