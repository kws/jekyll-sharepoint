from bs4 import BeautifulSoup, Comment
from jekpoint.api import SharePointApi


def add_arguments(parser):
    parser.add_argument('page_name', type=str, help='Site-relative path to page')


def run(args, config):
    api = SharePointApi(config.client, f"{config.site_url}{config.site_prefix}/", f"{config.site_prefix}/{config.site_pages}/")
    result = api.get_page_details(args.page_name)
    print(result.text)
    data = result.value
    content_data = data['CanvasContent1']
    soup = BeautifulSoup(content_data, 'html.parser')
    for div in soup.find_all('div'):
        if control_data := div.get('data-sp-controldata'):
            div['data-sp-controldata'] = '@data@'
            div.insert(0, Comment(control_data))

    print(soup.prettify())

