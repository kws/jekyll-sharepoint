#!/usr/bin/env python
import json

from config import client, SITE_URL, SITE_PREFIX
from local_api import LocalApi


def main():
    api = LocalApi(client, f"{SITE_URL}/", f"{SITE_PREFIX}/SiteAssets/")

    result = api.get_list_items('Site Pages')
    with open('examples/list_items.json', 'wt') as file:
        json.dump(result.value, file, indent=4, sort_keys=True)

    result = api.get_list_items_filenames('Site Pages')
    with open('examples/list_items_filenames.json', 'wt') as file:
        json.dump(result.value, file, indent=4, sort_keys=True)

    result = api.get_list_stream('Site Pages')
    with open('examples/list_as_stream.json', 'wt') as file:
        json.dump(result.value, file, indent=4, sort_keys=True)

    result = api.get_list_stream_all('Site Pages')
    with open('examples/list_as_stream_all.json', 'wt') as file:
        json.dump(result, file, indent=4, sort_keys=True)


if __name__ == '__main__':
    main()



