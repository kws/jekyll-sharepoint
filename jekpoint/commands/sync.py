from pathlib import Path

from jinja2 import ChoiceLoader, FileSystemLoader, PackageLoader
from jinja2 import Environment, select_autoescape

from jekpoint.html import SharepointHtml
from jekpoint.api import SharePointApi
from jekpoint.sync_jekyll import JekyllSync
from jekpoint.sync_sharepoint import SharepointSync


def add_arguments(parser):
    parser.add_argument('folder', type=str, help='The folder to synchronise from')
    parser.add_argument('--template', '-t', type=str, metavar='FILE',
                        help='A Jinja template for rendering the output')


def run(args, config):
    if args.template:
        template = get_jinja_template(args.template, config)
    else:
        template = None
    upload_pages(args.folder, config, template=template)
    upload_images(args.folder, config)


def upload_pages(folder, config, template=None):
    html = SharepointHtml(config.site_prefix, template=template)
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
    file_metadata = api.get_list(config.site_assets_list, property='files')
    file_metadata = file_metadata.json()['value']
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


def get_jinja_template(template, config):
    # If the path provided is a file, then we configure the a filesystem loader relative to that file
    template = Path(template)
    if template.is_file():
        fs_loader = FileSystemLoader(str(template.parent.resolve()))
        template = template.name
    else:
        fs_loader = FileSystemLoader()
        template = str(template.resolve())

    p_loader = PackageLoader("jekpoint")
    loader = ChoiceLoader([fs_loader, p_loader])
    env = Environment(
        loader=loader,
        autoescape=select_autoescape(['html', 'xml']),
    )
    env.globals['config'] = config
    return env.get_template(template)

