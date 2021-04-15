import json

from jekpoint.api import SharePointApi


def add_arguments(parser):
    parser.add_argument('--list-name', '-l', type=str,
                        help='Which list to dump',
                        default="Site Assets")


def dump_result(filename, result):
    with open(filename, 'wt') as file:
        json.dump(result, file, indent=4, sort_keys=True)


def run(args, config):
    api = SharePointApi(config.client,
                        f"{config.site_url}{config.site_prefix}/",
                        f"{config.site_prefix}")

    list_name = args.list_name

    result = api.get_list_items(list_name)
    dump_result('examples/list_items.json', result.value)

    result = api.get_list(list_name, property='files')
    dump_result('examples/list_files.json', result.value)

    result = api.get_list_items_filenames(list_name)
    dump_result('examples/list_items_filenames.json', result.value)

    result = api.get_list_stream(list_name)
    dump_result('examples/list_as_stream.json', result.value)

    result = api.get_list_stream_all(list_name)
    dump_result('examples/list_as_stream_all.json', result)
