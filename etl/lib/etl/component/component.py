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
from etl import logger



class component(signal):
    """
    Base class of ETL Component.
    """   
    def action_start(self, key, signal_data={}, data={}):
        self.logger.notifyChannel("component", logger.LOG_INFO, 
                     'the '+str(self)+' is start now...')
        return True

    def action_start_input(self, key, signal_data={}, data={}):
        self.logger.notifyChannel("component", logger.LOG_INFO, 
                     'the '+str(self)+' is start to taken input...')
        return True

    def action_start_output(self, key, signal_data={}, data={}):
        self.logger.notifyChannel("component", logger.LOG_INFO, 
                     'the '+str(self)+' is start to give output...')
        return True

    def action_no_input(self, key, signal_data={}, data={}): 
        self.logger.notifyChannel("component", logger.LOG_WARNING, 
                     'the '+str(self)+' has no input data...')   
        return True

    def action_stop(self, key, signal_data={}, data={}): 
        # TODO : stop all IN_trans and OUT_trans  related this component
        self.logger.notifyChannel("component", logger.LOG_INFO, 
                     'the '+str(self)+' is stop now...')
        return True

   

    def action_end(self, key, signal_data={}, data={}): 
        self.logger.notifyChannel("component", logger.LOG_INFO, 
                     'the '+str(self)+' is end now...') 
        return True


    def action_error(self, key, signal_data={}, data={}):                 
        self.logger.notifyChannel("component", logger.LOG_ERROR, 
                     str(self)+' : '+signal_data.get('error','False'))
        #yield {'error_msg':'Error  :'+str(e), 'error_date':datetime.datetime.today()}, 'error'
        return True

    def __init__(self, name='', transformer=None):
        super(component, self).__init__()  
        self._cache={} 
        self.name=name
        self.trans_in = []
        self.trans_out = []        
        self.data = {}        
        self.generator = None
        self.transformer=transformer
        self.logger = logger.logger()
        self.status = False
        self.signal_connect(self, 'start', self.action_start)
        self.signal_connect(self, 'start_input', self.action_start_input)
        self.signal_connect(self, 'start_output', self.action_start_output)
        self.signal_connect(self, 'no_input', self.action_no_input)
        self.signal_connect(self, 'stop', self.action_stop)
        self.signal_connect(self, 'end', self.action_end)
        self.signal_connect(self, 'error', self.action_error)

    def __copy__(self):
        res=component(name=self.name,transformer=self.transformer)
        trans_in=[]
        for tran_in in self.trans_in:
            new_tran_in=tran_in.copy()
            new_tran_in.destination=res
            trans_in.append(new_tran_in)   
        trans_out=[]
        for tran_out in self.trans_out:
            new_tran_out=tran_out.copy()
            new_tran_out.source=res
            trans_out.append(new_tran_out) 
        res.trans_in=trans_in
        res.trans_out=trans_out
        return res


    def __str__(self):
        if not self.name:
            self.name=''
    	return '<Component : '+self.name+'>'

    def generator_get(self, transition):
        """ 
        Get generator list of transition
        """
        if self.generator:
            return self.generator
        self.generator = self.process()
        return self.generator

    def channel_get(self, trans=None):
        """ 
        Get channel list of transition
        """
        if trans and trans.status=='close':
            return
        self.data.setdefault(trans, [])
        self._cache['start_output']={trans:False}
        self._cache['start_input']={trans:False}        
        gen = self.generator_get(trans) or []  
        if trans:
            trans.status='start'
            trans.signal('start')
        self.status='start'
        self.signal('start')
        try: 
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
                data, chan = gen.next() 
                if data is None:
                    self.signal('no_input')   
                    raise StopIteration
                for t, t2 in self.trans_out:
                    if (t == chan) or (not t) or (not chan):
                        self.data.setdefault(t2, [])
                        self.data[t2].append(data)   
        except StopIteration, e:            
            if trans:
                trans.status='end'
                trans.signal('end') 
            self.status='end' 
            self.signal('end')

    def process(self):
        """ 
        process method of ETL component
        """
        pass


    def input_get(self):
        """ 
        Get input iterator of ETL component
        """
        result = {}
        for channel, trans in self.trans_in:
            result.setdefault(channel, [])
            result[channel].append(trans.source.channel_get(trans))
        return result
