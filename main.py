import json

import package


repo = package.Repository([
    package.VersionedPackage("A", 1, []),
    package.VersionedPackage("A", 2, []),
    package.VersionedPackage("B", 1, [package.Set("A", [1])]),
    package.VersionedPackage("B", 2, []),
    package.VersionedPackage("C", 1, [package.Set("D", [1, 2, 3])]),  # C1 <-> D1 circular dependency
    package.VersionedPackage("D", 1, [
        package.Set("A", [1, 2]),
        package.Set("C", [1])]),
    package.VersionedPackage("D", 2, [
        package.Set("A", [1, 2])]),
    package.VersionedPackage("Root", 1, [package.Set("D", [1])])])
    
Root = repo.get("Root", 1)

node = Root.into_node(repo)

for path in node.paths():
    print(path)
