def test_args_kwargs(first, *args, **kwargs):
	print first
	print args
	print kwargs

def test_kwargs(first, **kwargs):	
	test_kwargs2(first,**kwargs)

def test_kwargs2(first, **kwargs):	
	print first
	print kwargs


test_args_kwargs(1, 2, 3, 4, k1=5, k2=6)

test_kwargs(1, k1=5, k2=6)


