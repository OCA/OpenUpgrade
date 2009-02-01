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




class statitic(object):
    """
    This class computes basic statistics and return them at the end of the process like data in a channel called "statistics":
    Input Channel | # of Records | Time To Process | Time/Record | Memory Usage
    main          | 1244         | 123 sec         | 0.1 sec     | 1Mb
    other         | 144          | 12 sec          | 0.1 sec     | 1Mb
    """
    
    statitics={}
    def statitic(self,source_component,destination_component,source_channel,destination_channel,total_record,stat_time):
        input_channel=(source_component,destination_component,source_channel,destination_channel)
        if input_channel not in self.statitics:
            self.statitics.setdefault(input_channel,{                   
                       'input_channel':input_channel,
                       'total_records':0,
                       'total_time':0,
                       'record_time':0,
                       'memory':0,
                       'start':stat_time
            })
        stat=self.statitics[input_channel]        
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
        'int':lambda x:int(x),
        'str':lambda x:str(x),
        'date':lambda x:datetime.datetime.strptime(x,transformer.DATE_FORMAT).date(),
        'time':lambda x:datetime.datetime.strptime(x,transformer.TIME_FORMAT).time(),
        'datetime':lambda x:datetime.datetime.strptime(x,transformer.DATETIME_FORMAT),
        'float':lambda x:float(x),
        'long':lambda x:long(x),
        'complex':lambda x:complex(x),
        'bool':lambda x:bool(x) 
    }

    def __init__(self,description):
        self.description=description             
    
    def transform(self,datas):                
        # TODO : TO check : data and description should have same keys.
        if type(datas)!=list:
           datas=[datas]
        for row in datas:            
            for column in row:
                transform_method=self._transform_method[self.description[column]]
                row[column]=transform_method(row[column])        

class component(signal,statitic):
    """
       Base class of ETL Component.
    """
    _name='etl.component'  
    _description='This is an ETL Component'   
    _author='tiny'

    is_end = False    
    _start_input={}
    _start_output={} 
    
        
    def action_start(self,key,singal_data={},data={}):
         trans=singal_data.get('trans',None)     
         stat_date=singal_data.get('start_date',None)             
         self.statitic( \
             str(key), \
             trans and str(trans.destination) or None, \
             trans and str(trans.channel_source) or None, \
             trans and str(trans.channel_destination) or None, \
             len(self.data[trans]), \
             stat_date)
         return True

    def action_start_input(self,key,singal_data={},data={}):
         return True

    def action_start_output(self,key,singal_data={},data={}):
         return True

    def action_no_input(self,key,singal_data={},data={}):              
         return True

    def action_stop(self,key,singal_data={},data={}):                   
         return True

    def action_continue(self,key,singal_data={},data={}):                   
         return True

    def action_end(self,key,singal_data={},data={}):         
         trans=singal_data.get('trans',None)         
         stat_date=singal_data.get('end_date',None)         
         self.statitic( \
             str(key), \
             trans and str(trans.destination) or None, \
             trans and str(trans.channel_source) or None, \
             trans and str(trans.channel_destination) or None, \
             len(self.data[trans]), \
             stat_date)
         return True 
         

    def action_error(self,key,singal_data={},data={}):   
         error_value={
              'error_from':str(key),
              'error_msg':singal_data.get('error_msg'),
              'error_date':singal_data.get('error_date')
         }       
         self.errors.append(error_value)     
         return True

    def __init__(self,transformer=None,*args, **argv):
        super(component, self).__init__(*args, **argv)         
        self.trans_in = []
        self.trans_out = []
        self.is_output = False
        self.data = {}
        self.errors=[]
        self.generator = None
        self.transformer=transformer

        self.signal_connect(self,'start',self.action_start)
        self.signal_connect(self,'start_input',self.action_start_input)
        self.signal_connect(self,'start_output',self.action_start_output)
        self.signal_connect(self,'no_input',self.action_no_input)
        self.signal_connect(self,'stop',self.action_stop)
        self.signal_connect(self,'continue',self.action_continue)
        self.signal_connect(self,'end',self.action_end)
        self.signal_connect(self,'error',self.action_error)
        

    def __str__(self):
        return '<Component : '+self._name+'>'

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
        self.data.setdefault(trans, [])
        self._start_output.setdefault(trans,False)
        self._start_input.setdefault(trans,False)
        gen = self.generator_get(trans) or []   
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


class transition(object):
    """
       Base class of ETL transition.
    """
    def __init__(self, source, destination, channel_source='main', channel_destination='main', type='data'):
        self.type = type
        self.source = source
        self.destination = destination
        self.channel_source = channel_source
        self.channel_destination = channel_destination
        self.destination.trans_in.append((channel_destination,self))
        self.source.trans_out.append((channel_source,self))

class job(object):
    """
       Base class of ETL job.
    """
    def __init__(self,outputs=[]):
        self.outputs=outputs
    def __str__(self):
        pass

    def run(self):
        for c in self.outputs:
            for a in c.channel_get():
                pass

class connector(object):
    """
        Base class of ETL Connector.
    """
    def __init__(self,*args,**argv):
        self.host=argv.get('host',False)
        self.port=argv.get('port',False)
        self.uid=argv.get('uid',False)
        self.pwd=argv.get('pwd',False)
        self.connection_string=argv.get('connection_string',False)
        self.connection_type=argv.get('connection_type',False)
        self.encoding=argv.get('encoding',False)
    def open(self,mode=False):
        return True
    def __str__(self):        
        return self.connection_string
    def close(self):
        return True


                        
        
        


def test1():    
    fileconnector=connector.file_connector.file_connector('demo/data/invoice.csv')
    transformer.description= {'id':transformer.LONG,'name':transformer.STRING,'invoice_date':transformer.DATE,'invoice_amount':transformer.FLOAT,'is_paid':transformer.BOOLEAN}    
    transformer=transformer(transformer.description)
    csv_in1= component.input.csv_in.csv_in(fileconnector=fileconnector,transformer=transformer)
    log1=component.transform.logger.logger(name='Read Invoice File')
    tran=etl.transition(csv_in1,log1)
    job1=etl.job([log1])
    job1.run()


if __name__ == '__main__':
    #test1()
    pass






