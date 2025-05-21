from limekit.engine.parts import EnginePart
from PySide6.QtWidgets import QFileDialog


class SaveFile(QFileDialog, EnginePart):
    name = "__saveFileDialog"

    # For filters: {['Image Files' = {'.jpg', '.png', '.jpeg', '.ico'}]}
    def __init__(self, parent):
        super().__init__(parent)

    def setInitDir(self, dir):
        self.setDirectory(dir)

    def display(self, parent, title, start_dir, filters):
        self.process_filters(filters)
        name_, ok = self.getSaveFileName(
            parent,
            title,
            start_dir,
            self.process_filters(filters),
            # "Image Files (*.png *.jpg *.bmp);;Text Files (*.txt *.lua)",
            # options=QFileDialog.Option.DontUseNativeDialog,
        )
        return name_ if name_ else None

    def process_filters(self, filters):
        final_filters = ""

        c = 0
        to_py_dict = dict(filters).items()

        for title, extensions in to_py_dict:
            c += 1
            get_ext_only = [
                "." if not "." in filters[title][x] else "" + filters[title][x]
                for x in extensions
            ]
            filtered_exts = " ".join(["*{}".format(ext) for ext in get_ext_only])
            required_final = (
                f"{title} ({filtered_exts}){';;' if c != len(to_py_dict) else ''}"
            )
            # print(required_final)
            final_filters += required_final
            # if c != len(to_py_dict):
            #     pass
            # else:
            #     print("DOne")

        return final_filters

    # Programmatically, use double ;; to support further filters
    # "Images (*.png  *.jpg);;Vector (*.svg)"
    def setAllowedFileTypes(self, types):
        self.setNameFilters()
