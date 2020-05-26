import file2

test_v = "123"

def test_m1():
	file2.test_m2()

if __name__ == '__main__':
	print("test_v",test_v)
	test_m1()
	print("test_v",test_v)