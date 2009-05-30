class ETLThread(threading.Thread):
   def __init__(self, jobs):
       threading.Thread.__init__(self)
       self.vlock = threading.Lock()
       self.jobs = jobs
       self.threads = []
       self.data={}
       self.sleeptime=5
       threading.Thread.__init__(self)
       count=0
   def run(self):
        try:
            self.running = True
            while self.running:
#                ct = ETLThread(self.threads)

                print " Now Sleeping after Lock acquired for ",
                time.sleep( self.sleeptime)
                self.jobs.run()
                job1=self.jobs
                time.sleep(self.sleeptime)

        except Exception, e:
            import traceback,sys
            info = reduce(lambda x, y: x+y, traceback.format_exception(sys.exc_type, sys.exc_value, sys.exc_traceback))
            print "error",info
            self.running = False


            return False

   def stop(self):

        self.running = False
        for t in self.threads:
            t.stop()

#
if __name__ == '__main__':
    test=ETLThread(job1)

    test.start()