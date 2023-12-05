import os
import json
import shutil
import zipfile
from typing import Iterable

from limekit.framework.handle.system.file import File
from limekit.framework.core.engine.parts import EnginePart
from limekit.framework.handle.scripts.swissknife.converters import Converter

# python-fsutil

__all__ = [
    "clean_dir",
    "convert_size_bytes_to_string",
    "convert_size_string_to_bytes",
    "copy_dir",
    "copy_dir_content",
    "copy_file",
    "create_dir",
    "create_file",
    "create_zip_file",
    "delete_dir",
    "delete_dir_content",
    "delete_dirs",
    "delete_file",
    "delete_files",
    "download_file",
    "exists",
    "extract_zip_file",
    "get_dir_creation_date",
    "get_dir_creation_date_formatted",
    "get_dir_last_modified_date",
    "get_dir_last_modified_date_formatted",
    "get_dir_size",
    "get_dir_size_formatted",
    "get_file_basename",
    "get_file_creation_date",
    "get_file_creation_date_formatted",
    "get_file_extension",
    "get_file_hash",
    "get_file_last_modified_date",
    "get_file_last_modified_date_formatted",
    "get_file_size",
    "get_file_size_formatted",
    "get_filename",
    "get_parent_dir",
    "get_unique_name",
    "is_dir",
    "is_empty",
    "is_empty_dir",
    "is_empty_file",
    "is_file",
    "join_filename",
    "join_filepath",
    "join_path",
    "list_dirs",
    "list_files",
    "make_dirs",
    "make_dirs_for_file",
    "move_dir",
    "move_file",
    "read_file",
    "read_file_from_url",
    "read_file_json",
    "read_file_lines",
    "read_file_lines_count",
    "remove_dir",
    "remove_dir_content",
    "remove_dirs",
    "remove_file",
    "remove_files",
    "rename_dir",
    "rename_file",
    "rename_file_basename",
    "rename_file_extension",
    "replace_dir",
    "replace_file",
    "search_dirs",
    "search_files",
    "split_filename",
    "split_filepath",
    "split_path",
    "write_file",
    "write_file_json",
]

"""
            DONE

read_file
read_file_json
is_empty
is_empty_dir
is_empty_file
get_file_size
is_dir


"""


class FileUtils(EnginePart):
    name = "__fileutils"

    @classmethod
    def read_file(cls, path):
        """
        Read the content of the file at the given path using the specified encoding.
        """
        with open(path) as file:
            return file.read()

    @classmethod
    def read_file_json(cls, path):
        """
        Read and decode a json encoded file at the given path.
        """
        content = cls.read_file(path)
        data = json.loads(content)
        return Converter.table_from(data)

    @classmethod
    def write_file_json(cls, path, data):
        """
        Write a json file at the given path with the specified data encoded in json format.
        """
        print(Converter.table_to_dict(data))
        # content = json.dumps(dict(Converter.table_from(data)), indent=4)
        # File.write_file(path, content)

    @classmethod
    def is_dir(cls, path) -> bool:
        """
        Determine whether the specified path represents an existing directory.
        """
        return os.path.isdir(path)

    @classmethod
    def is_empty(cls, path) -> bool:
        """
        Determine whether the specified path represents an empty directory or an empty file.
        """
        if cls.is_dir(path):
            return cls.is_empty_dir(path)
        return cls.is_empty_file(path)

    @classmethod
    def is_empty_dir(cls, path) -> bool:
        """
        Determine whether the specified path represents an empty directory.
        """
        if not cls.exists(path):
            return None
        return len(os.listdir(path)) == 0

    @classmethod
    def is_empty_file(cls, path) -> bool:
        """
        Determine whether the specified path represents an empty file.
        """
        if not cls.exists(path):
            return None
        return cls.get_file_size(path) == 0

    @classmethod
    def get_file_size(cls, path) -> int:
        """
        Get the directory size in bytes.
        """
        if not cls.exists(path):
            return None
        size = os.path.getsize(path)
        return size

    @staticmethod
    def exists(path):
        """
        Check if a directory of a file exists at the given path.
        """
        return os.path.exists(path)

    @classmethod
    def make_dirs(cls, path):
        """
        Create the directories needed to ensure that the given path exists.
        If a file already exists at the given path an OSError is raised.
        """
        if cls.is_dir(path):
            return None

        os.makedirs(path, exist_ok=True)

    @classmethod
    def is_file(cls, path) -> bool:
        """
        Determine whether the specified path represents an existing file.
        """
        return os.path.isfile(path)

    @classmethod
    def extract_zip_file(
        cls,
        path,
        dest,
        # autodelete: bool = False,
        content_paths: Iterable[str | zipfile.ZipInfo] | None = None,
    ):
        """
        Extract zip file at path to dest path.
        If autodelete, the archive will be deleted after extraction.
        If content_paths list is defined,
        only listed items will be extracted, otherwise all.
        """
        cls.make_dirs(dest)
        try:
            with zipfile.ZipFile(path, "r") as file:
                file.extractall(dest, members=content_paths)
                return True

        except FileNotFoundError:
            return None

        # if autodelete:
        #     remove_file(path)

    @classmethod
    def read_file_lines_count(cls, path) -> int:
        """
        Read file lines count.
        """
        lines_count = 0
        with open(path, "rb") as file:
            file.seek(0)
            lines_count = sum(1 for line in file)

        return lines_count

    @staticmethod
    def copy_file(source, destination):
        try:
            shutil.copyfile(source, destination)
        except FileExistsError as ex:
            print(ex)

    @staticmethod
    def get_filename_ext(path):
        file_name = os.path.basename(path)
        name, ext = os.path.splitext(file_name)

        return Converter.table_from([name, ext])

    @classmethod
    def rename_dir(cls, dir, dir_new):
        cls.renamer(dir, dir_new)

    @classmethod
    def rename_file(cls, file, file_new):
        cls.renamer(file, file_new)

    @classmethod
    def renamer(cls, new, old):
        """
        Rename a directory with the given name.
        If a directory or a file with the given name already exists, an OSError is raised.
        """
        try:
            os.rename(new, old)
            return True
        except OSError as ex:
            print(ex)
            return False
