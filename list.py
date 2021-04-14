#!/usr/bin/env python
import json

from config import client, SITE_URL, SITE_PREFIX
from local_api import LocalApi


def dump_result(filename, result):
    with open(filename, 'wt') as file:
        json.dump(result, file, indent=4, sort_keys=True)


def main():
    api = LocalApi(client, f"{SITE_URL}/", f"{SITE_PREFIX}/SiteAssets/")

    list_name = 'Site Assets'

    result = api.get_list_items(list_name)
    dump_result('examples/list_items.json', result.value)

    result = api.get_list(list_name, property='files')
    dump_result('examples/list_files.json', result.value)

    result = api.get_list_items_filenames(list_name)
    dump_result('examples/list_items_filenames.json', result.value)

    result = api.get_list_stream(list_name)
    dump_result('examples/list_as_stream.json', result.value)

    result = api.get_list_stream_all(list_name)
    dump_result('examples/list_as_stream_all.json', result)


if __name__ == '__main__':
    main()



