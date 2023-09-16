from limekit.framework.handle.scripts.swissknife.fileutils import FileUtils

"""
dir = "D:/sandbox/"

route_structure = {
    "routes": {
        "book": dir + "book.txt",
        "names": dir + "names.txt",
        "book": dir + "book.txt",
        "group": {
            "books": {
                "Harry Potter": dir + "Harry Potter.txt",
                "Rings": dir + "Lord of the rings.txt",
                "Tom Clancy": dir + "Tom Clancy.txt",
            },
            "cities": {
                "Zomba": dir + "zomba.txt",
                "Blantyre": dir + "Blantyre.txt",
                "Mzuzu": dir + "Mzuzu.txt",
                "Lilongwe": dir + "Lilongwe.txt",
            },
        },
    }
}
"""


# 16 September, 2023 (9:41 AM) (Saturday)
class Routing:
    pathss = {}
    dir = "D:/sandbox/"
    paths = {
        "routes": {
            "book": dir + "book.txt",
            "names": dir + "names.txt",
            "book": dir + "book.txt",
            "group": {
                "books": {
                    "Harry Potter": dir + "Harry Potter.txt",
                    "Rings": dir + "Lord of the rings.txt",
                    "Tom Clancy": dir + "Tom Clancy.txt",
                },
                "cities": {
                    "Zomba": dir + "zomba.txt",
                    "Blantyre": dir + "Blantyre.txt",
                    "Mzuzu": dir + "Mzuzu.txt",
                    "Lilongwe": dir + "Lilongwe.txt",
                },
            },
        }
    }
    routes = {}

    def __init__(self, file):
        project_json = FileUtils.read_file_json(file)

    def get_project_json(self, file):
        pass

    def check_routes_available(self):
        return bool(self.paths.get("routes"))

    def reader(self, path):
        try:
            with open(path) as file:
                return file.read()
        except Exception as ex:
            print("File does not exist")

    def processor(self, route):
        # Adopts django's routing system of using : after app_name usage
        if ":" in route:
            route_key, route_resource = route.split(":")

            route_pointer = self.paths["routes"]["group"].get(route_key)

            if route_pointer:
                get_route_resource = route_pointer.get(route_resource)

                return get_route_resource or ""
        else:
            route_pointer = self.paths["routes"].get(route)
            return route_pointer or ""

    def get(self, route):
        if self.check_routes_available():
            res = self.processor(route)
            print(self.reader(res))
        else:
            print("Add routes first")


Routing().get("books:Harry Potter")
# print(reader(paths["routes"]["group"]["books"]["Rings"]))
