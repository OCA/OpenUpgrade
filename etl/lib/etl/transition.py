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
ETL transition.

Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
GNU General Public License
"""
from signal import signal
import logger
class transition(signal):
    """
    Base class of ETL transition.
    """
    

    def action_start(self,key,signal_data={},data={}):       
        self.logger.notifyChannel("transition", logger.LOG_INFO, 
                     'the '+str(self)+' is start now...')
        return True 

    def action_pause(self,key,signal_data={},data={}):       
        self.logger.notifyChannel("transition", logger.LOG_INFO, 
                     'the '+str(self)+' is pause now...')
        return True 

    def action_stop(self,key,signal_data={},data={}):       
        self.logger.notifyChannel("transition", logger.LOG_INFO, 
                     'the '+str(self)+' is stop now...')
        return True 
  
    def action_end(self,key,signal_data={},data={}):       
        self.logger.notifyChannel("transition", logger.LOG_INFO, 
                     'the '+str(self)+' is end now...')        
        return True     

    def __str__(self):
        return '<Transition : '+str(self.source)+' to '+str(self.destination)+'>'

    def open(self):
        self.status='open'

    def close(self):
        self.status='close'

    def stop(self):
        self.status='stop'
        self.signal('stop')

    def pause(self):
        self.status='pause'
        self.signal('pause')

    def start(self):
        self.status='start'
        self.signal('start')
    

    def __init__(self, source, destination, channel_source='main', channel_destination='main', type='data',trigger=None):
        super(transition, self).__init__() 
        self.type = type
        self.trigger=trigger
        self.source = source
        self.destination = destination
        self.channel_source = channel_source
        self.channel_destination = channel_destination
        self.destination.trans_in.append((channel_destination,self))
        self.source.trans_out.append((channel_source,self))
        self.status='open' # open,close 
                           # open : active, close : inactive

        self.logger = logger.logger()
        self.signal_connect(self,'start',self.action_start)
        self.signal_connect(self,'pause',self.action_pause)
        self.signal_connect(self,'stop',self.action_stop)
        self.signal_connect(self,'end',self.action_end)

    def __copy__(self):                               
        res=transition(self.source,self.destination,self.channel_source, self.channel_destination, self.type)               
        return res

    def copy(self):
        return self.__copy__()





