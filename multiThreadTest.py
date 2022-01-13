#!/usr/bin/python3 -u

import threading
import queue
import time

class testThread(threading.Thread):
    def __init__(self, thId):
        threading.Thread.__init__(self)
        self.thId = thId

    def run(self):
        print("Thread %d started" % self.thId)
        while not exitFlag:
            qLock.acquire()
            if not jobQueue.empty():
                job = jobQueue.get()
                qLock.release()
                print("Thread %d get job: %d" % (self.thId, job))
            else:
                print("Thread %d idle" % (self.thId))
                qLock.release()
                time.sleep(1)
        print("Thread %d end" % self.thId)

if __name__ == "__main__":

    threads = []
    exitFlag = 0
    qLock = threading.Lock()
    jobQueue = queue.Queue()
    for i in range(6):
        thd = testThread(i)
        thd.start()
        threads.append(thd)

    qLock.acquire()
    for j in range(0, 1000):
        jobQueue.put(j+10000)
    qLock.release()

    while not jobQueue.empty():
        pass

    exitFlag = 1

    for thd in threads:
        thd.join()

