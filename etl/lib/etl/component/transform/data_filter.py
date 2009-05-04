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
Data filter component.
"""

from etl.component import component
import datetime

class data_filter(component):
    """
        Data filter component.
    """

    def __init__(self, filter_criteria, name='component.transfer.data_filter', transformer=None, row_limit=0):

        """
        Required Parameters
        filter_criteria  : Dictionary of filtering criteria.

        Extra Parameters
        name             : Name of component.
        transformer      : Transformer object to transform string data into particular type.
        """
        super(data_filter, self).__init__(name=name, transformer=transformer,row_limit=row_limit)
        self._type = 'component.transfer.data_filter'
        self.filter_criteria = filter_criteria

    def __copy__(self):
        res = data_filter(self.filter_criteria, self.name, self.transformer, self.row_limit)
        return res

    def process(self):
        datas = []
        for channel, trans in self.input_get().items():
            for iterator in trans:
                for d in iterator:
                    if self.transformer:
                        d = self.transformer.transform(d)
                    filter = ''
                    for filter_data in self.filter_criteria:
                         val = d[filter_data['name']]
                         _filter = filter_data.get('filter', False)
                         if val and _filter:
                             val = eval((_filter) % d)
                         filter += " %s %s %s %s" % (repr(val), filter_data['operator'], filter_data['operand'], filter_data.get('condition', ''))
                    if self.transformer:
                        d = self.transformer.transform(d)
                    if eval(filter):
                       yield d, 'main'
                    else:
                       yield d, 'invalid'
def test():
    from etl_test import etl_test
    from etl import transformer
    import etl
    openobject_partner=etl.connector.openobject_connector('http://localhost:8869', 'trunk', 'admin', 'admin',con_type='xmlrpc')
    transformer_description= {'title':transformer.STRING,'name':transformer.STRING,'street':transformer.STRING,'street2':transformer.STRING,'birthdate':transformer.DATE}
    transformer=transformer(transformer_description)
    openobject_in1= etl.component.input.openobject_in(
                 openobject_partner,'res.partner.address',
                 fields=['partner_id','title', 'name', 'street', 'street2' , 'phone' , 'city' ,  'zip' ,'state_id' , 'country_id' , 'mobile', 'birthdate'],
                 transformer=transformer)
    filter_criteria=[
        {'name':'Partner','filter':'"%(Partner)s".lower() or ""','operator':'==','operand':"'leclerc'",'condition':'or'},
        {'name':'Address Name','operator':'==','operand':"'Fabien Pinckaers'"}
        ]

    test1 = data_filter_component=etl_test.etl_component_test(etl.component.transform.data_filter(filter_criteria,transformer=transformer))
    res = test1.output()
    print res
if __name__ == '__main__':
    test()

