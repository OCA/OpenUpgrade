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
ETL Connector.
"""
from etl import signal
from etl import logger
import datetime
class connector(signal):
    """
    Base class of ETL Connector.
    """
    def action_open(self, key, signal_data={}, data={}):
        self.logger.notifyChannel("connector", logger.LOG_INFO, 
                     'the '+str(self)+' is open now...')
        return True
    def action_close(self, key, signal_data={}, data={}):
        self.logger.notifyChannel("connector", logger.LOG_INFO, 
                    'the '+str(self)+' is close now...')
        return True
    def action_error(self, key, signal_data={}, data={}):
        self.logger.notifyChannel("connector", logger.LOG_ERROR, 
                    str(self)+' : '+data.get('error',False))
        return True
    def __init__(self,name='connector'): 
        super(connector, self).__init__()  
        self.name=name     
        self.connector=None  
        self.logger = logger.logger()
        
        self.signal_connect(self, 'open', self.action_open)
        self.signal_connect(self, 'close', self.action_close)    
    def open(self):
        self.signal('open')
    def close(self):
        self.signal('close') 
    def execute(self):
        pass   
    def __str__(self):        
        if not self.name:
            self.name=''
    	return '<Connector : '+self.name+'>'
    
