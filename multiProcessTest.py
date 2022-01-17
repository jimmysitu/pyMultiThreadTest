#!/usr/bin/python3 -u

import multiprocessing as mp
from multiprocessing.managers import BaseManager
import time


class testProcess(mp.Process):
    def __init__(self, pId):
        mp.Process.__init__(self)
        self.pId = pId

    def run(self):
        print("Process %d started" % self.pId)
        #while not (exitFlag.value and jobSentEvent.is_set()):
        while not (exitFlag.value):
            qLock.acquire()
            if not jobQueue.empty():
                (job, d) = jobQueue.get()
                qLock.release()
                print("Process %d get job" % self.pId,)
                rtn = testSubClass("rObj" + str(d))
                rtn.set_data("%s, Process %d" % (rtn.get_data(), self.pId))
                job.set_data("%s, Process %d" % (job.get_data(), self.pId))
                # Assume process takes some time
                #time.sleep(0.1)
                rtnQueue.put(rtn)
            else:
                print("Process %d idle" % (self.pId))
                qLock.release()
                time.sleep(1)
        print("Process %d end" % self.pId)

class testClass():
    def __init__(self, name):
        self.name = name
        self.data = "base"

    def get_name(self):
        return self.name

    def set_data(self, data):
        self.data = data

    def get_data(self):
        return self.data

class testSubClass(testClass):
    def __init__(self, name):
        testClass.__init__(self, name)
        self.data = "sub"

class testShareClass(testClass):
    def __init__(self, name):
        testClass.__init__(self, name)
        self.data = "share"

if __name__ == "__main__":

    exitFlag = mp.Value('i', 0)
    jobSentEvent = mp.Event()
    qLock = mp.Lock()
    jobQueue = mp.Queue()
    rtnQueue = mp.Queue()

    processes = []
    for i in range(0):
        ps = testProcess(i)
        ps.start()
        processes.append(ps)

    BaseManager.register('testShareClass', testShareClass)
    mgr = BaseManager()
    mgr.start()

    # In fact, mp.Queue is thread/process safe
    qLock.acquire()
    tObjs = []
    for i in range(0, 1000):
        tObj = mgr.testShareClass("tObj" + str(i))
        tObjs.append(tObj)
        jobQueue.put((tObj, i))
    qLock.release()
    print("All jobs are sent")
    #jobSentEvent.set()

    # It is not reliable for Qeueu.empty() to sync process/thread
    # Sleep for a while for safty here
    time.sleep(1)
#    while not jobQueue.empty():
#        print("JobQueue not empty")
#        time.sleep(1)

#    while not rtnQueue.empty():
#        rtn = rtnQueue.get()
#        print("main:", rtn.get_name(), rtn.get_data())

    exitFlag.value = 1
    rtnQueue.close()

    for ps in processes:
        ps.join()
    print("All processes exit")


    for tObj in tObjs:
        print("main:", tObj.get_name(), tObj.get_data())

