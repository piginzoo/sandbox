import time,random,os
from multiprocessing import Process,Queue 
 
def producer(queue):
	for i in range(3):
	    s = "消息" + str(random.random())
	    queue.put({"pid":os.getpid(),"":s})
	    t = random.randint(1,3)
	    time.sleep(t)
	    print("[%d]生产一个消息:%s" % (os.getpid(),s))
 
def consumer(queue):
    while(True):
        data = queue.get()
        print("[%d]消费一个消息" % os.getpid())
        print("消息：%r" % data)
     
if __name__ == "__main__":
    #queue = queue.Queue()
    queue = Queue()

    producers = []
    for i in range(3):
        producers.append(Process(target=producer,args=(queue,)))

    consumer = Process(target=consumer,args=(queue,))

    for i in range(3):
        producers[i].start()
    consumer.start()

    for i in range(3):
        producers[i].join()
    consumer.join()
