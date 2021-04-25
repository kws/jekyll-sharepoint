from typing import Callable
import requests


class AuthorisingClient:
    def __init__(self, token_fetcher: Callable):
        self.__token_fetcher = token_fetcher

    def make_request(self, url, method="get", headers=None, use_auth=True, **kwargs):
        if use_auth:
            headers = headers if headers else {}
            headers = {**headers, "Authorization": f'Bearer {self.__token_fetcher()}'}

        return requests.request(method, url, headers=headers, **kwargs)


class SharePointApi:

    def __init__(self, client, site_root, server_root):
        self.__client = client
        self.__site_root = site_root
        self.__server_root = server_root

    def download_page(self, page_name):
        url = f"{self.__site_root}_api/web/getFileByServerRelativeUrl('{self.__server_root}{page_name}')" \
              f"/$value"
        response = self.__client.make_request(
            url=url,
            method="get",
            headers=dict(Accept="application/json;odata=nometadata")
        )
        return response

    def get_page_details(self, page_name):
        url = f"{self.__site_root}_api/web/getFileByServerRelativeUrl('{self.__server_root}{page_name}')" \
              f"/ListItemAllFields"
        response = self.__client.make_request(
            url=url,
            method="get",
            headers=dict(Accept="application/json;odata=nometadata")
        )
        return response

    def create_new_page(self, folder, page_name, template_file_type=1):
        # StandardPage.The value = 0.
        # WikiPage.The value = 1.
        # FormPage.The value = 2.
        url = f"{self.__site_root}_api/web/GetFolderByServerRelativeUrl('{self.__server_root}{folder}')/Files/" \
              f"AddTemplateFile(urlOfFile='{self.__server_root}{page_name}',templateFileType={template_file_type})"
        response = self.__client.make_request(
            url=url,
            method="post",
            headers=dict(Accept="application/json;odata=verbose")
        )
        return response

    def copy_page(self, source_name, page_name, overwrite=False):
        url = f"{self.__site_root}_api/web/getFileByServerRelativeUrl('{self.__server_root}{source_name}')" \
              f"/CopyTo(strnewurl='{self.__server_root}{page_name}', bOverwrite={str(overwrite).lower()})"
        response = self.__client.make_request(
            url=url,
            method="post",
            headers=dict(Accept="application/json;odata=verbose")
        )
        return response

    def create_folder(self, folder_name):
        url = f"{self.__site_root}_api/web/folders"
        response = self.__client.make_request(
            url=url,
            method="post",
            json=dict(ServerRelativeUrl=f"{self.__server_root}{folder_name}"),
            headers=dict(Accept="application/json;odata=verbose")
        )
        return response

    def update_page(self, page_name, e_tag, data):
        url = f"{self.__site_root}_api/web/getFileByServerRelativeUrl('{self.__server_root}{page_name}')" \
              f"/ListItemAllFields"
        response = self.__client.make_request(
            url=url,
            method="post",
            headers={
                'Accept': "application/json;odata=nometadata",
                'X-HTTP-Method': "MERGE",
                'If-Match': e_tag,
            },
            json=data
        )
        return response

    def publish(self, page_name):
        url = f"{self.__site_root}_api/web/getFileByServerRelativeUrl('{self.__server_root}{page_name}')" \
              f"/Publish"
        response = self.__client.make_request(
            url=url,
            method="post",
            data=""
        )
        return response

    def get_list(self, list_name, property='', params=None):
        url = f"{self.__site_root}_api/web/lists/getByTitle('{list_name}')/{property}"
        response = self.__client.make_request(
            url=url,
            params=params,
            method="get",
            headers=dict(Accept="application/json")
        )
        return response

    def get_list_items(self, list_name):
        return self.get_list(list_name, property='items')

    def get_list_items_filenames(self, list_name):
        url = f"{self.__site_root}_api/web/lists/getByTitle('{list_name}')/items?" \
              f"$select=FieldValuesAsText/FSObjType&$select=FieldValuesAsText/FileRef&$expand=FieldValuesAsText"
        response = self.__client.make_request(
            url=url,
            method="get",
            headers=dict(Accept="application/json;odata=nometadata")
        )
        return response

    def get_list_stream(self, list_name, render_options=0, paging=''):
        url = f"{self.__site_root}_api/web/lists/getByTitle('{list_name}')/RenderListDataAsStream{paging}"
        response = self.__client.make_request(
            url=url,
            method="post",
            headers=dict(Accept="application/json;odata=nometadata"),
            json=dict(parameters={
                'RenderOptions': render_options,
            })
        )
        return response

    def get_list_stream_all(self, list_name, render_options=0):
        result = self.get_list_stream(list_name, render_options=render_options).json()
        results = [] + result.get("Row", [])
        while 'NextHref' in result:
            result = self.get_list_stream(list_name, render_options=render_options, paging=result['NextHref']).json()
            results += result.get("Row", [])

        return results

    def upload_file(self, folder, filename, data):
        url = f"{self.__site_root}_api/web/GetFolderByServerRelativeUrl('{self.__server_root}{folder}')" \
              f"/Files/Add(url='{filename}', overwrite=true)"
        response = self.__client.make_request(
            url=url,
            method="post",
            data=data
        )
        return response
