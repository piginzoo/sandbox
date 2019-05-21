import test1

var1 = None

test1.test_global()

test1.print_global()

import test_global2

def set_config(conf):
    global config
    config = conf


def print_config():    
	global config
	print(config)
