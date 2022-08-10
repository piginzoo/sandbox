from module1 import global_test 
class A:
	Test = "11111"

	def test(self):
		#print(Test)
		print(self.Test)
		self.abc = "bbbbbb"

		global gv
		gv = "xxxxxxxx"

	def __init__(self):
		self.abc = "aaaaaaaaa"

a = A()
print(a.abc)
a.test()
print(a.abc)

print(hash(a))
print(A())
print(A())
print(A())

class B:
	p1 = "p1"
	p2 = 2

class C(B):
	pass

b = B()
print("b.p1=",b.p1)
print("b.p2=",b.p2)

c = C()
print("c.p1=",c.p1)
print("c.p2=",c.p2)


# python test_class.py