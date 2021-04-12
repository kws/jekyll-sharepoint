#!/usr/bin/env python
import sys
from bs4 import BeautifulSoup, Comment
from config import api


def main(file):
    result = api.get_page_details(file)
    data = result.value
    content_data = data['CanvasContent1']
    soup = BeautifulSoup(content_data, 'html.parser')
    for div in soup.find_all('div'):
        if control_data := div.get('data-sp-controldata'):
            div['data-sp-controldata'] = '@data@'
            div.insert(0, Comment(control_data))

    print(soup.prettify())


if __name__ == '__main__':
    main(sys.argv[1])