import node
import path


A = node.Simple("A", node.Nil)
B = node.Simple("B", A)
C = node.Simple("C", node.Nil)
B_C = node.Or([B, C])
D = node.Simple("D", B_C)
AiD = node.And([A, D])
E = node.Simple("E", AiD)
EiB_C = node.And([E, B_C])
Root = node.Simple("Root", EiB_C)

print(Root.dumps())

paths = Root.paths(path.Path.empty())

for p in paths:
    print(p)
