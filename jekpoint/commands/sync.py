import hashlib
from collections import namedtuple
from pathlib import Path

from bs4 import BeautifulSoup
from jinja2 import ChoiceLoader, FileSystemLoader, PackageLoader
from jinja2 import Environment, select_autoescape

from jekpoint.html import SharepointHtml
from jekpoint.api import SharePointApi
from jekpoint.sync_jekyll import JekyllSync
from jekpoint.sync_sharepoint import SharepointSync

FileMetaData = namedtuple('FileMetaData', ('name', 'site_relative_name', 'type', 'checksum'))
ImageMetaData = namedtuple('ImageMetaData', ('name', 'url', 'type', 'size'))


def add_arguments(parser):
    parser.add_argument('folder', type=str, help='The folder to synchronise from')
    parser.add_argument('--template', '-t', type=str, metavar='FILE',
                        help='A Jinja template for rendering the output')
    parser.add_argument('--show', '-s', action='store_true',
                        help='Show the HTML output as it\'s written')
    parser.add_argument('--dry-run', action='store_true',
                        help="Run generation, but don't upload files")
    parser.add_argument('--force', '-f', action='store_true',
                        help="Force upload even if not changed.")


def run(args, config):
    if args.template:
        template = get_jinja_template(args.template, config)
    else:
        template = None
    upload_pages(args.folder, config, template=template, show=args.show, dry_run=args.dry_run,
                 force=args.force)
    upload_images(args.folder, config, dry_run=args.dry_run)


def shape_file_metadata(config):
    site_prefix = f'{config.site_prefix}/{config.site_pages}/'

    def _function(item):
        fields = item['FieldValuesAsText']
        properties = item['Properties']
        site_relative_name = fields['FileRef']
        content = properties.get('CanvasContent1')
        try:
            soup = BeautifulSoup(content, 'html.parser')
            checksum = soup.select_one('div[data-checksum]').attrs.get('data-checksum')
        except (TypeError, AttributeError):
            checksum = ''
        return FileMetaData(
            name=site_relative_name.removeprefix(site_prefix),
            site_relative_name=site_relative_name,
            type=fields['FSObjType'],
            checksum=checksum,
        )

    return _function


def shape_image_metadata(config):
    url_prefix = f'{config.site_url}{config.site_prefix}/{config.site_assets}/'

    def _function(item):
        return ImageMetaData(
            name=item['Url'].removeprefix(url_prefix),
            url=item['Url'],
            size=item['Size'],
            type=item['odata.type'],
        )

    return _function


def upload_pages(folder, config, template=None, show=False, dry_run=False, force=False):
    html = SharepointHtml(config.site_prefix, template=template)
    jekyll = JekyllSync(folder, html_gen=html.convert_html)
    api = SharePointApi(config.client,
                        f"{config.site_url}{config.site_prefix}/",
                        f"{config.site_prefix}/{config.site_pages}/")
    sharepoint = SharepointSync(api, config)

    # Get all site metadata
    file_metadata = api.get_list(config.site_pages_list, property='items', params=[
        ('$select', 'FieldValuesAsText/FSObjType'),
        ('$select', 'FieldValuesAsText/FileRef'),
        ('$expand', 'FieldValuesAsText'),
        ('$expand', 'Properties'),
    ])
    file_metadata = map(shape_file_metadata(config), file_metadata.json()['value'])
    file_metadata = {md.name: md for md in file_metadata}

    # Get all HTML files that need to be uploaded
    files = jekyll.website_files()
    folders = jekyll.get_file_folders(files)
    for p in folders:
        if not str(p) in file_metadata:
            print("Creating", p)
            if not dry_run:
                api.create_folder(p)
        else:
            print(f"{p} already exists")

    for file in files:
        path = file.rel_path
        page_name = str(path)

        if page_name.endswith('.html'):
            page_name = page_name[:-5]
        if not page_name.endswith('.aspx'):
            page_name = f'{page_name}.aspx'

        metadata = file_metadata.get(page_name)
        checksum = hashlib.sha256(file.html.encode('utf-8')).hexdigest()

        if force or metadata is None or checksum != metadata.checksum:
            if metadata is None:
                print(f"Creating {str(path)}")
                if not dry_run:
                    sharepoint.create_page(page_name, overwrite=False)
            else:
                print(f"Updating {str(path)}")

            if not dry_run:
                sharepoint.update_page(page_name, file.front_matter, file.html, checksum)

            if show:
                print(file.html)


def upload_images(folder, config, dry_run=False):
    jekyll = JekyllSync(folder)
    api = SharePointApi(config.client,
                        f"{config.site_url}{config.site_prefix}/",
                        f"{config.site_prefix}/{config.site_assets}/")

    # Fetch file metadata
    file_metadata = api.get_list(config.site_assets_list, property='files')
    file_metadata = map(shape_image_metadata(config), file_metadata.json()['value'])
    file_metadata = {md.name: md for md in file_metadata}

    # Get all image files that need to be uploaded
    files = jekyll.website_images()
    folders = jekyll.get_file_folders(files)
    for p in folders:
        if not str(p) in file_metadata:
            print("Creating", p)
            if not dry_run:
                api.create_folder(p)
        else:
            print(f"{p} already exists")

    for file in files:
        path = file.rel_path
        metadata = file_metadata.get(str(path))

        if metadata is None or file.abs_path.stat().st_size != metadata.size:
            print("Uploading", path)
            data = file.abs_path.read_bytes()
            if not dry_run:
                api.upload_file(path.parent, path.name, data)


def get_jinja_template(template, config):
    # If the path provided is a file, then we configure the a filesystem loader relative to that file
    template = Path(template)
    if template.is_file():
        fs_loader = FileSystemLoader(str(template.parent.resolve()))
        template = template.name
    else:
        fs_loader = FileSystemLoader(str(Path().resolve()))
        template = str(template.resolve())

    p_loader = PackageLoader("jekpoint")
    loader = ChoiceLoader([fs_loader, p_loader])
    env = Environment(
        loader=loader,
        autoescape=select_autoescape(['html', 'xml']),
    )
    env.globals['config'] = config
    return env.get_template(template)

