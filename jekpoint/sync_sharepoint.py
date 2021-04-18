import hashlib

from bs4 import BeautifulSoup


class SharepointSync:

    def __init__(self, api, config):
        self.api = api
        self.config = config

    def create_page(self, page_name, front_matter, html, overwrite=False, force=False):
        if page_name.endswith('.html'):
            page_name = page_name[:-5]
        if not page_name.endswith('.aspx'):
            page_name = f'{page_name}.aspx'

        self.api.copy_page(self.config.template_file, page_name, overwrite=overwrite)
        response = self.api.get_page_details(page_name)
        e_tag = response.headers.get('ETag')

        data = response.json()
        if title := front_matter.get('title'):
            data['Title'] = title

        content_data = data['CanvasContent1']

        soup = BeautifulSoup(content_data, 'html.parser')
        div = soup.select_one('div[data-sp-rte]')
        if div is None:
            print(" * Container not found")
            return

        old_hash = div.attrs.get('data-checksum')
        new_hash = hashlib.sha256(html.encode('utf-8')).hexdigest()

        div.clear()
        div.append(BeautifulSoup(html, 'html.parser'))
        div.attrs['data-checksum'] = new_hash

        if not force and old_hash == new_hash:
            print(" * No changes detected")
            return

        content_data = str(soup)

        data['CanvasContent1'] = content_data
        data = {k: v for k, v in data.items() if v is not None}

        response = self.api.update_page(page_name, e_tag, data)
        print(f" * Uploaded {page_name}: {response.status_code}")
        if not response.ok:
            print(response.text)

        response = self.api.publish(page_name)
        print(f" * Published {page_name}: {response.status_code}")
        if not response.ok:
            print(response.text)

    def upload_file(self, file, front_matter, html):
        self.create_page(file.stem, front_matter, html)
