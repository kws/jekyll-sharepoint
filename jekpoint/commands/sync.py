from jekpoint.html import SharepointHtml
from jekpoint.api import SharePointApi
from jekpoint.sync_jekyll import JekyllSync
from jekpoint.sync_sharepoint import SharepointSync


def add_arguments(parser):
    parser.add_argument('folder', type=str, help='The folder to synchronise from')


def run(args, config):
    upload_pages(args.folder, config)
    upload_images(args.folder, config)


def upload_pages(folder, config):
    html = SharepointHtml(config.site_prefix)
    jekyll = JekyllSync(folder, html_gen=html.convert_html)
    api = SharePointApi(config.client,
                        f"{config.site_url}{config.site_prefix}/",
                        f"{config.site_prefix}/{config.site_pages}/")
    sharepoint = SharepointSync(api, config)

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


def upload_images(folder, config):
    jekyll = JekyllSync(folder)
    api = SharePointApi(config.client,
                        f"{config.site_url}{config.site_prefix}/",
                        f"{config.site_prefix}/{config.site_assets}/")

    # Get all image files that need to be uploaded
    files = jekyll.website_images()
    folders = jekyll.get_file_folders(files)
    for p in folders:
        print("Creating", p)
        api.create_folder(p)

    # Fetch file metadata
    file_metadata = api.get_list(config.site_assets_list, property='files').value['value']
    file_metadata = {m['Url']: m for m in file_metadata}

    for file in files:
        path = file.rel_path
        est_url = f'{config.site_url}{config.site_prefix}/{config.site_assets}/{path}'

        print(f"Uploading {str(path)}: {est_url}")
        size = file_metadata.get(est_url, {}).get('Size', -1)
        if size == file.abs_path.stat().st_size:
            print(" * File size unchanged, skipping")
            continue

        data = file.abs_path.read_bytes()
        api.upload_file(path.parent, path.name, data)



