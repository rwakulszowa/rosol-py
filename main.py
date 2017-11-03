import node
import path


A = node.Simple("A", node.Nil)
B = node.Simple("B", A)
C = node.Simple("C", node.Nil)
B_C = node.Or([B, C])
D = node.Simple("D", B_C)
AiD = node.And([A, D])
Root = node.Simple("Root", AiD)

print(Root.dumps())

paths = Root.paths(path.Path.empty())

for p in paths:
    print(p)

