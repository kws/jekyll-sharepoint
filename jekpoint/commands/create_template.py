from jekpoint.api import SharePointApi


def add_arguments(parser):
    parser.add_argument('--templates-folder', type=str,
                        help='The templates folder, default _templates',
                        default="_templates")


def run(args, config):
    print("Attempting to create", args.templates_folder)
    api = SharePointApi(config.client,
                        f"{config.site_url}{config.site_prefix}/",
                        f"{config.site_prefix}/{config.site_pages}/")

    response = api.create_folder(args.templates_folder)
    print(response.text)
