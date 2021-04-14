#!/usr/bin/env python
import sys

from config import client, SITE_URL, SITE_PREFIX
from sharepoint_html import SharepointHtml
from local_api import LocalApi
from sync.jekyll import JekyllSync
from sync.sharepoint import SharepointSync


def upload_pages(folder):
    html = SharepointHtml(SITE_PREFIX)
    jekyll = JekyllSync(folder, html_gen=html.convert_html)
    api = LocalApi(client, f"{SITE_URL}/", f"{SITE_PREFIX}/SitePages/")
    sharepoint = SharepointSync(api)

    # Get all HTML files that need to be uploaded
    files = jekyll.website_files()
    folders = jekyll.get_file_folders(files)
    for p in folders:
        print("Creating", p)
        api.create_folder(p)

    for file in files:
        path = file.rel_path
        print(f"Uploading {str(path)}")
        sharepoint.create_page(str(path), file.front_matter, file.html, overwrite=False)


def upload_images(folder, asset_path='SiteAssets', asset_list='Site Assets'):
    jekyll = JekyllSync(folder)
    api = LocalApi(client, f"{SITE_URL}/", f"{SITE_PREFIX}/{asset_path}/")

    # Get all image files that need to be uploaded
    files = jekyll.website_images()
    folders = jekyll.get_file_folders(files)
    for p in folders:
        print("Creating", p)
        api.create_folder(p)

    # Fetch file metadata
    file_metadata = api.get_list(asset_list, property='files').value['value']
    file_metadata = {m['Url']: m for m in file_metadata}

    for file in files:
        path = file.rel_path
        est_url = f'{SITE_URL}/{asset_path}/{path}'

        print(f"Uploading {str(path)}: {est_url}")
        size = file_metadata.get(est_url, {}).get('Size', -1)
        if size == file.abs_path.stat().st_size:
            print(" * File size unchanged, skipping")
            continue

        data = file.abs_path.read_bytes()
        api.upload_file(path.parent, path.name, data)


def main(folder):
    upload_pages(folder)
    upload_images(folder)


if __name__ == '__main__':
    folder = sys.argv[1]
    main(folder)
