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
from mx import DateTime

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
    """
    def __init__(self,*args, **argv):
        self.__connects={}  
    
    def signal(self, signal, signal_data=None):
        for fnct,data,key in self.__connects.get(signal, []):
            fnct(self, signal_data, *data)
        return True

    def signal_connect(self, key, signal, fnct, *data):
        self.__connects.setdefault(signal, [])
        if (fnct, data, key) not in self.__connects[signal]:
            self.__connects[signal].append((fnct, data, key))
        return True

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
        return True
    
class transformer(object):
    """
        transfer data into different type.
        pass description like :
          - INTEGER  : convert string to Integer object
          - FLOAT : convert string to float object
          - LONG  : convert string to long integer object
          - COMPLEX : convert string to complex number
          - STRING : convert string to string
          - DATE   : convert string to date object
          - DATETIME : convert string to datetime object
          - BOOLEAN : convert string to boolean object
        example :
           datas = [{'id':'1','name':'abc','invoice_date':'2009-10-20','invoice_amount':'200.00','is_paid':'1'}]
           description= {'id':etl.transformer.LONG,'name':etl.transformer.STRING,'invoice_date':etl.transformer.DATE,'invoice_amount':etl.transformer.FLOAT,'is_paid':etl.transformer.BOOLEAN}
           return = [{'id':1,'name':'abc','invoice_date':<mx.DateTime.DateTime object -2009-10-20>,'invoice_amount':200.00,'is_paid':True}]
    """
    INTEGER='int'
    STRING='str'
    DATE='date'
    DATETIME='datetime'
    FLOAT='float'
    LONG='long'
    COMPLEX='complex'
    BOOLEAN='bool'

    DATE_FORMAT='%Y-%m-%d'
    DATETIME_FORMAT='%Y-%m-%d %H:%M:%S'

    _transform_method={
        'int':lambda x:int(x),
        'str':lambda x:str(x),
        'date':lambda x:DateTime.strptime(x,transformer.DATE_FORMAT),
        'datetime':lambda x:DateTime.strptime(x,transformer.DATETIME_FORMAT),
        'float':lambda x:float(x),
        'long':lambda x:long(x),
        'complex':lambda x:complex(x),
        'bool':lambda x:bool(x) 
    }

    def __init__(self,description={}):
        self.description=description             
    
    def transform(self,datas,encoding='utf-8'):                
        # TODO : TO check : data and description should have same keys.
        if type(datas)!=list:
           datas=[datas]
        for row in datas:            
            for column in row:
                transform_method=self._transform_method[self.description[column]]
                row[column]=transform_method(row[column].decode(encoding))        

class component(signal):
    """
       Base class of ETL Component.
    """
    is_end = False
    def __init__(self,*args, **argv):
        super(component, self).__init__(*args, **argv) 
        self.trans_in = []
        self.trans_out = []
        self.is_output = False
        self.data = {}
        self.generator = None
        self.transformer=None
        

    def __str__(self):
        return self.data

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
        gen = self.generator_get(trans) or []
        while True:
            if self.data[trans]:
                yield self.data[trans].pop(0)
                continue
            elif self.data[trans] is None:
                raise StopIteration
            data, chan = gen.next()
            if data is None:
                raise StopIteration
            for t,t2 in self.trans_out:
                if (t == chan) or (not t) or (not chan):
                    self.data.setdefault(t2, [])
                    self.data[t2].append(data)

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
    def open(self,mode=False):
        return True
    def __str__(self):        
        return self.connection_string
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






