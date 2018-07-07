#-*- coding:utf-8 -*-  
import threading
import time

def run1():
    print('current thead1:', threading.current_thread().name)
    time.sleep(100)

def run2():
    print('current thead2:', threading.current_thread().name)
    time.sleep(100)

def run3():
    print('current thead3:', threading.current_thread().name)
    time.sleep(1)
    xxx


if __name__ == '__main__':

    t1 = threading.Thread(target=run1)
    t2 = threading.Thread(target=run2)
    t3 = threading.Thread(target=run3)

    t1.start()
    t2.start()
    t3.start()
