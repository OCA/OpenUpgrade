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
  To import data from vcard

  Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
  GNU General Public License
"""

from etl.component import component
import csv
#import vobject 

class vcard_in(component):

    def __init__(self,fileconnector,name='component.input.csv_in'):

	"""
	Parameters ::
	fileconnector : It is a required field and it provides  local file connector to connect with file.
	"""

        super(vcard_in, self).__init__(name)
        self.fileconnector = fileconnector
        self.fp=None
        self.reader=None

    def action_start(self,key,singal_data={},data={}):
        import vobject
        super(vcard_in, self).action_start(key,singal_data,data)
        self.fp=self.fileconnector.open('r')
        #self.reader=csv.DictReader(self.fp,**self.csv_params)
        self.s = "".join(self.fp.readlines())
        self.reader = vobject.readComponents(self.s)


    def action_end(self,key,singal_data={},data={}):
       
        super(vcard_in, self).action_end(key,singal_data,data)
        if self.fp:
            self.fp.close()
           
        if self.fileconnector:
            self.fileconnector.close()
    
    def process(self):
        try:
            while True:
                row={}
                data=self.reader.next()
                for d in data.contents:
                    row[unicode(d)]=eval('data.'+unicode(d)+'.value')                    
                yield row,'main'
        except IOError,e:
            self.action_error(e) 

