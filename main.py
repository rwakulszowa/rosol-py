import json

from rosol import package
from rosol.cache import instance as CACHE


repo = package.Repository([
    package.SimpleVersionedPackage("A", 1, []),
    package.SimpleVersionedPackage("A", 2, []),
    package.SimpleVersionedPackage("A", 3, [package.Set("X", [1])]),  # X1 -> non-existent package
    package.SimpleVersionedPackage("B", 1, [package.Set("A", [1])]),
    package.SimpleVersionedPackage("B", 2, []),
    package.SimpleVersionedPackage("C", 1, [package.Set("D", [1, 2, 3])]),  # C1 <-> D1 circular dependency
    package.SimpleVersionedPackage("D", 1, [
        package.Set("A", [1, 2]),
        package.Set("C", [1])]),
    package.SimpleVersionedPackage("D", 2, [
        package.Set("A", [1, 2, 3])]),
    package.SimpleVersionedPackage("Root", 1, [package.Set("D", [1, 2])])])
    
Root = repo.get("Root", 1)

node = Root.into_node(repo)

for path in node.resolve().paths:
    print(path)

print(CACHE)
print(CACHE.info())
