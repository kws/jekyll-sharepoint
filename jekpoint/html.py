from pathlib import Path
from urllib.parse import urlparse

from bs4 import BeautifulSoup
import re

from markupsafe import Markup

__pattern = re.compile(r'([^:])//+')


def remove_double_slash(value):
    return __pattern.sub(r'\1/', value)


class SharepointHtml:

    def __init__(self, site_url, site_dir='SitePages', asset_dir='Site Assets', template=None):
        self.link_prefix = f"{site_url}/{site_dir}/"
        self.asset_prefix = f"{site_url}/{asset_dir}/"
        self.template = template

    def convert_html(self, html, rel_path):
        soup = BeautifulSoup(html, 'html.parser')
        ptn_start = re.compile(r'^https?')
        ptn_ext = re.compile(r'.html?$')
        for a in soup.find_all('a'):
            href = a['href']
            if not ptn_start.search(href):
                path = Path(rel_path).parent / Path(href)
                # Attempt to simplify path
                try:
                    path = path.resolve(strict=False).relative_to(Path().resolve())
                except ValueError:
                    pass

                # This is a very special case - the index/home page of a sharepoint site is actually
                # one folder higher than the rest of the site.
                if str(path) == "/":
                    path = "../"

                href = f'{self.link_prefix}/{path}'
            href = ptn_ext.sub('.aspx', href)
            href = remove_double_slash(href)

            a['data-cke-saved-href'] = a['href']
            a['data-interception'] = 'on'
            a['title'] = a['href']
            a['href'] = href

        pattern = re.compile(r'^/images/')
        for img in soup.find_all('img'):
            src = pattern.sub(self.asset_prefix, img['src'])
            src = remove_double_slash(src)
            img['src'] = src

        output = "".join([str(c) for c in soup.find('div', id='bodycontent').children])

        front_matter = {}
        if title := soup.find('title'):
            front_matter['title'] = title.text

        if self.template:
            output = self.template.render(body=Markup(output), front_matter=front_matter,
                                          link_prefix=self.link_prefix, asset_prefix=self.asset_prefix)

        return output, front_matter
