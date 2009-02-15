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

    The module for ETL job.

"""
import signal
import logger
class job(signal.signal):
    """
       Base class of ETL job.
    """
    def action_start(self,key,signal_data={},data={}):
        self.status='start'        
        self.logger.notifyChannel("job", logger.LOG_INFO, 
                     'the '+str(self)+' is start now...')
        return True

    def action_pause(self,key,signal_data={},data={}):
        import_job(None)    
        for output in self.outputs:
            output.action_pause(self)      
        self.status='pause'
        self.logger.notifyChannel("job", logger.LOG_INFO, 
                     'the '+str(self)+' is pause now...')        
        return True

    def action_stop(self,key,signal_data={},data={}):                    
        export_job(None)
        for output in self.outputs:
            output.action_stop(self)        
        self.status='stop'
        self.logger.notifyChannel("job", logger.LOG_INFO, 
                     'the '+str(self)+' is stop now...')    
        return True

    def action_end(self,key,signal_data={},data={}):
        self.status='end'
        self.logger.notifyChannel("job", logger.LOG_INFO, 
                     'the '+str(self)+' is end now...')              
        
        return True

    def action_copy(self,key,signal_data={},data={}):
        #TODO : copy job process
        self.logger.notifyChannel("job", logger.LOG_INFO, 
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
        self.signal_connect(self,'end',self.action_end)
        self.signal_connect(self,'copy',self.action_copy)
        self.logger = logger.logger()
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
        self.signal('end')







