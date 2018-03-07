def test(a,b,c):
	print a,b,c

def test2(a,b,c):
	test(a=c,b=b,c=a)

test(a="a",b="b",c="c")
test("a","b","c")

test2("a","b","c")
