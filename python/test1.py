def test_global():
	global test_global
	test_global="test_global"

def print_global():
	print test_global

def test123():
	a = {}
	a['123']='123'
	return a

a = "N"

def test():
	global a
	if a is None: print "i ma none"
	a = "aaaaa"


def test2():
	print a

if __name__ == '__main__':
	test()
	test2()

	print test123()
	test_global()
	print test_global
