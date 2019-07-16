#-*- coding:utf-8 -*-  
import threading
import time

def run():
    print('current thead:', threading.current_thread().name)
    time.sleep(100)


if __name__ == '__main__':

    start_time = time.time()

    print('Main thread:', threading.current_thread().name)
    thread_list = []
    for i in range(5):
        t = threading.Thread(target=run)
        t.setDaemon(True)
        thread_list.append(t)

    for t in thread_list:
        t.start()

    time.sleep(3)     

    print('Main therad finish!' , threading.current_thread().name)
    print('Total time:', time.time()-start_time)