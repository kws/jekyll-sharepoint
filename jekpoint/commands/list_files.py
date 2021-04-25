import json

from bs4 import BeautifulSoup

from jekpoint.api import SharePointApi


def add_arguments(parser):
    parser.add_argument('--list-name', '-l', type=str,
                        help='Which list to dump',
                        default="Site Pages")


def run(args, config):
    api = SharePointApi(config.client,
                        f"{config.site_url}{config.site_prefix}/",
                        f"{config.site_prefix}")

    list_name = args.list_name

    result = api.get_list(list_name, property='items', params=[
        ('$select', 'FieldValuesAsText/FSObjType'),
        ('$select', 'FieldValuesAsText/FileRef'),
        ('$expand', 'FieldValuesAsText'),
        ('$expand', 'Properties'),
    ])
    items = result.json()
    for item in items['value']:
        fields = item['FieldValuesAsText']
        properties = item['Properties']
        file_type = fields['FSObjType']
        filename = fields['FileRef']
        content = properties.get('CanvasContent1')

        try:
            soup = BeautifulSoup(content, 'html.parser')
            checksum = soup.select_one('div[data-checksum]').attrs.get('data-checksum')
        except (TypeError, AttributeError):
            checksum = ''

        print(file_type, filename, checksum)