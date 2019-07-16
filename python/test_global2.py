import test1

test1.print_global()

def test():
	print 

if __name__ == "__main__":
	import test_global
	test_global.set_config("xxxxxx")
	test_global.print_config()