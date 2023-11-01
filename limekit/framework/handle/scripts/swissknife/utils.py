import lupa
import heapq
from limekit.framework.core.engine.parts import EnginePart
from limekit.framework.handle.scripts.swissknife.converters import Converter


class Utils(EnginePart):
    name = "__utils"

    @staticmethod
    @lupa.unpacks_lua_table
    def weighted_graph(edges, start_node, end_node):
        # edges: {{ 'point 1', 'point 2', value }, ...}
        graph = WeightedGraph()

        for a, b in edges.items():
            node1, node2, distance = b.values()
            graph.add_edge(node1, node2, distance)

        shortest_path, path_cost = graph.dijkstra_algorithm(start_node, end_node)

        return Converter.table_from(shortest_path), path_cost


class WeightedGraph:
    infinity_number = float("inf")

    def __init__(self):
        self.graph = {}  # Initialize an empty graph

    # Method to add an edge to the graph with a specified weight
    def add_edge(self, start, end, weight):
        if start not in self.graph:
            self.graph[
                start
            ] = (
                []
            )  # Initialize an empty list for the start node if it's not already in the graph

        self.graph[start].append(
            (end, weight)
        )  # Add the end node and weight to the start node's list

        if end not in self.graph:
            self.graph[
                end
            ] = (
                []
            )  # Initialize an empty list for the end node if it's not already in the graph

        self.graph[end].append(
            (start, weight)
        )  # Since the graph is undirected, add the reverse edge

    # Dijkstra's algorithm to find the shortest path from the start to the end
    def dijkstra_algorithm(self, start, end):
        priority_queue = [
            (0, start)
        ]  # Initialize a priority queue with the start node and a distance of 0
        shortest_distances = {
            node: self.infinity_number for node in self.graph
        }  # Initialize all distances to infinity
        previous_nodes = (
            {}
        )  # Initialize a dictionary to track the previous node in the shortest path
        shortest_distances[start] = 0  # Set the distance of the start node to 0

        while priority_queue:
            current_distance, current_node = heapq.heappop(
                priority_queue
            )  # Get the node with the shortest distance

            if current_distance > shortest_distances[current_node]:
                continue  # Skip this node if a shorter path has already been found

            for neighbor, weight in self.graph[current_node]:
                distance = current_distance + weight
                if distance < shortest_distances[neighbor]:
                    shortest_distances[
                        neighbor
                    ] = distance  # Update the shortest distance
                    previous_nodes[neighbor] = current_node  # Update the previous node
                    heapq.heappush(
                        priority_queue, (distance, neighbor)
                    )  # Add to the priority queue

        if end not in previous_nodes:
            return (
                None,
                self.infinity_number,
            )  # If there's no path to the end node, return None and infinity

        path = []
        current = end
        while current:
            path.append(current)
            current = previous_nodes.get(
                current
            )  # Reconstruct the path by backtracking

        path.reverse()
        path_cost = shortest_distances[end]

        return path, path_cost
