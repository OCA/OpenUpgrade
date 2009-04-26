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
 Defines ETL job with ETL output components

 Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). 
 GNU General Public License
"""
from signal import signal
import logger
import pickle

class job(signal):
    """
    Base class of ETL job.
    """ 
 
    def __init__(self,components=[],name='job'):        
        super(job, self).__init__()
        self.name=name
        self._components=components        
        for component in self._components:
            component.job=self   
        self.status='open' # open,start,pause,stop,close
        self.pickle=False
        self.logger=logger.logger()

    def __str__(self):           
        res='<Job name="%s">'%(self.name)
        components=[] 
        trans=[]
        for component in self.get_components():            
            res += "\n"+str(component)
        for transition in self.get_transitions():            
            res += "\n"+str(transition)         
        return res    
    
    def __copy__(self):
        """
        Copy job instance
        """
        new_outputs=[]
        new_transitions=[]
        new_components={}       
        for transition in self.get_transitions():
            new_tra=transition.copy()
            if transition.source not in new_components:
                new_components[transition.source]=transition.source.copy()                
            if transition.destination not in new_components:
                new_components[transition.destination]=transition.destination.copy()

            new_tra.source=new_components[new_tra.source]
            new_tra.destination=new_components[new_tra.destination]
            new_tra.destination.trans_in.append((new_tra.channel_destination,new_tra))
            new_tra.source.trans_out.append((new_tra.channel_source,new_tra))
            new_transitions.append(new_tra)

        res=job(new_components.values(), self.name+'(copy)')
        self.signal('copy')
        return res

    def copy(self):		
        return self.__copy__()

    def get_components(self):
        return self._components

    def add_component(self, component):
        self._componets.append(component)
        

    def get_transitions(self):
        transitions=[]
        for component in self._components:
            for channel,tran_in in component.trans_in:            
                if tran_in not in transitions:
                    transitions.append(tran_in)
            for channel,tran_out in component.trans_out:                
                if tran_out not in transitions:
                    transitions.append(tran_out)             
        return transitions
    
    def write(self):
        """
        Store job instance into pickle object
        """        
        return pickle.dumps(self)
        
    def read(self,value): 
        """
        Read job instance value from pickle object
        Parameter :
        value - pickle value  
        """     
        return pickle.load(value)
      
    def pause(self): 
        self.pickle=self.write()     
        for tran in self.get_transitions():
            tran.pause()
        self.status='pause'
        self.signal('pause')
        return self.pickle

    def restart(self):      
        for tran in self.get_transitions():
            tran.restart()           
        
        self.status='start'
        self.signal('restart') 

    def start(self):      
        self.register_actions()  
        self.status='start'            
        self.signal('start')
        for c in self.get_end_components():
            for a in c.channel_get():              
                pass 

    def end(self):
        self.status='end'
        self.signal('end')
        
        
    def open(self):
        self.status='open'

    def close(self):
        self.status='close'

    def stop(self):
        for tran in self.get_transitions():
            tran.stop()                
        self.status='stop'
        self.signal('stop')
          
    def get_end_components(self):
        end_components=[]
        for component in self.get_components():         
            if component.is_end():
                end_components.append(component)       
        return end_components

    

    def run(self):              
        if self.pickle:
            job=self.read(self.pickle)
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
        job.signal_connect(job,'start',self.action_job_start)
        job.signal_connect(job,'pause',self.action_job_pause)
        job.signal_connect(job,'stop',self.action_job_stop)
        job.signal_connect(job,'end',self.action_job_end)
        job.signal_connect(job,'copy',self.action_job_copy)

    def register_actions_component(self, component):        
        component.signal_connect(component, 'start', self.action_component_start)
        component.signal_connect(component, 'start_input', self.action_component_start_input)
        component.signal_connect(component, 'start_output', self.action_component_start_output)
        component.signal_connect(component, 'no_input', self.action_component_no_input)
        component.signal_connect(component, 'stop', self.action_component_stop)
        component.signal_connect(component, 'end', self.action_component_end)
        component.signal_connect(component, 'error', self.action_component_error)

    def register_actions_connector(self, connector):
        connector.signal_connect(connector, 'open', self.action_connector_open)
        connector.signal_connect(connector, 'close', self.action_connector_close)
        connector.signal_connect(connector, 'error', self.action_connector_error)


    def register_actions_transition(self, transition):        
        transition.signal_connect(transition,'start',self.action_transition_start)
        transition.signal_connect(transition,'pause',self.action_transition_pause)
        transition.signal_connect(transition,'stop',self.action_transition_stop)
        transition.signal_connect(transition,'end',self.action_transition_end)
    

    def action_job_start(self,key,signal_data={},data={}):              
        self.logger.notifyChannel("job", logger.LOG_INFO, 
                     'the <'+key.name+'> is start now...')
        return True
  
    def action_job_restart(self,key,signal_data={},data={}):          
        self.logger.notifyChannel("job", logger.LOG_INFO, 
                     'the <'+key.name+'> is start now...')
        return True

    def action_job_pause(self,key,signal_data={},data={}):      
        self.logger.notifyChannel("job", logger.LOG_INFO, 
                     'the <'+key.name+'> is pause now...')        
        return True

    def action_job_stop(self,key,signal_data={},data={}):
        self.logger.notifyChannel("job", logger.LOG_INFO, 
                     'the <'+key.name+'> is stop now...')    
        return True

    def action_job_end(self,key,signal_data={},data={}):      
        self.logger.notifyChannel("job", logger.LOG_INFO, 
                     'the <'+key.name+'> is end now...')              
        
        return True

    def action_job_copy(self,key,signal_data={},data={}):      
        self.logger.notifyChannel("job", logger.LOG_INFO, 
                     'the <'+key.name+'> is coping now...')
        return True

    def action_connector_open(self, key, signal_data={}, data={}):        
        self.logger.notifyChannel("connector", logger.LOG_INFO,
                     'the <'+key.name+'> is open now...')
        return True

    def action_connector_close(self, key, signal_data={}, data={}):
        self.logger.notifyChannel("connector", logger.LOG_INFO,
                    'the <'+key.name+'> is close now...')
        return True
    
    def action_connector_error(self, key, signal_data={}, data={}):
        self.logger.notifyChannel("connector", logger.LOG_ERROR,
                    '<'+key.name+'> : '+data.get('error',False))
        return True


    def action_component_start(self, key, signal_data={}, data={}):
        self.logger.notifyChannel("component", logger.LOG_INFO,
                     'the <'+key.name+'> is start now...')
        return True

    def action_component_start_input(self, key, signal_data={}, data={}):
        self.logger.notifyChannel("component", logger.LOG_INFO,
                     'the <'+key.name+'> is start to taken input...')
        return True

    def action_component_start_output(self, key, signal_data={}, data={}):
        self.logger.notifyChannel("component", logger.LOG_INFO,
                     'the <'+key.name+'> is start to give output...')
        return True

    def action_component_no_input(self, key, signal_data={}, data={}):
        self.logger.notifyChannel("component", logger.LOG_WARNING,
                     'the <'+key.name+'> has no input data...')
        return True

    def action_component_stop(self, key, signal_data={}, data={}):
        # TODO : stop all IN_trans and OUT_trans  related this component
        self.logger.notifyChannel("component", logger.LOG_INFO,
                     'the <'+key.name+'> is stop now...')
        return True



    def action_component_end(self, key, signal_data={}, data={}):
        self.logger.notifyChannel("component", logger.LOG_INFO,
                     'the <'+key.name+'> is end now...')
        return True


    def action_component_error(self, key, signal_data={}, data={}):
        self.logger.notifyChannel("component", logger.LOG_ERROR,
                     '<'+key.name+'> : '+signal_data.get('error','False'))        
        return True


    def action_transition_start(self,key,signal_data={},data={}):       
        self.logger.notifyChannel("transition", logger.LOG_INFO, 
                     'the <%s> to <%s>  is start now...'%(key.source.name,key.destination.name))
        return True 

    def action_transition_pause(self,key,signal_data={},data={}):       
        self.logger.notifyChannel("transition", logger.LOG_INFO, 
                     'the <%s> to <%s>  is start now...'%(key.source.name,key.destination.name))
        return True 

    def action_transition_stop(self,key,signal_data={},data={}):       
        self.logger.notifyChannel("transition", logger.LOG_INFO, 
                     'the <%s> to <%s>  is start now...'%(key.source.name,key.destination.name))
        return True 
  
    def action_transition_end(self,key,signal_data={},data={}):       
        self.logger.notifyChannel("transition", logger.LOG_INFO, 
                     'the <%s> to <%s>  is start now...'%(key.source.name,key.destination.name))     
        return True     







