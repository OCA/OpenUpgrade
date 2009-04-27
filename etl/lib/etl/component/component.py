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
"""
ETL Component.

Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
GNU General Public License
"""
import datetime
from etl import signal


class component(signal):
    """
    Base class of ETL Component.
    """

    def __init__(self, name='', connector=None, transformer=None, row_limit=0):
        super(component, self).__init__() 
        self._type='component'       
        self._cache={}        
        self.trans_in=[]
        self.trans_out=[]
        self.data={}
        self.job=False
        self.generator=None
        self.name=name
        self.connector=connector
        self.transformer=transformer
        self.row_limit=row_limit
        self.status='open'
            

    def __str__(self):                   
        res='<Component job="%s" name="%s" type="%s"'% (self.job.name, self.name, self._type)
        if self.is_start():
            res += ' is_start="True"'
        if self.is_end():
            res += ' is_end="True"'
        res += ">"
        return res
    
            

    def __copy__(self):        
        res=component(name=self.name,transformer=self.transformer)
        return res

    def copy(self):
        res=self.__copy__()
        res.name+='(copy)'
        return res

    def is_start(self):        
        if not len(self.trans_in):
            return True
        return False

    def is_end(self):        
        if not len(self.trans_out):
            return True
        return False

    

    def pause(self):        
        self.status='pause'
        self.signal('pause')

    def stop(self):        
        self.status='stop'
        self.signal('stop')  

    def end(self):
        self.status='end'
        self.signal('end')  

    def start(self):
        self.status='start'
        self.signal('start')

    def generator_get(self, transition):
        """
        Get generator list of transition
        """
        if self.generator:
            return self.generator
        self.generator=self.process()
        return self.generator

    def channel_get(self, trans=None):
        """
        Get channel list of transition
        """        
        #if self.status in ('end','stop') or (trans and trans.type=='trigger' and trans.status in ('end','stop','close')):
        #    return
        self.data.setdefault(trans, [])
        self._cache['start_output']={trans:False}
        self._cache['start_input']={trans:False}
        gen=self.generator_get(trans) or None
        if trans:
            trans.start()
        self.start()
        try:
            row_count=0
            while True:
                if self.data[trans]:
                    if not self._cache['start_output'][trans]:
                        self._cache['start_output'][trans]=datetime.datetime.today()
                        self.signal('start_output', {'trans':trans, 'start_output_date':datetime.datetime.today()})
                    self.signal('send_output', {'trans':trans, 'send_output_date':datetime.datetime.today()})
                    yield self.data[trans].pop(0)
                    continue
                elif self.data[trans] is None:                    
                    self.signal('no_input')
                    raise StopIteration
                if not self._cache['start_input'][trans]:
                    self._cache['start_input'][trans]=datetime.datetime.today()
                    self.signal('start_input', {'trans':trans, 'start_input_date':datetime.datetime.today()})
                self.signal('get_input', {'trans':trans, 'get_input_date':datetime.datetime.today()})

                

                data, chan=gen.next() 
                row_count+=1                 
                if self.row_limit and row_count > self.row_limit:
                     raise StopIteration
              
                if data is None:                    
                    self.signal('no_input')
                    raise StopIteration

                
                if self.transformer:
                    data=self.transformer.transform(data)

                for t, t2 in self.trans_out:                    
                    if (t == chan) or (not t) or (not chan):
                        self.data.setdefault(t2, [])
                        self.data[t2].append(data)        

        except StopIteration, e:                       
            if trans:
                trans.end()
            self.end()           

        except Exception, e:
            self.signal('error', {'data':self.data, 'type':'exception', 'error':str(e)}) 
            

    def process(self):
        """
        process method of ETL component
        """
        pass

    def get_trigger_data(self,channel,trigger):
        return None

    def input_get(self):
        """
        Get input iterator of ETL component
        """
        result={}
        for channel, trans in self.trans_in:
            result.setdefault(channel, [])
            if trans=='trigger':
                data=trans.source.get_trigger_data(channel,trans.trigger)
            else:
                data=trans.source.channel_get(trans)
            result[channel].append(data)
        return result
