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
This is an ETL Component that is used to read data from facebook.

 Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
 GNU General Public License.
"""

from etl.component import component

class facebook_in(component):
    """
    This is an ETL Component that is used to read data from facebook.

    Type                  : Data Component.
    Computing Performance : Streamline.
    Input Flows           : 0.
    * .*                  : Nothing.
    Output Flows          : 0-x.
    * .*                  : Returns the main flow with data.
    """

    def __init__(self, facebook_connector, method, domain=[], fields=['name'], name='component.input.facebook_in', transformer=None, row_limit=0):
        """ 
        Required  Parameters 
        facebook_connector : Facebook connector.
        method             : Name of the method which is going to be called to connector to fetch data from facebook.
        domain             : Domain List to put domain.
        fields             : Fields List.
        
        Extra Parameters 
        name               : Name of Component.
        transformer        : Transformer object to transform string data into  particular object.
        row_limit          : Limited records are sent to destination if row limit is specified. If row limit is 0, all records are sent.
        """
        super(facebook_in, self).__init__(name=name, connector=facebook_connector, transformer=transformer, row_limit=row_limit)        
        self._type = 'component.input.facebook_in'
        self.method = method
        self.domain = domain
        self.fields = fields
       
    def __copy__(self):        
        res = facebook_in(self.connector, self.method, self.domain, self.fields, self.name, self.transformer, self.row_limit)
        return res

    def process(self):        
        facebook = self.connector.open()
        rows = self.connector.execute(facebook, self.method, fields=self.fields)
        for row in rows:           
            if row:
                yield row, 'main'

# fields = ['uid', 'name', 'birthday', 'about_me', 'activities', 'affiliations', 'books', 'current_location', 'education_history', 'email_hashes', 'first_name','has_added_app', 'hometown_location', 'hs_info', 'hs_info', 'hs_info', 'hs_info', 'hs_info', 'meeting_for', 'meeting_sex', 'movies', 'music','notes_count', 'pic', 'pic_with_logo', 'pic_big', 'pic_big_with_logo', 'pic_small', 'pic_small_with_logo', 'pic_square', 'pic_square_with_logo','political', 'profile_update_time', 'profile_url', 'proxied_email', 'quotes', 'relationship_status', 'religion', 'sex', 'significant_other_id']

def test():
    from etl_test import etl_test
    import etl
    facebook_conn = etl.connector.facebook_connector('http://facebook.com', 'modiinfo@gmail.com')
    test1 = etl_test.etl_component_test(facebook_in(facebook_conn, 'get_user_events'))
    res = test1.output()

if __name__ == '__main__':
    pass
    #test()
