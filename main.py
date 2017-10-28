import node


A = node.Simple("A", node.Nil)
B = node.Simple("B", node.Nil)
C = node.Simple("C", node.Nil)
AB = node.And([A, B])
AB_C = node.Or([AB, C])
Root = node.Simple("Root", AB_C)

print(Root.dumps())
