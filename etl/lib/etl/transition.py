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
 GNU General Public License.
"""
from signal import signal
import datetime
import pickle
class transition(signal):
    """
    Base class of ETL transition.
    """
    def __init__(self, source, destination, channel_source='main', channel_destination='main', type='data', trigger=None):
        super(transition, self).__init__()            
        self.type = type
        self.trigger = trigger
        self.source = source
        self.destination = destination
        self.channel_source = channel_source
        self.channel_destination = channel_destination
        self.destination.trans_in.append((channel_destination, self))
        self.source.trans_out.append((channel_source, self))
        self.status = 'open' # open,close # open : active, close : inactive
        
    def __str__(self):
        return "<Transition source='%s' destination='%s' channel_source='%s' channel_destination='%s' type='%s' trigger='%s' status='%s'>" \
                %(self.source.name, self.destination.name, self.channel_source, self.channel_destination, self.type, self.trigger, self.status)

    def __copy__(self):             
        res = transition(self.source, self.destination, self.channel_source, self.channel_destination, self.type)               
        return res  

    def __getstate__(self):        
        return {'type' : self.type,'status' : self.status, 'source' : pickle.dumps(self.source), 'destination': pickle.dumps(self.destination), 'trigger' : self.trigger, 'channel_source' : self.channel_source, 'channel_destination' : self.channel_destination}

    def __setstate__(self, state):
        source = pickle.loads(state['source'])
        destination = pickle.loads(state['destination'])
        destination.__dict__['trans_in'].append((state['channel_destination'],self))
        source.__dict__['trans_out'].append((state['channel_source'],self))
        state['source'] = source
        state['destination'] = destination
        self.__dict__ = state

    def copy(self):
        return self.__copy__()   

    def open(self):
        self.status = 'open'

    def close(self):
        self.status = 'close'

    def stop(self):
        #self.status = 'stop'
        self.signal('stop')

    def end(self):
        #self.status = 'end'
        self.signal('end', {'date': datetime.datetime.today()})

    def start(self):
        #self.status = 'start'
        self.signal('start', {'date': datetime.datetime.today()})

    def pause(self):
        #self.status = 'pause'
        self.signal('pause')    

    def restart(self):
        #self.status = 'start'
        self.signal('restart')
