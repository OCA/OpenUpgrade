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
This is an ETL Component that use to read data from facebook.

 Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). 
 GNU General Public License
"""

from etl.component import component
import time
class facebook_in(component):
    """
    This is an ETL Component that use to read data from facebook.

    Type: Data Component
    Computing Performance: Streamline
    Input Flows: 0
    * .* : nothing
    Output Flows: 0-x
    * .* : return the main flow with data
    """

    def __init__(self,facebook_connector,method,domain=[],fields=['name'],name='component.input.facebook_in',transformer=None,row_limit=0):
        super(facebook_in, self).__init__(name,transformer=transformer)
        self.facebook_connector = facebook_connector
        self.method=method
        self.domain=domain
        self.fields=fields
        self.row_limit=row_limit

    def process(self):        
        facebook=self.facebook_connector.open()
        rows=self.facebook_connector.execute(facebook,self.method,fields=self.fields)
        for row in rows:
            if self.transformer:
                row=self.transformer.transform(row)
            if row:
                yield row,'main'

# fields = ['uid', 'name', 'birthday', 'about_me', 'activities', 'affiliations', 'books', 'current_location', 'education_history', 'email_hashes', 'first_name','has_added_app', 'hometown_location', 'hs_info', 'hs_info', 'hs_info', 'hs_info', 'hs_info', 'meeting_for', 'meeting_sex', 'movies', 'music','notes_count', 'pic', 'pic_with_logo', 'pic_big', 'pic_big_with_logo', 'pic_small', 'pic_small_with_logo', 'pic_square', 'pic_square_with_logo','political', 'profile_update_time', 'profile_url', 'proxied_email', 'quotes', 'relationship_status', 'religion', 'sex', 'significant_other_id']

def test():
    from etl_test import etl_test
    import etl
    facebook_conn=etl.connector.facebook_connector('http://facebook.com', 'modiinfo@gmail.com')
    test1=etl_test.etl_component_test(facebook_in(facebook_conn,'get_user_events'))
    res=test1.output()

if __name__ == '__main__':
    pass
    #test()
