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
 GNU General Public License.
"""
from etl import signal
import datetime
class connector(signal):
    """
    Base class of ETL Connector.
    """   

    def __init__(self,name='connector'):
        """
        Parameters 
        name : Name of the connector.
        """
        self._type = 'connector'
        super(connector, self).__init__()
        self.name = name or ''
        self.status = 'close'        

    def __copy__(self):       
        res = connector(name=self.name)
        return res

    def __str__(self):        
    	return '<Connector name = "%s" type = "%s">'%(self.name, self._type)

    def __getstate__(self):
        return {'name' : self.name, 'status': self.status , '_type' :self._type}

    def __setstate__(self, state):
        self.__dict__ = state

    def open(self):
        self.status = 'open'
        self.signal('open', {'date': datetime.datetime.today()})

    def close(self, connector=False):
        """
        Parameters
        connector : Connector that is to be closed.
        """
        self.status = 'close'
        self.signal('close', {'date': datetime.datetime.today()})

    def execute(self):
        return True

