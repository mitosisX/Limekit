# from limekit.framework.handle.scripts.swissknife.fileutils import FileUtils
from limekit.framework.handle.paths.path import Path
from limekit.framework.core.exceptions.routes import RouteException

"""
dir = "D:/sandbox/"

route_structure = {
        "project": {
            "name": "Simple",
            "author": "Limekit",
            "description": "Brief project description",
            "copyright": "© 2023 limekit. All Rights Reserved",
            "version": "2.0.1",
            "email": "limekit@lua.gui",
            "url": "",
            "routes": {
                "single": {"book": "book.txt", "names": "names.txt"},
                "group": {
                    "books": {
                        "group_label": "",
                        "Harry Potter": "Harry Potter.txt",
                        "Rings": "Lord of the rings.txt",
                        "Tom Clancy": "Tom Clancy.txt",
                    },
                    "cities": {
                        "Zomba": "zomba.txt",
                        "Blantyre": "Blantyre.txt",
                        "Mzuzu": "Mzuzu.txt",
                        "Lilongwe": "Lilongwe.txt",
                    },
                },
            },
        }
    }
"""


# 16 September, 2023 (9:41 AM) (Saturday)
class Routing:
    """
                The shortest routing system

    ###### Mechanics proposition (16 September, 2023) (1:47 PM) ######
        No code implemetation yet

                Moza (single routing)

    - In individual routing, user can use labels in each route:

                Example

        "routes":{
            "single":{
                "book": "misc::book.txt"
            }
        }


                Vose (group routing)

    - In "group" routing, user can add "group_label" key to the "group", this in turn overides the usage of
    marking (::) during fetching

    - The engine will in turn use the marker to determine where to fetch the resource
    # This technique is reffered to as: Excempt Indidual Marking (EIM)

                Example

            Without EIM

        "routes":{
            "group":{
                "book": {
                    "book1"::"misc:book1.txt",
                    "book2"::"script:book2.lua",
                    "book3"::"images:book3.png",
                    ...
                }
            }
        }


                TODO:




    """

    project_json = {}
    project_json_ = {
        "project": {
            "name": "Simple",
            "author": "Limekit",
            "description": "Brief project description",
            "copyright": "© 2023 limekit. All Rights Reserved",
            "version": "2.0.1",
            "email": "limekit@lua.gui",
            "url": "",
            "routes": {
                "single": {
                    "book": "misc::book.txt",
                    "alarm": "misc::Alarm03.wav",
                    "app_icon": "images::lua.pg",
                },
                "group": {
                    "books": {
                        "group_label": "misc",
                        "Harry Potter": "misc::hey/Harry Potter.txt",
                        "Rings": "script::Lord of the rings.txt",
                        "Tom Clancy": "misc::Tom Clancy.txt",
                    },
                    "cities": {
                        "Zomba": "script::zomba.txt",
                        "Blantyre": "misc::Blantyre.txt",
                        "Mzuzu": "images::Mzuzu.txt",
                        "Lilongwe": "misc::Lilongwe.txt",
                    },
                },
            },
        }
    }

    def set_project_json(self, project_json):
        self.project_json = project_json

    def check_routes_available(self):
        # Check whether user has added routes in their project file
        return bool(self.project_json["project"].get("routes"))

    def reader(self, path):
        # only good for testing
        try:
            dir = "D:/sandbox/"
            with open(dir + path) as file:
                return file.read()
        except Exception as ex:
            print("File does not exist")

    def route_processor(self, route):
        # Adopts django's routing system of using : after app_name usage
        if "::" in route:
            route_key, route_resource = route.split("::")

            route_pointer = self.project_json["project"]["routes"]["group"].get(
                route_key
            )

            if route_pointer:
                get_route_resource = route_pointer.get(route_resource)

                if get_route_resource:
                    print("here")
                    return self.route_marker_mapping(get_route_resource)
                else:
                    raise RouteException(
                        f"Route Error: Route resource '{route_resource}' not Found"
                    )
        else:
            route_pointer = self.project_json["project"]["routes"]["single"].get(route)

            if route_pointer:
                return self.route_marker_mapping(route_pointer)

            else:
                raise RouteException("Route Error: Route resource not Found")

    # Takes the images:lua.png as var: route
    def route_marker_mapping(self, route):
        group_label = ""

        if "::" not in route:
            raise RouteException(
                f'Routing Error: "{route}" does not appear to have a marker. Try "marker:{route}"'
            )
            # print("Add key for ", route)
        else:
            marker, resource = route.split("::")  # ["images", "lua.png"]

            return Path.resource_path_resolver(
                marker, resource
            )  # here to map the marker to the resource

    def marker_redirection(self, marker, resource):
        allowed_paths = ["misc", "images", "scripts"]

        if marker in allowed_paths:
            joined_resource_path = Path.join_paths(
                Path.current_project_dir(), marker, resource
            )
            return joined_resource_path
        else:
            print("Marker not available")

    def fetch_resource(self, route):
        if self.check_routes_available():
            final_resource_path = self.route_processor(route)

            return final_resource_path
            # print(self.reader(res))
        else:
            raise RouteException(
                "Route Error: No routes added to app.json. Add routes first"
            )


# Routing().fetch_resource("books:Harry Potter")
# print(reader(paths["routes"]["group"]["books"]["Rings"]))
