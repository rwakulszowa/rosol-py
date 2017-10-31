import node
import path


A = node.Simple("A", node.Nil)
B = node.Simple("B", A)
C = node.Simple("C", node.Nil)
B_C = node.Or([B, C])
Root = node.Simple("Root", B_C)

print(Root.dumps())

paths = Root.paths(path.Path.empty())

for p in paths:
    print(p)
