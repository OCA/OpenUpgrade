#!/usr/bin/python
import threading
import sys
sys.path.append('..')

import etl

fileconnector_partner=etl.connector.localfile('input/partner.csv')

fileconnector_partner1=etl.connector.localfile('input/partner1.csv')
fileconnector_partner3=etl.connector.localfile('input/partner3.csv')
fileconnector_output=etl.connector.localfile('output/test1_partner.csv','r+')

csv_in1= etl.component.input.csv_in(fileconnector_partner,name='Partner Data')
csv_in2= etl.component.input.csv_in(fileconnector_partner1,name='Partner Data1')
csv_out1= etl.component.output.csv_out(fileconnector_output,name='Partner OUT Data1')
sort1=etl.component.transform.sort('name')
log1=etl.component.transform.logger(name='Read Partner File')
log2=etl.component.transform.logger(name='After Sort')
sleep1=etl.component.control.sleep()

tran=etl.transition(csv_in1,sort1)
tran1=etl.transition(csv_in2,sort1)
tran4=etl.transition(sort1,sleep1)
tran4=etl.transition(sleep1,log2)
#tran6=etl.etl.transition(sleep1,log1,channel_source="statistics")
tran5=etl.transition(sort1,csv_out1)


job1=etl.job([csv_in1,csv_in2,csv_out1,sort1,log1,log2,sleep1], name="vvvvvvvv")



import pickle
class etl_server(threading.Thread):
    path = 'pickle.txt'
    job = False

    # Todo:
    #    1. make data on pickle object with rowcount
    #    2. use row_count/row_index in pickle for restarting ...
    #    3. check server done same concept for stoping...
    #    4. pause and restart function on job should be modify
    #    5. currenlty get error on pause the job: job does not have _connect varible...
    #    6. there should be some unique name or id for all job so that we can get same job when we restart it (currenltly we make name as unique of job)
    #    7. test pickling and unpickling process with get and set state method of class
    #    8. multi threading should be use..
    #    9. other changes on components...

    def write(self):
        """
        Store job instance into pickle object.
        """
        fp = open(self.path,'wb')
        pck_obj = pickle.dump(self.job,fp)
        fp.close()
        return True

    def read(self):
        """
        Read job instance value from pickle object.
        Parameter
        value - pickle value
        """
        value = False
        try:
            fp = open(self.path,'a+')
            value = pickle.load(fp)
        except Exception,e:
            print e
        return value

    def run(self):
        try:
            obj = self.read()
            if obj:
                if self.job.job_id == obj.job_id:
                    if obj.status == 'end':
                        #self.job.run() # should be chk.. if in picke if our job is ended once..and try to run that same job with exception then it should be run...
                        #self.write()
                        pass
                    elif obj.status == 'pause':
                        self.job = obj
                        self.job.run() # or run
                        self.write()
                    else:
                        pass
                else:
                    self.job.run()
                    self.write()
            else:
                self.job.run()
                self.write()
        except Exception,e:
            self.job.pause()
            self.write()

server = etl_server()
server.job = job1
server.start()