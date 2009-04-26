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

from etl.component import component

class gmail_in(component):

    def __init__(self, user, password, name='component.input.gmail_in', transformer=None, row_limit=0):
        """    
        Required  Parameters ::
        user     : user name 
        password : password of the user
        
        Extra Parameters ::
        name          : Name of Component.
        row_limit     : Limited records send to destination if row limit specified. If row limit is 0,all records are send.
        """

        super(gmail_in, self).__init__(name=name, transformer=transformer, row_limit=row_limit)
        self._type='component.input.gmail_in'        
        self.user=user
        self.pwd=password
        

    def __copy__(self):        
        res=gmail_in(self.user, self.password, self.name, self.transformer, self.row_limit)
        return res    
        
    
    def process(self):
        import gdata.contacts.service
        super(gmail_in, self).action_start(key, singal_data, data)
        connector = gdata.contacts.service.ContactsService()
        connector.ClientLogin(self.user, self.pwd)
        contacts_feed = connector.GetContactsFeed()        
        for feed in contacts_feed.entry:            
            emails=[]  
            phone_numbers=[]
            postal_addresses=[]        
            for email in feed.email:
                emails.append(email.address)
        
            for phone_number in feed.phone_number:
                phone_numbers.append(phone_number.text)
        
            for postal_address in feed.postal_address:
                postal_addresses.append(postal_address.text)
            d={
                'title':feed.title and feed.title.text or False, 
                'emails':emails, 
                'phone_numbers':phone_numbers, 
                'postal_addresses':postal_addresses
            }
            yield d, 'main'
        
    
    
def test():
    from etl_test import etl_test
    import etl
    user = raw_input('Enter gmail username: ')
    user = user + '@gmail.com'
    password = raw_input('Enter correct password for user %s: ' % user)
    test=etl_test.etl_component_test(gmail_in(user, password))
    res=test.output()
    
    
if __name__ == '__main__':
    test()

