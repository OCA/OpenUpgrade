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
This is an ETL Component that writes data to gmail contacts.
"""

from etl.component import component
from etl.connector import openobject_connector

class gmail_out(component):
    """
    This is an ETL Component that writes data to gmail contacts.
    """

    def __init__(self, user, password, data={}, name='component.output.gmail_out', transformer=None, row_limit=0):
        super(gmail_out, self).__init__(name=name, transformer=transformer, row_limit=row_limit)
        self._type = 'component.output.gmail_out'
        self.user = user
        self.pwd = password
        self.data = data

    def __copy__(self):
        res = gmail_out(self.user, self.password, self.name, self.transformer, self.row_limit)
        return res

    def end(self):
        super(gmail_out, self).end()

    def __getstate__(self):
        res = super(gmail_out, self).__getstate__()
        res.update({'user':self.user, 'pwd':self.pwd})
        return res

    def __setstate__(self, state):
        super(gmail_out, self).__setstate__(state)
        self.__dict__ = state

    def process(self):
        import gdata.contacts.service
        import atom

        connector = gdata.contacts.service.ContactsService()
        connector.ClientLogin(self.user, self.pwd)
        res={}
#        res = self.data
        for channel, trans in self.input_get().items():
            for iterator in trans:
                for d in iterator:
                    new_contact = gdata.contacts.ContactEntry(title=atom.Title(text=d['name']))
                    email_address = d['email']
                    if email_address:
                        new_contact.email.append(gdata.contacts.Email(address=email_address, primary='true', rel=gdata.contacts.REL_WORK))

                    phone_number = d['phone']
                    if phone_number:
                        new_contact.phone_number.append(gdata.contacts.PhoneNumber(text=phone_number))

                    contact_entry = connector.CreateContact(new_contact)
                    d.update({'gmail':contact_entry})
                    yield d, 'main'

#        for d in res['main']:
#            new_contact = gdata.contacts.ContactEntry(title=atom.Title(text=d['name']))
#            email_address = d['email']
#            if email_address:
#                new_contact.email.append(gdata.contacts.Email(address=email_address, primary='true', rel=gdata.contacts.REL_WORK))
#
#            phone_number = d['phone']
#            if phone_number:
#                new_contact.phone_number.append(gdata.contacts.PhoneNumber(text=phone_number))
#
#            contact_entry = connector.CreateContact(new_contact)
#            yield contact_entry, 'main'

def test():
    from etl_test import etl_test
    import etl
    import getpass
    user = raw_input('Enter gmail username: ')
    user = user + '@gmail.com'
    password = getpass.unix_getpass("Enter your password:")

    ooconnector=openobject_connector('http://localhost:8069', 'quality', 'admin', 'admin',con_type='xmlrpc')
    oo_in_event = etl_test.etl_component_test(etl.component.input.openobject_in(
                     ooconnector,'res.partner.address',
                     fields=['name', 'email', 'phone'],
    ))
    res = oo_in_event.output()

    test = etl_test.etl_component_test(gmail_out(user, password,res))

#    test.check_output([{'phone_numbers': [''], 'postal_addresses': [''], 'emails': [''], 'title': ''}], 'main')
    # here add the details of the contact in your gmail in the above mentioned format
    res = test.output()
#    print res

if __name__ == '__main__':
    test()
