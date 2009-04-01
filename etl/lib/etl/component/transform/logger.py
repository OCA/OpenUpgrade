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
 To display log detail in streamline.

 Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). 
 GNU General Public License
"""

from etl.component import component
import sys
class logger(component):
    """
        This is an ETL Component that use to display log detail in streamline.
 
	    Type: Data Component
		Computing Performance: Streamline
		Input Flows: 0-x
		* .* : the main data flow with input data
		Output Flows: 0-y
		* .* : return the main flow 
    """    
    def __init__(self, name='component.output.logger', output=sys.stdout):        
        self.output = output
        self.is_end = 'main'
        super(logger, self).__init__(name)

    def process(self):
        #TODO : proper handle exception
        for channel,trans in self.input_get().items():
            for iterator in trans:
                for d in iterator:                    
                    self.output.write('Log '+self.name+' '+str(d)+'\n')
                    yield d, 'main'
        super(logger, self).process()

        
    def __copy__(self):
        """
        Overrides copy method
        """
        res=logger(self.name, self.output)
        return res
    
