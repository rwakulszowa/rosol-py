import json

import node
import package
import path


A = node.Simple("A")
B = node.Simple("B", A)
C = node.Simple("C")
B_C = node.Or([B, C])
D = node.Simple("D", B_C)
AiD = node.And([A, D])
Root = node.Simple("Root", AiD)

print(Root.dumps())

paths = Root.paths(path.Path.empty())

for p in paths:
    print(p)

repo = package.Repository([
    package.VersionedPackage("A", 1, []),
    package.VersionedPackage("A", 2, []),
    package.VersionedPackage("B", 1, []),
    package.VersionedPackage(
        "C",
        1,
        [
            package.Set("A", [1, 2, 3]),
            package.Range("B", 1, 3)])])

print(repo.dumps())

C1 = repo.get("C", 1)

node = C1.into_node(repo)
print(list(node.paths(path.Path.empty())))
