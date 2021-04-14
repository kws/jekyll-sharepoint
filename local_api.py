from msgraphy.sharepoint_classic import SharePointApi


class LocalApi(SharePointApi):

    def __init__(self, client, site_root, server_root):
        self.__client = client
        self.__site_root = site_root
        self.__server_root = server_root
        super(LocalApi, self).__init__(client, site_root, server_root)

    def get_list(self, list_name, property=''):
        url = f"{self.__site_root}_api/web/lists/getByTitle('{list_name}')/{property}"
        response = self.__client.make_request(
            url=url,
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
        result = self.get_list_stream(list_name).value
        results = [] + result.get("Row", [])
        while 'NextHref' in result:
            result = self.get_list_stream(list_name, paging=result['NextHref']).value
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
