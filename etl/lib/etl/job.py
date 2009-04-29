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
 Defines ETL job with ETL components.

 Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). 
 GNU General Public License.
"""
from signal import signal
import time
import logger
import pickle
import datetime

class job(signal):
    """
    Base class of ETL job.
    """ 
 
    def __init__(self, components=[], name='job'):        
        super(job, self).__init__()
        self.name = name
        self._components = components    
        self._cache = {}    
        for component in self._components:
            component.job = self   
        self.status = 'open' # open, start, pause, stop, close
        self.pickle = False
        self.logger = logger.logger()

    def __str__(self):           
        res = '<Job name="%s" status="%s">' % (self.name, self.status)
        components = [] 
        trans = []
        for component in self.get_components():            
            res += "\n" + str(component)
        for transition in self.get_transitions():            
            res += "\n" + str(transition)         
        return res    
    
    def __copy__(self):
        """
        Copy job instance.
        """
        new_outputs = []
        new_transitions = []
        new_components = {}       
        for transition in self.get_transitions():
            new_tra=transition.copy()
            if transition.source not in new_components:
                new_components[transition.source] = transition.source.copy()                
            if transition.destination not in new_components:
                new_components[transition.destination] = transition.destination.copy()

            new_tra.source = new_components[new_tra.source]
            new_tra.destination = new_components[new_tra.destination]
            new_tra.destination.trans_in.append((new_tra.channel_destination, new_tra))
            new_tra.source.trans_out.append((new_tra.channel_source, new_tra))
            new_transitions.append(new_tra)

        res = job(new_components.values(), self.name + '(copy)')
        self.signal('copy', {'date': datetime.datetime.today()})
        return res

    def copy(self):		
        return self.__copy__()

    def get_components(self):
        return self._components

    def add_component(self, component):
        self._componets.append(component)
        
    def get_transitions(self):
        transitions = []
        for component in self.get_components():
            for channel, tran_in in component.trans_in:            
                if tran_in not in transitions:
                    transitions.append(tran_in)
            for channel, tran_out in component.trans_out:                
                if tran_out not in transitions:
                    transitions.append(tran_out)             
        return transitions
    
    def write(self):
        """
        Store job instance into pickle object.
        """        
        return pickle.dumps(self)
        
    def read(self,value): 
        """
        Read job instance value from pickle object.
        Parameter
        value - pickle value  
        """     
        return pickle.load(value)
      
    def pause(self): 
        self.pickle = self.write()     
        for tran in self.get_transitions():
            tran.pause()
        self.status = 'pause'
        self.signal('pause', {'date': datetime.datetime.today()})
        return self.pickle

    def restart(self):      
        for tran in self.get_transitions():
            tran.restart()           
        
        self.status = 'start'
        self.signal('restart', {'date': datetime.datetime.today()}) 

    def start(self):              
        self.register_actions()  
        self.status = 'start'            
        self.signal('start', {'date': datetime.datetime.today()})        
        for c in self.get_end_components():
            for a in c.channel_get():              
                pass 

    def end(self):
        self.status = 'end'
        self.signal('end', {'date': datetime.datetime.today()})
        
        
    def open(self):
        self.status = 'open'

    def close(self):
        self.status = 'close'

    def stop(self):
        for tran in self.get_transitions():
            tran.stop()                
        self.status = 'stop'
        self.signal('stop', {'date': datetime.datetime.today()})
          
    def get_end_components(self):
        end_components = []
        for component in self.get_components():         
            if component.is_end():
                end_components.append(component)       
        return end_components

    def get_statitic_info(self):
        stat_info =  'Statistical Information (process time in microsec):\n'
        stat_info += '======================================\n'
        stat_info += 'Job : %s\n' %(self.name)
        stat_info += '-------------------\n'
        stat_info += 'Start : %s\n' %(self._cache['start_date'])
        stat_info += 'End   : %s\n' %(self._cache['end_date'])
        stat_info += 'Total Process time : %s\n' %(self._cache['process_time'])
        for component in self.get_components():
             stat_info += '\nComponent : %s\n'%(component)
             stat_info += '---------------------------------\n'
             stat_info += 'Start : %s\n' %(component._cache['start_date'])
             stat_info += 'End   : %s\n' %(component._cache['end_date'])
             stat_info += 'Total Process time : %s\n' %(component._cache['process_time'])
             for trans,value in component._cache['trans'].items():
                stat_info += '\nOut Transition : %s\n'%trans
                stat_info += '---------------------------------\n'
                stat_info += 'Total Inputs : %s\n'%value.get('total_inputs',0)
                stat_info += 'Total Outputs : %s\n'%value.get('total_outputs',0)
                stat_info += 'Total Input Process Time : %s\n'%value.get('input_process_time',0)
                stat_info += 'Total Output Process Time : %s\n'%value.get('output_process_time',0)
                stat_info += 'Input Process Time per Record : %s\n'%value.get('input_process_time_per_record',0)
                stat_info += 'Output Process Time per Record : %s\n'%value.get('output_process_time_per_record',0)
        return stat_info         
                

    def run(self):              
        if self.pickle:
            job = self.read(self.pickle)
            job.restart()
            job.end()
        else:
            self.start()
            self.end()
        

    def register_actions(self):
        self.register_actions_job(self)
        for component in self.get_components():
            self.register_actions_component(component)
            if component.connector:
                self.register_actions_connector(component.connector)
        for transition in self.get_transitions():
            self.register_actions_transition(transition)

    def register_actions_job(self, job):
        job.signal_connect(job, 'start', self.action_job_start)
        job.signal_connect(job, 'pause', self.action_job_pause)
        job.signal_connect(job, 'stop', self.action_job_stop)
        job.signal_connect(job, 'end', self.action_job_end)
        job.signal_connect(job, 'copy', self.action_job_copy)

    def register_actions_component(self, component):        
        component.signal_connect(component, 'start', self.action_component_start)
        component.signal_connect(component, 'start_input', self.action_component_start_input)
        component.signal_connect(component, 'start_output', self.action_component_start_output)
        component.signal_connect(component, 'get_input', self.action_component_get_input)
        component.signal_connect(component, 'send_output', self.action_component_send_output)
        component.signal_connect(component, 'no_input', self.action_component_no_input)
        component.signal_connect(component, 'stop', self.action_component_stop)
        component.signal_connect(component, 'end', self.action_component_end)
        component.signal_connect(component, 'error', self.action_component_error)
        component.signal_connect(component, 'warning', self.action_component_warning)

    def register_actions_connector(self, connector):
        connector.signal_connect(connector, 'open', self.action_connector_open)
        connector.signal_connect(connector, 'close', self.action_connector_close)
        connector.signal_connect(connector, 'error', self.action_connector_error)


    def register_actions_transition(self, transition):        
        transition.signal_connect(transition, 'start', self.action_transition_start)
        transition.signal_connect(transition, 'pause', self.action_transition_pause)
        transition.signal_connect(transition, 'stop', self.action_transition_stop)
        transition.signal_connect(transition, 'end', self.action_transition_end)
    

    def action_job_start(self, key, signal_data={}, data={}):              
        self.logger.notifyChannel("job", logger.LOG_INFO, 
                     'the <' + key.name + '> has started now...')
        key._cache['start_date'] =  signal_data.get('date',False)        
        return True
  
    def action_job_restart(self, key, signal_data={}, data={}):          
        self.logger.notifyChannel("job", logger.LOG_INFO, 
                     'the <' + key.name + '> has started now...')
        return True

    def action_job_pause(self, key, signal_data={}, data={}):      
        self.logger.notifyChannel("job", logger.LOG_INFO, 
                     'the <' + key.name + '> is paused now...')        
        return True

    def action_job_stop(self, key, signal_data={}, data={}):
        self.logger.notifyChannel("job", logger.LOG_INFO, 
                     'the <' + key.name + '> has stopped now...')    
        return True

    def action_job_end(self, key, signal_data={}, data={}):      
        self.logger.notifyChannel("job", logger.LOG_INFO, 
                     'the <' + key.name + '> has ended now...')           
        start_time = key._cache.get('start_date',False)
        current_time = signal_data.get('date',datetime.datetime.today())
        diff = 0
        if current_time and start_time:
            diff = (current_time - start_time).microseconds
    
        key._cache['end_date'] =  current_time
        key._cache['process_time'] = diff
        return True

    def action_job_copy(self, key, signal_data={}, data={}):      
        self.logger.notifyChannel("job", logger.LOG_INFO, 
                     'the <' + key.name + '> is coping now...')
        return True

    def action_connector_open(self, key, signal_data={}, data={}):        
        self.logger.notifyChannel("connector", logger.LOG_INFO,
                     'the <' + key.name + '> is open now...')
        return True

    def action_connector_close(self, key, signal_data={}, data={}):
        self.logger.notifyChannel("connector", logger.LOG_INFO,
                    'the <' + key.name + '> is closed now...')
        return True
    
    def action_connector_error(self, key, signal_data={}, data={}):
        self.logger.notifyChannel("connector", logger.LOG_ERROR,
                    '<' + key.name + '> : '+signal_data.get('message', False))
        return True
    

    def action_component_start(self, key, signal_data={}, data={}):
        self.logger.notifyChannel("component", logger.LOG_INFO,
                     'the <' + key.name + '> has started now...')
        key._cache['start_date'] = signal_data.get('date',False)        
        return True

    def action_component_start_input(self, key, signal_data={}, data={}):             
        if 'trans' not in key._cache:
            key._cache['trans'] = {}
        value = key._cache['trans']
        trans = signal_data.get('trans',False)
        if trans not in value:
            value[trans] = {}
        value[trans].update({'start_input' : signal_data.get('date',False)})
        return True

    def action_component_start_output(self, key, signal_data={}, data={}):        
        if 'trans' not in key._cache:
            key._cache['trans'] = {}
        value = key._cache['trans']
        trans = signal_data.get('trans',False)
        if trans not in value:
            value[trans] = {}
        value[trans].update({'start_output' : signal_data.get('date',False)})
        return True

    def action_component_get_input(self, key, signal_data={}, data={}):        
        if 'trans' not in key._cache:
            key._cache['trans'] = {}
        value = key._cache['trans']

        trans = signal_data.get('trans',False)
        total = value[trans].get('total_inputs',0)
        total += 1
        start_time = value[trans].get('start_input',False)        
        current_time = signal_data.get('date',datetime.datetime.today())        
        diff = 0
        if current_time and start_time:
            diff = (current_time - start_time).microseconds
        process_per_record = 0
        if total :            
            process_per_record =  diff / total        
        value[trans].update({'total_inputs' : total, 'input_process_time' : diff ,'input_process_time_per_record' : process_per_record})
        return True

    def action_component_send_output(self, key, signal_data={}, data={}):        
        if 'trans' not in key._cache:
            key._cache['trans'] = {}
        value = key._cache['trans'] 

        trans = signal_data.get('trans',False)
        total = value[trans].get('total_outputs',0)
        total += 1
        start_time = value[trans].get('start_output',False)
        current_time = signal_data.get('date',datetime.datetime.today())
        diff = 0
        if current_time and start_time:
            diff = (current_time - start_time).microseconds
        process_per_record = 0
        if total :
            process_per_record =  diff / total
        value[trans].update({'total_outputs' : total, 'output_process_time' : diff ,'output_process_time_per_record' : process_per_record})
        return True

    def action_component_no_input(self, key, signal_data={}, data={}):
        self.logger.notifyChannel("component", logger.LOG_WARNING,
                     'the <' + key.name + '> has no input data...')
        return True

    def action_component_stop(self, key, signal_data={}, data={}):        
        self.logger.notifyChannel("component", logger.LOG_INFO,
                     'the <' + key.name + '> has stopped now...')        
        return True

    def action_component_end(self, key, signal_data={}, data={}):
        self.logger.notifyChannel("component", logger.LOG_INFO,
                     'the <' + key.name + '> has ended now...')      
        
        value = key._cache
        start_time = value.get('start_date',False)
        current_time = signal_data.get('date',datetime.datetime.today())
        diff = 0
        if current_time and start_time:
            diff = (current_time - start_time).microseconds
        value.update({'end_date' : current_time, 'process_time' : diff})
        return True

    def action_component_error(self, key, signal_data={}, data={}):
        self.logger.notifyChannel("component", logger.LOG_ERROR,
                     '<' + key.name + '> : ' + signal_data.get('message', 'False'))        
        return True

    def action_component_warning(self, key, signal_data={}, data={}):        
        self.logger.notifyChannel("component", logger.LOG_WARNING,
                    '<' + key.name + '> : '+signal_data.get('message', False))
        return True

    def action_transition_start(self, key, signal_data={}, data={}):       
        self.logger.notifyChannel("transition", logger.LOG_INFO, 
                     'the <%s> to <%s>  has started now...'%(key.source.name, key.destination.name))        
        return True 

    def action_transition_pause(self, key, signal_data={}, data={}):       
        self.logger.notifyChannel("transition", logger.LOG_INFO, 
                     'the <%s> to <%s>  has started now...'%(key.source.name, key.destination.name))
        return True 

    def action_transition_stop(self, key, signal_data={}, data={}):       
        self.logger.notifyChannel("transition", logger.LOG_INFO, 
                     'the <%s> to <%s>  has started now...'%(key.source.name, key.destination.name))
        return True 
  
    def action_transition_end(self, key, signal_data={}, data={}):       
        self.logger.notifyChannel("transition", logger.LOG_INFO, 
                     'the <%s> to <%s>  has started now...'%(key.source.name, key.destination.name))          
        return True     

