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

Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
GNU General Public License
"""
from etl import signal
from etl import logger
import datetime
class connector(signal):
    """
    Base class of ETL Connector.
    """
    def action_open(self, key, signal_data={}, data={}):
        """
        Parameters::
        key :  Provides Key for connector
        signal_data   :  Data sent by signal
        data     :  Other common data between all methods
        """
        self.logger.notifyChannel("connector", logger.LOG_INFO,
                     'the '+str(self)+' is open now...')
        return True

    def action_close(self, key, signal_data={}, data={}):
        """
        Parameters::
        key :  Provides Key for connector
        signal_data   :  Data sent by signal
        data     :  Other common data between all methods
        """
        self.logger.notifyChannel("connector", logger.LOG_INFO,
                    'the '+str(self)+' is close now...')
        return True
    def action_error(self, key, signal_data={}, data={}):
        """
        Parameters::
        key :  Provides Key for connector
        signal_data   :  Data sent by signal
        data     :  Other common data between all methods
        """
        self.logger.notifyChannel("connector", logger.LOG_ERROR,
                    str(self)+' : '+data.get('error',False))
        return True

    def __init__(self,name='connector'):
        """
        Parameters::
        name :  Name of the connector
        """
        super(connector, self).__init__()
        self.name=name
        self.logger = logger.logger()

        self.status = 'close'
        self.signal_connect(self, 'open', self.action_open)
        self.signal_connect(self, 'close', self.action_close)

    def open(self):
        self.status='open'
        self.signal('open')
    def close(self,connector=False):
        """
        Parameters::
        connector :  Connector that is to be closed
        """
        self.status='close'
        self.signal('close')

    def __copy__(self):
        """
        Overrides copy method
        """
        res=connector(name=self.name)
        return res

    def execute(self):
        return True

    def __str__(self):
        if not self.name:
            self.name=''
    	return '<Connector : '+self.name+'>'
    
