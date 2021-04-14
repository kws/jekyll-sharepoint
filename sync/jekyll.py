from pathlib import Path
from collections import namedtuple

HtmlFile = namedtuple('HtmlFile', ['abs_path', 'rel_path', 'html', 'front_matter'])
ImageFile = namedtuple('ImageFile', ['abs_path', 'rel_path'])


class JekyllSync:

    def __init__(self, root, images="images", html_gen=None):
        self._root = Path(root)
        self._images = self._root / Path(images)
        self._html_gen = html_gen

    def website_files(self):
        file_list = self._root.glob("**/*.html")

        all_files = []
        for filename in file_list:
            relative_filename = filename.relative_to(self._root)
            with open(filename, 'rt') as file:
                html = file.read()

            if self._html_gen:
                html, front_matter = self._html_gen(html)
            else:
                front_matter = dict()
            all_files.append(HtmlFile(abs_path=filename.absolute(), rel_path=relative_filename,
                                      html=html, front_matter=front_matter))
        return all_files

    def website_images(self):
        file_list = self._images.glob("**/*")
        all_files = []
        for filename in file_list:
            if not filename.is_file():
                continue
            relative_filename = filename.relative_to(self._images)
            print(relative_filename)
            all_files.append(ImageFile(abs_path=filename.absolute(), rel_path=relative_filename))

        return all_files

    def get_file_folders(self, files):
        files = [f.rel_path for f in files]
        folders = set()
        for f in files:
            for p in f.parents:
                if not p.is_file() and p.name != "":
                    folders.add(p)

        folders = list(folders)
        folders.sort(key=lambda x: len(str(x)))
        return folders
