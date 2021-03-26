from treelib import Node, Tree
tree = Tree()
tree.create_node("n1", 1) # root node
tree.create_node("n2", 2, parent=1)
tree.create_node("n21", 21, parent=2)
tree.create_node("n22", 22, parent=2)
tree.create_node("n211", 211, parent=21)
tree.create_node("n221", 221, parent=22)
tree.create_node("n3", 3, parent=1)
tree.show()

childrens = tree.children(2)
for c in childrens:
	ccs = tree.children(c.identifier)
	print(c,"=>",ccs)

print(list(tree.rsearch(221))[::-1])
print(tree.root,type(tree.root))