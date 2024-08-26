import os
import shutil

from pathlib import Path

from state.graph.types import ValueType, read, write
from exceptions import NotExistError
from utils import CachedClass


class GraphDatabase(metaclass=CachedClass):
    path = f"{Path(__file__).parent}/.database"

    def __init__(self) -> None:
        if not os.path.isdir(self.path):
            os.mkdir(self.path)

    @staticmethod
    def _check_path(*path: str) -> None:
        for node in path:
            if "." in node or "/" in node:
                raise ValueError(f"{node} is not a valid node name")

    def write_node(self, *path_to_node: str, value: ValueType | None = None) -> None:
        GraphDatabase._check_path(*path_to_node)
        path_to_parent = "/".join(path_to_node[0:-1])
        full_path_to_node = self.path + "/" + "/".join(path_to_node)
        if not os.path.isdir(f"{self.path}/{path_to_parent}"):
            raise NotExistError("parant node", path_to_parent)
        if not os.path.isdir(full_path_to_node):
            os.mkdir(full_path_to_node)
        if value != None and len(path_to_node) > 0:
            with open(f"{full_path_to_node}/.value", mode="wb") as file:
                file.write(write(value))

    def read_node(self, *path_to_node: str) -> ValueType | None:
        GraphDatabase._check_path(*path_to_node)
        full_path_to_node = self.path + "/" + "/".join(path_to_node)
        path_to_value = full_path_to_node + "/.value"
        if not os.path.isdir(full_path_to_node):
            raise NotExistError("node", "/".join(path_to_node))
        if os.path.isfile(path_to_value):
            with open(path_to_value, mode="rb") as file:
                return read(file.read())

    def get_tree(self, *path_to_root: str) -> dict[str, dict]:
        GraphDatabase._check_path(*path_to_root)
        full_path_to_root = self.path + "/" + "/".join(path_to_root)
        nodes = [
            file
            for file in os.listdir(full_path_to_root)
            if os.path.isdir(f"{full_path_to_root}/{file}")
        ]
        return {node: self.get_tree(*path_to_root, node) for node in nodes}

    def delete_node(self, *path_to_node: str) -> None:
        GraphDatabase._check_path(*path_to_node)
        full_path_to_node = self.path + "/" + "/".join(path_to_node)
        if len(path_to_node) > 0 and os.path.isdir(full_path_to_node):
            shutil.rmtree(full_path_to_node)
