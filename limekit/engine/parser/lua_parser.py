import re


class LuaParser:
    def remove_lua_comments(self, content):
        """Remove all Lua comments from the content."""
        # Remove block comments: --[[ ... ]]
        content = re.sub(r"--\[\[.*?\]\]", "", content, flags=re.DOTALL)
        # Remove line comments: -- ...
        content = re.sub(r"--.*$", "", content, flags=re.MULTILINE)
        return content

    def find_function_definitions(self, content):
        """Find all function definitions in the Lua file."""
        pattern = r"(?:(?:local\s+)?function\s+([A-Za-z_]\w*)\s*\(|([A-Za-z_]\w*)\s*=\s*function\s*\()"
        matches = re.finditer(pattern, content)
        return {
            match.group(1) or match.group(2)
            for match in matches
            if match.group(1) or match.group(2)
        }

    def find_class_instances(self, content, function_defs):
        """Find all PascalCase class instantiations."""
        # Pattern to match class instantiations (both assignment and direct calls)
        pattern = r"""
            (?:^|\s|=|,)                  # Beginning or after space/=/,
            ([A-Z][A-Za-z0-9_]*)          # Class name (must start with capital)
            \s*                           # Optional whitespace
            (?:\((.*?)\)|\{(.*?)\})       # Arguments in () or {}
            """

        matches = re.finditer(pattern, content, re.VERBOSE)

        return [
            match.group(1)
            for match in matches
            if match.group(1) not in function_defs  # Skip if it's a defined function
        ]

    def get_all_classes(self, content):
        content = self.remove_lua_comments(content)

        # First pass: find all function definitions
        function_defs = self.find_function_definitions(content)

        # Find all class instantiations
        class_instances = self.find_class_instances(content, function_defs)

        return set(class_instances)
