import threading
import logging
import time

"""
    list_size For문 도는 List최대 사이즈
    func_work( targetIndex ) 함수를 전달받아서 수행함
"""

format = "%(asctime)s: %(message)s"
logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")
                    
def work_Statement_For_Index( threadIndex , func_work, thread_cnt, list_size ):
    logging.info("Thread %s: starting", threadIndex)
    for i in range( 0 , list_size ):
        if i % thread_cnt == threadIndex :
            # time.sleep(2)
            func_work(i)
    logging.info("Thread %s: finishing", threadIndex)

def doMultiThread_For_Index_State( func_work, thread_cnt = 4, list_size=0 ):
    # Create two threads as follows
    threads = []
    for i in range( 0 , thread_cnt ):
        th = threading.Thread(target=work_Statement_For_Index, args=(i,func_work,thread_cnt,list_size))
        threads.append( th )
        th.start()

    for index, thread in enumerate(threads):
        logging.info("Main    : before joining thread %d.", index)
        thread.join()
        logging.info("Main    : thread %d done", index)
    
def work_Statement_While( threadIndex , func_work, func_is_finish ):
    logging.info("Thread %s: starting", threadIndex)
    while func_is_finish(threadIndex) :
        func_work( threadIndex )
    logging.info("Thread %s: finishing", threadIndex)

"""
   func_work( threadIndex )
   func_is_inWhile( threadIndex ) 
"""
def doMultiThread_While_State( func_work, func_is_inWhile, thread_cnt = 4 ):
    # Create two threads as follows
    threads = []
    for i in range( 0 , thread_cnt ):
        th = threading.Thread(target=work_Statement_While, args=(i,func_work,func_is_inWhile))
        threads.append( th )
        th.start()

    for index, thread in enumerate(threads):
        logging.info("Main    : before joining thread %d.", index)
        thread.join()
        logging.info("Main    : thread %d done", index)

def testFunction():
    # Define a function for the thread
    totalLen = 1000000
    list = [ i for i in range(0, totalLen ) ]
    WorkChecker = [ 0 for i in range(0, totalLen ) ]
    def print_time( targetIndex ):
        global list
        WorkChecker[targetIndex] += 1

    doMultiThread_For_Index_State( print_time, 10 , len(list) )

    count =0
    for i in WorkChecker:
        if i == 1 :
            count += 1

    print( "YES"  if totalLen == count else "NO" )