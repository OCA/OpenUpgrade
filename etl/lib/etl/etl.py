# -*- encoding: utf-8 -*-
##############################################################################
#
#    ETL system- Extract Transfer Load system
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
""" ETL Process.

    The module provides process of ETL.

"""
import datetime
import logging
import logging.handlers
import sys
import os

LOG_INFO = 'info'
LOG_WARNING = 'warn'
LOG_ERROR = 'error'


def init_logger():
    logger = logging.getLogger()
    # create a format for log messages and dates
    formatter = logging.Formatter('[%(asctime)s] %(levelname)s:%(name)s:%(message)s', '%a %b %d %Y %H:%M:%S')
    # Normal Handler on standard output
    handler = logging.StreamHandler(sys.stdout)
    # tell the handler to use this format
    handler.setFormatter(formatter)
    # add the handler to the root logger
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)   


class Logger(object):
    def notifyChannel(self, name, level, msg):        
        log = logging.getLogger(name)
        level_method = getattr(log, level)        
        msg = unicode(msg)

        result = msg.strip().split('\n')
        if len(result)>1:
            for idx, s in enumerate(result):
                level_method('[%02d]: %s' % (idx+1, s,))
        elif result:
            level_method(result[0])

    def shutdown(self):
        logging.shutdown()


init_logger()



class statistic(object):
    """
    This class computes basic statistics and return them at the end of the process like data in a channel called "statistics":
    Input Channel | # of Records | Time To Process | Time/Record | Memory Usage
    main          | 1244         | 123 sec         | 0.1 sec     | 1Mb
    other         | 144          | 12 sec          | 0.1 sec     | 1Mb
    """
    
    statistics={}
    def statistic(self,source_component,destination_component,source_channel,destination_channel,total_record,stat_time):
        input_channel=(source_component,destination_component,source_channel,destination_channel)
        if input_channel not in self.statistics:
            self.statistics.setdefault(input_channel,{                   
                       'input_channel':input_channel,
                       'total_records':0,
                       'total_time':0,
                       'record_time':0,
                       'memory':0,
                       'start':stat_time
            })
        stat=self.statistics[input_channel]        
        stat['end']=stat_time
        stat['total_time']=stat['end']-stat['start']
        if total_record:      
            stat['total_records']+=total_record
            stat['record_time']=stat['total_time']/stat['total_records']
            stat['memory']+=0 # TODO : Calculate size of data


class signal(object):
    """
    ETL Signal.
    Each component can send signals. Trigger Transitions can listen to these signals.
    Signals are automatically generated:
       - start : When the component starts
       - start_input : At the first row received by the component
       - start_output : At the first row send by the component
       - no_input : At the end of the process, if no data received
       - stop : when the component is set as pause
       - continue : when the component restart after a pause
       - end : When the component finnished is process
       - error : When the component give error
    """
    def __init__(self,*args, **argv):
        self.__connects={}  
    
    def signal(self, signal, signal_data=None):
        for fnct,data,key in self.__connects.get(signal, []):
            fnct(self, signal_data, *data)
        

    def signal_connect(self, key, signal, fnct, *data):
        self.__connects.setdefault(signal, [])
        if (fnct, data, key) not in self.__connects[signal]:
            self.__connects[signal].append((fnct, data, key))
        

    def signal_unconnect(self, key, signal=None):
        if not signal:
            signal = self.__connects.keys()
        else:
            signal = [signal]
        for sig in signal:
            i=0
            while i<len(self.__connects[sig]):
                if self.__connects[sig][i][2]==key:
                    del self.__connects[sig][i]
                else:
                    i+=1
        
    
class transformer(object):
    """
        transfer data into different type.
        pass description like :
          - INTEGER  : convert string to Integer object
          - FLOAT : convert string to float object
          - LONG  : convert string to long integer object
          - COMPLEX : convert string to complex number
          - STRING : convert string to string
          - DATE   : convert string to datetime.date object
          - DATETIME : convert string to datetime.datetime object
          - TIME : convert string to datetime.time object
          - BOOLEAN : convert string to boolean object
        example :
           datas = [{'id':'1','name':'abc','invoice_date':'2009-10-20','invoice_amount':'200.00','is_paid':'1'}]
           description= {'id':etl.transformer.LONG,'name':etl.transformer.STRING,'invoice_date':etl.transformer.DATE,'invoice_amount':etl.transformer.FLOAT,'is_paid':etl.transformer.BOOLEAN}
           return = [{'id':1,'name':'abc','invoice_date': datetime.date object (2009, 10, 20) ,'invoice_amount':200.00,'is_paid':True}]
    """
    INTEGER='int'
    STRING='str'
    DATE='date'
    DATETIME='datetime'
    TIME='time'
    FLOAT='float'
    LONG='long'
    COMPLEX='complex'
    BOOLEAN='bool'

    DATE_FORMAT='%Y-%m-%d'
    TIME_FORMAT='%H:%M:%S'
    DATETIME_FORMAT='%Y-%m-%d %H:%M:%S'

    _transform_method={
        'int':int,
        'str':unicode,
        'date':lambda x:datetime.datetime.strptime(x,transformer.DATE_FORMAT).date(),
        'time':lambda x:datetime.datetime.strptime(x,transformer.TIME_FORMAT).time(),
        'datetime':lambda x:datetime.datetime.strptime(x,transformer.DATETIME_FORMAT),
        'float':float,
        'long':long,
        'complex':complex,
        'bool':bool 
    }

    def __init__(self,description):
        self.description=description             
    
    def transform(self,row):                
        # TODO : TO check : data and description should have same keys.                    
        for column in row:
            transform_method=self._transform_method[self.description[column]]
            row[column]=transform_method(row[column])        




class component(signal,statistic):
    """
       Base class of ETL Component.
    """    

    is_end = False    
    _start_input={}
    _start_output={} 
    
        
    def action_start(self,key,signal_data={},data={}):
         trans=signal_data.get('trans',None)     
         stat_date=signal_data.get('start_date',None)             
         self.statistic( \
             str(key), \
             trans and str(trans.destination) or None, \
             trans and str(trans.channel_source) or None, \
             trans and str(trans.channel_destination) or None, \
             len(self.data[trans]), \
             stat_date)         
         self.logger.notifyChannel("component", LOG_INFO, 
                     'the '+str(self)+' is start now...')
         return True

    def action_start_input(self,key,signal_data={},data={}):
         self.logger.notifyChannel("component", LOG_INFO, 
                     'the '+str(self)+' is start to taken input...')
         return True

    def action_start_output(self,key,signal_data={},data={}):
         self.logger.notifyChannel("component", LOG_INFO, 
                     'the '+str(self)+' is start to give output...')
         return True

    def action_no_input(self,key,signal_data={},data={}):      
         self.logger.notifyChannel("component", etl.LOG_WARNING, 
                     'the '+str(self)+' has no input data...')        
         return True

    def action_stop(self,key,signal_data={},data={}):    
         self.logger.notifyChannel("component", LOG_INFO, 
                     'the '+str(self)+' is stop now...')                
         return True

    

    def action_end(self,key,signal_data={},data={}):         
         trans=signal_data.get('trans',None)         
         stat_date=signal_data.get('end_date',None)         
         self.statistic( \
             str(key), \
             trans and str(trans.destination) or None, \
             trans and str(trans.channel_source) or None, \
             trans and str(trans.channel_destination) or None, \
             len(self.data[trans]), \
             stat_date)
         self.logger.notifyChannel("component", LOG_INFO, 
                     'the '+str(self)+' is end now...')
         return True 
         

    def action_error(self,key,signal_data={},data={}):   
         error_value={
              'error_from':str(key),
              'error_msg':signal_data.get('error_msg'),
              'error_date':signal_data.get('error_date')
         }       
         self.errors.append(error_value)     
         self.logger.notifyChannel("component", etl.LOG_ERROR, 
                     str(self)+' : ' + error_value['error_from'] + ','+error_value['error_msg'])
         return True

    def __init__(self,name='',transformer=None,*args, **argv):
        super(component, self).__init__(*args, **argv)    
        self.name=name     
        self.trans_in = []
        self.trans_out = []
        self.is_output = False
        self.data = {}
        self.errors=[]
        self.generator = None
        self.transformer=transformer
        self.logger = Logger()

        self.signal_connect(self,'start',self.action_start)
        self.signal_connect(self,'start_input',self.action_start_input)
        self.signal_connect(self,'start_output',self.action_start_output)
        self.signal_connect(self,'no_input',self.action_no_input)
        self.signal_connect(self,'stop',self.action_stop)        
        self.signal_connect(self,'end',self.action_end)
        self.signal_connect(self,'error',self.action_error)

        

    def __str__(self):
        return '<Component : '+self.name+'>'

    def generator_get(self, transition):
        """ Get generator list of transition
        """
        if self.generator:
            return self.generator
        self.generator = self.process()
        return self.generator

    def channel_get(self, trans=None):
        """ Get channel list of transition
        """        
        if trans and trans.status=='close':
            return
        self.data.setdefault(trans, [])
        self._start_output.setdefault(trans,False)
        self._start_input.setdefault(trans,False)
        gen = self.generator_get(trans) or [] 
        if trans:
            trans.signal('start')      
        self.signal('start',{'trans':trans,'start_date':datetime.datetime.today()})     
        while True:            
            if self.data[trans]:                
                if not self._start_output[trans]:
                    self._start_output[trans]=datetime.datetime.today()                               
                    self.signal('start_output',{'trans':trans,'start_output_date':datetime.datetime.today()})
                yield self.data[trans].pop(0)                
                continue
            elif self.data[trans] is None:
                self.signal('no_input')               
                raise StopIteration
            if not self._start_input[trans]:   
                self._start_input[trans]=datetime.datetime.today()
                self.signal('start_input',{'trans':trans,'start_input_date':datetime.datetime.today()})
            data, chan = gen.next()             
            if data is None:
                self.signal('no_input')               
                raise StopIteration            
            for t,t2 in self.trans_out:
                if (t == chan) or (not t) or (not chan):
                    self.data.setdefault(t2, [])
                    self.data[t2].append(data)   
        if trans:
            trans.signal('stop')     
        self.signal('end',{'trans':trans,'channel_source':chan,'end_date':datetime.datetime.today()})

    def process(self):
        """ process method of ETL component
        """
        pass


    def input_get(self):
        """ Get input iterator of ETL component
        """
        result = {}
        for channel,trans in self.trans_in:
            result.setdefault(channel, [])
            result[channel].append(trans.source.channel_get(trans))
        return result


class transition(signal):
    """
       Base class of ETL transition.
    """
    

    def action_start(self,key,signal_data={},data={}):
        self.status='start'
        self.logger.notifyChannel("transition", LOG_INFO, 
                     'the '+str(self)+' is start now...')
        return True 

    def action_pause(self,key,signal_data={},data={}):
        self.status='pause'
        self.logger.notifyChannel("transition", LOG_INFO, 
                     'the '+str(self)+' is pause now...')
        return True 

    def action_stop(self,key,signal_data={},data={}):
        self.status='stop'
        self.logger.notifyChannel("transition", LOG_INFO, 
                     'the '+str(self)+' is stop now...')
        return True    

    def __str__(self):
        return str(self.source)+' to '+str(self.destination)

    def __init__(self, source, destination, channel_source='main', channel_destination='main', type='data'):
        super(transition, self).__init__() 
        self.type = type
        self.source = source
        self.destination = destination
        self.channel_source = channel_source
        self.channel_destination = channel_destination
        self.destination.trans_in.append((channel_destination,self))
        self.source.trans_out.append((channel_source,self))
        self.status='open' # open,start,pause,stop,close 
                           # open : active, start : in running, pause : pause, stop: stop, close : inactive

        self.logger = Logger()
        self.signal_connect(self,'start',self.action_start)
        self.signal_connect(self,'pause',self.action_pause)
        self.signal_connect(self,'stop',self.action_stop)

class job(signal):
    """
       Base class of ETL job.
    """
    def action_start(self,key,signal_data={},data={}):
        self.status='start'        
        self.logger.notifyChannel("job", LOG_INFO, 
                     'the '+str(self)+' is start now...')
        return True

    def action_pause(self,key,signal_data={},data={}):
        self.status='pause'
        self.logger.notifyChannel("job", LOG_INFO, 
                     'the '+str(self)+' is pause now...')
        #TODO : pause job process
        return True

    def action_stop(self,key,signal_data={},data={}):
        self.status='stop'
        self.logger.notifyChannel("job", LOG_INFO, 
                     'the '+str(self)+' is stop now...')
        #TODO : stop job process
        return True

    def action_copy(self,key,signal_data={},data={}):
        #TODO : copy job process
        self.logger.notifyChannel("job", LOG_INFO, 
                     'the '+str(self)+' is coping now...')
        return True

 
    def __init__(self,name,outputs=[]):
        super(job, self).__init__()
        self.name=name
        self.outputs=outputs
        self.status='open' # open,start,pause,stop,close
        
        self.signal_connect(self,'start',self.action_start)
        self.signal_connect(self,'pause',self.action_pause)
        self.signal_connect(self,'stop',self.action_stop)
        self.signal_connect(self,'copy',self.action_copy)
        self.logger = Logger()
    def __str__(self):     
        #TODO : return complete print of the job (all components and transitions)
        return self.name   
    
    
    def import_job(self,connector):
        #TODO : read job instance from file
        pass
    def export_job(self,connector):
        #TODO : write job instance in file
        pass

    def run(self):
        # run job process
        self.signal('start')
        for c in self.outputs:
            for a in c.channel_get():
                pass
        self.signal('stop')

class connector(object):
    """
        Base class of ETL Connector.
    """
    def __init__(self,uri,bufsize=-1,encoding=False):        
        self.uri=uri
        self.bufsize=bufsize
        self.encoding=encoding
    def open(self,mode=False):
        return True
    def __str__(self):        
        return self.uri
    def close(self):
        return True


                        
        
        


def test1():    
    fileconnector=etl.connector.file_connector.file_connector('demo/data/invoice.csv')
    transformer.description= {'id':etl.transformer.LONG,'name':etl.transformer.STRING,'invoice_date':etl.transformer.DATE,'invoice_amount':etl.transformer.FLOAT,'is_paid':etl.transformer.BOOLEAN}    
    transformer=etl.transformer(transformer.description)
    csv_in1= etl.component.input.csv_in.csv_in(fileconnector=fileconnector,transformer=transformer)
    log1=etl.component.transform.logger.logger(name='Read Invoice File')
    tran=etl.etl.transition(csv_in1,log1)
    job1=etl.etl.job([log1])
    job1.run()


if __name__ == '__main__':
    pass
    #test1()






