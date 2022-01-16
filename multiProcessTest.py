#!/usr/bin/python3 -u

import multiprocessing as mp
import time


class testProcess(mp.Process):
    def __init__(self, pId):
        mp.Process.__init__(self)
        self.pId = pId

    def run(self):
        print("Process %d started" % self.pId)
        while not exitFlag.value:
            qLock.acquire()
            print("Process jobQueue", self.pId, id(jobQueue))
            if not jobQueue.empty():
                (job, d) = jobQueue.get()
                qLock.release()
                print("Process %d get job" % self.pId,)
                for j in job:
                    print(j)
                    j.set_data("Process %d" % self.pId)
            else:
                print("Process %d idle" % (self.pId))
                qLock.release()
                time.sleep(1)
        print("Process %d end" % self.pId)

class testClass():
    def __init__(self, name):
        self.name = name
        self.data = "xxxx"

    def set_data(self, data):
        self.data = data

    def get_data(self):
        return self.data

class testSubClass(testClass):
    def __init__(self, name):
        testClass.__init__(self, name)
        self.data = "yyyy"


if __name__ == "__main__":

    processes = []
    exitFlag = mp.Value('i', 0)
    qLock = mp.Lock()
    jobQueue = mp.Queue()
    print("main jobQueue", id(jobQueue))
    for i in range(1):
        ps = testProcess(i)
        ps.start()
        processes.append(ps)

    tObjs = []
    for i in range(0, 20):
        tObj = testSubClass("tObj" + str(i))
        tObjs.append(tObj)

    qLock.acquire()
    for i in range(1):
        jobQueue.put((tObjs, i))
    qLock.release()

    # It is not reliable for Qeueu.empty() to sync process/thread
    # Sleep for a while for safty here
    time.sleep(1)
    while not jobQueue.empty():
        print("JobQueue not empty")
        time.sleep(1)
        pass

    exitFlag.value = 1

    for ps in processes:
        ps.join()

    for tObj in tObjs:
        print("main data", tObj.get_data())

