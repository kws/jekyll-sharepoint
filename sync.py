#!/usr/bin/env python
import re
import sys
from pathlib import Path
from bs4 import BeautifulSoup
from config import api, LINK_PREFIX


def create_page(page_name, front_matter, html):
    if not page_name.endswith('.aspx'):
        page_name = f'{page_name}.aspx'

    response = api.copy_page('templates/_Template.aspx', page_name, overwrite=True)
    response = api.get_page_details(page_name)
    e_tag = response.headers.get('ETag')

    data = response.value
    if title := front_matter.get('title'):
        data['Title'] = title

    content_data = data['CanvasContent1']

    content_data = re.sub(
        r'<div data-sp-rte="">.*?</div>',
        f'<div data-sp-rte="">{html}</div>',
        content_data
    )
    data['CanvasContent1'] = content_data
    data = {k: v for k, v in data.items() if v is not None}
    response = api.update_page(page_name, e_tag, data)
    response = api.publish(page_name)


def upload_file(file, front_matter, html):
    create_page(file.stem, front_matter, html)


def convert_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    for a in soup.find_all('a'):
        if not (href := a['href']).startswith('http'):
            href = f'{LINK_PREFIX}{href.replace(".html", ".aspx")}'
        a['data-cke-saved-href'] = a['href']
        a['data-interception'] = 'on'
        a['title'] = a['href']
        a['href'] = href

    output = "".join([c.prettify() for c in soup.find('div', id='bodycontent').children if hasattr(c, 'prettify')])

    front_matter = {}
    if title := soup.find('title'):
        front_matter['title'] = title.text

    return output, front_matter


def main(folder):
    file_list = Path(folder).glob("*.html")
    for filename in file_list:
        if filename.name == '404.html':
            continue
        with open(filename, 'rt') as file:
            html = file.read()

        html, front_matter = convert_html(html)
        print(html)
        upload_file(filename, front_matter, html)


if __name__ == '__main__':
    main(sys.argv[1])
