#!/usr/bin/python
import threading
import sys
sys.path.append('..')

import etl

fileconnector_partner=etl.connector.localfile('input/partner.csv')

fileconnector_partner1=etl.connector.localfile('input/partner1.csv')
fileconnector_partner3=etl.connector.localfile('input/partner3.csv')
fileconnector_output=etl.connector.localfile('output/test1_partner55.csv','r+')

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


job1=etl.job([csv_in1,csv_in2,csv_out1,sort1,log1,log2,sleep1])



import pickle
class etl_server(threading.Thread):   
    path = 'pickle.txt'
    job = False

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
            print "<<<<<<<<<<<",e
        return value

        
    def run(self):      
        try:          
            obj = self.read() 
            print obj                                
            if obj:
                self.job = obj
            else:
                self.job.run()
        except Exception,e:
            print ">>>>>>>>",e            
            self.write()
        
    
    


server = etl_server()
server.job = job1
server.start()



       

