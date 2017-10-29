import node


A = node.Simple("A", node.Nil)
B = node.Simple("B", node.Nil)
C = node.Simple("C", node.Nil)
E = node.Simple("E", A)
EC = node.Or([E, C])
AB = node.And([A, B])
AB_C = node.Or([AB, C])
D = node.And([AB_C, B, A])
Root = node.Simple("Root", D)

print(Root.dumps())

paths = Root.paths([(".", )])
for path in paths:
    print(path)

resolved = Root.resolve(tuple())
print(set([node.id() for node in resolved]))

