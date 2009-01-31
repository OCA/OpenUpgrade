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
   This is ETL Component to put job process in sleep.
"""
from etl import etl
import time

class sleep(etl.component):
    """
       put job process in sleep.
    """
    _name='etl.component.control.sleep'  
    _description='This is ETL Component to put job process in sleep.'   
    _author='tiny'

    def __init__(self, delay=1, *args, **argv):
        self.delay = delay
        super(sleep, self).__init__(*args, **argv)

    def process(self):
        for channel,trans in self.input_get().items():
            for iterator in trans:
                for d in iterator:
                    time.sleep(self.delay)
                    yield d, 'main'
            for stat in self.statitics.values():                
                yield stat,'statistics'  
	        for error in self.errors:                
	            yield error,'error'

