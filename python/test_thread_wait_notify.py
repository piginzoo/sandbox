# -*- coding: utf-8 -*-
import time
import threading


def startup(cond):
    cond.acquire()
    print "准备睡觉1秒"
    time.sleep(3)
    cond.notify()
    cond.release()
    print "睡醒了，通知你"


cond = threading.Condition()

cond.acquire()

t = threading.Thread(target=startup, name='qq-bot', args=(cond,))
t.start()

print "启动了线程，准备等待"
cond.wait()
print "wait活动结束，完事"
