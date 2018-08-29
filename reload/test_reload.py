from reloadr import autoreload

import threading,time

@autoreload
def test_print():
	print "test_print123"

class SomeThing:
    def do_stuff(self):
        print "123"

s = SomeThing()

def run():
	while True:
		# s.do_stuff()
		test_print()
		time.sleep(1)

t = threading.Thread(target=run, name='wx-bot')
t.start()
