
class TestClass():

	def __init__(self):
		TestClass.__inst = self


TestClass()

print(TestClass.__inst)