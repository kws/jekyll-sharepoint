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


def upload_images(folder):
    jekyll = JekyllSync(folder)
    api = LocalApi(client, f"{SITE_URL}/", f"{SITE_PREFIX}/SiteAssets/")

    # Get all image files that need to be uploaded
    files = jekyll.website_images()
    folders = jekyll.get_file_folders(files)
    for p in folders:
        print("Creating", p)
        api.create_folder(p)

    for file in files:
        path = file.rel_path
        print(f"Uploading {str(path)}")
        with open(file.abs_path, 'rb') as FILE:
            data = FILE.read()
        api.upload_file(path.parent, path.name, data)


def main(folder):
    upload_pages(folder)
    upload_images(folder)


if __name__ == '__main__':
    folder = sys.argv[1]
    main(folder)
