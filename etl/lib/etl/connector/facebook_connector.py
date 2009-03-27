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
ETL Connectors:
* Facebook connector
"""
from etl.connector import connector

class facebook_connector(connector):    
    def __init__(self, facebook_uri, email, password=False, delay_time=20):
        super(facebook_connector, self).__init__()
        self.email = email
        self.delay_time = delay_time
        self.uid = False
        self.auth_token = False
        self.session = False
        self.api_key = '1673458a9d3ddaa8c6f888d7150da256'
        self.secret_key = '666197caab406752474bd0c6695a53f6'
        self.facebook_uri = facebook_uri
        self.facebook = False

    def open(self):
        from facebook import Facebook
        super(facebook_connector, self).open()
        self.facebook = Facebook(api_key=self.api_key, secret_key=self.secret_key)
        self.auth_token = self.facebook.auth.createToken()                       
        self.login(self.email)
        time.sleep(self.delay_time)
        self.session = f.auth.getSession()
        return self.facebook

    def login(self, email, password=False):
        from facebook import Facebook
        self.facebook.login(email)
    
   
  
    
