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
 Puts job process in sleep.

 Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). 
 GNU General Public License

"""
from etl.component import component
import time

class sleep(component):
    """
       put job process in sleep.
    """
    def __init__(self, delay=1,name='component.control.sleep'):
        """ 
        Parametrs ::
        delay          : Delay in Seconds 
        name          : Name of Component. 
        """
        self.delay = delay
        self.name = name
        super(sleep, self).__init__(name)

    def process(self):
        for channel,trans in self.input_get().items():
            for iterator in trans:
                for d in iterator:
                    time.sleep(self.delay)
                    yield d, 'main'


    def __copy__(self):
        """
        Overrides copy method
        """
        res=sleep(self.delay, name=self.name)
        return res
