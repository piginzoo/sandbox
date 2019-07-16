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