def ttt(func):
	def decorator(func):
		def wrapper(*args , **kw):
			print ">>>>>>>>>>>"
			print func.__name__
			print "<<<<<<<<<<<"
			return func(*args, **kw)

		print "in ttt body"
		return wrapper
	print "in decorator..."
	return decorator
		
s = "sssssssssss"

@ttt(s)
def test(bbb,ccc):
	print "test:",bbb,ccc



test('1234','abc')


'''
@ttt
def test(arg):
    pass

ttt(test(arg))
'''