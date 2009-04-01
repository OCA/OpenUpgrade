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
 To read data from csv file.

 Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). 
 GNU General Public License
"""


from etl.component import component
import csv


class csv_in(component):
    """
        This is an ETL Component that use to read data from csv file.Its type is data component.
	Its computing peformance is streamline.It has two flows ::
        Input Flows: 0
        * .* : nothing
        Output Flows: 0-x
        * .* : return the main flow with data from csv file
    """

    def __init__(self, fileconnector, name='component.input.csv_in', transformer=None, row_limit=0, csv_params={}):

	
	"""	
        Parameters::
	fileconnector :  provides  localfile connector to connect with file
	transformer   :  provides transformer object to transform string data into  particular object
	row_limit     :  Limited records send to destination if row limit specified. If row limit is 0,all records are send.
	csv_param     :  To specify other csv parameter like fieldnames , restkey , restval etc. 

	"""
        super(csv_in, self).__init__(name, transformer=transformer)
        self.name = name
        self.transformer = transformer
        self.fileconnector = fileconnector
        self.csv_params=csv_params
        self.row_limit=row_limit
        self.fp=None
        self.reader=None

    def action_start(self, key, singal_data={}, data={}):
        super(csv_in, self).action_start(key, singal_data, data)
        self.row_count=0
        self.fp=self.fileconnector.open()
        self.reader=csv.DictReader(self.fp, **self.csv_params)

    def action_end(self, key, singal_data={}, data={}):
        super(csv_in, self).action_end(key, singal_data, data)
        if self.fp:
             self.fp.close()
        if self.fileconnector:
             self.fileconnector.close()

    def process(self):
        try:
            for data in self.reader:
                self.row_count+=1
                if self.row_limit and self.row_count > self.row_limit:
                     raise StopIteration
                if self.transformer:
                    data=self.transformer.transform(data)
                if data:
                    yield data, 'main'


        except TypeError, e:
            self.action_error(e)
        except IOError, e:
            self.action_error(e)

    def __copy__(self):
        """
        Overrides copy method
        """
        res= csv_in(self.fileconnector , self.name, self.transformer, self.row_limit, self.csv_params)
        return res
    
def test():
    from etl_test import etl_test
    import etl
    file_conn=etl.connector.file_connector('http://localhost:8069', 'dms_20090204', 'admin', 	
    'admin', con_type='xmlrpc')
    test=etl_test.etl_component_test(csv_in('test', file_conn, 'res.partner'))
    test.check_input({'main':[{'name':'OpenERP1'}, {'name':'Fabien1'}]})
    test.check_output([{'name':'OpenERP1'}, {'name':'Fabien1'}], 'main')
    res=test.output()
    print res
if __name__ == '__main__':
	test()


