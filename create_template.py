#!/usr/bin/env python
import json

from config import client, SITE_URL, SITE_PREFIX
from local_api import LocalApi


def main():
    api = LocalApi(client, f"{SITE_URL}/", f"{SITE_PREFIX}/SitePages/")
    response = api.create_folder("_templates")
    print(response.text)


if __name__ == '__main__':
    main()



