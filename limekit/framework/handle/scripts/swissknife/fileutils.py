from limekit.framework.core.engine.app_engine import EnginePart
import json

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


class FileUtils(EnginePart):
    name = "__fileutils"

    @classmethod
    def read_file(cls, path, encoding: str = "utf-8"):
        """
        Read the content of the file at the given path using the specified encoding.
        """
        content = ""
        with open(path, encoding=encoding) as file:
            content = file.read()

        return content

    @classmethod
    def read_file_json(cls, path):
        """
        Read and decode a json encoded file at the given path.
        """
        content = cls.read_file(path)
        data = json.loads(content)
        return data
