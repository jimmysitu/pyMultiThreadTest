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
                job = jobQueue.get()
                qLock.release()
                print("Process %d get job: %d" % (self.pId, job))
            else:
                print("Process %d idle" % (self.pId))
                qLock.release()
                time.sleep(1)
        print("Process %d end" % self.pId)


if __name__ == "__main__":

    processes = []
    exitFlag = mp.Value('i', 0)
    qLock = mp.Lock()
    jobQueue = mp.Queue()
    print("main jobQueue", id(jobQueue))
    for i in range(3):
        ps = testProcess(i)
        ps.start()
        processes.append(ps)

    qLock.acquire()
    for j in range(0, 1000):
        jobQueue.put(j+10000)
    qLock.release()

    while not jobQueue.empty():
        print("JobQueue not empty")
        time.sleep(1)
        pass

    exitFlag.value = 1

    for ps in processes:
        ps.join()



