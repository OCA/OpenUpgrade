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
To provide connectivity with Facebook

Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
GNU General Public License
"""
import datetime
import time
from etl.connector import connector

class facebook_connector(connector):
    """
    This is an ETL connector that use to provide connectivity with Facebook server.
    """
    def __init__(self, facebook_uri, email, password=False, delay_time=20,name='facebook_connector'):
        """
        Required Parameters ::
        facebook_uri: URI of Facebook server
        email       : Email Address of Facebook User
        Extra Parameters ::
        password    : Password
        delay_time  : Time in sec which is use to wait for login when open login page in browser
        name        : Name of connector
        """
        super(facebook_connector, self).__init__(name)
        self.email = email
        self.delay_time = delay_time
        self.uid = False
        self.api_key = '1673458a9d3ddaa8c6f888d7150da256' # TO CHECK
        self.secret_key = '666197caab406752474bd0c6695a53f6' # TO CHECK
        self.facebook_uri = facebook_uri

    def open(self):
        """
        Opens connection to facebook
        """
        from facebook import Facebook
        super(facebook_connector, self).open()
        facebook = Facebook(api_key=self.api_key, secret_key=self.secret_key)
        auth_token = facebook.auth.createToken()
        facebook.login(self.email)

        time.sleep(self.delay_time)
        session = facebook.auth.getSession()
        return facebook

    def execute(self,facebook,method,fields):
        """
        Required Parameters ::
        facebook : Facebook Object
        method   : Method name like
                    'get_user_info'=> Returns information of current user
                    'get_friends'=> Returns all the friends and its information for current user
                    'get_user_events'=> Returns all the events related to current user and members of events
                    'get_user_groups'=> Returns all the groups and its members
                    'get_user_notes'=> Returns notes created by user
                    'get_user_notification'=> Returns information on outstanding Facebook notifications for current session user
                    'get_user_profile'=> Returns the specified user's application info section for the calling application.
                    'get_user_pages'=> Returns all visible pages to the filters specified.
                    'get_user_photos'=> Returns all visible photos according to the filters specified.
                    'get_user_albums'=> Returns metadata about all of the photo albums uploaded by the specified user.
                    'get_user_status'=> Returns the user's current and most recent statuses
                    'get_user_links'=> Returns all links the user has posted on their profile through your application.
        fields  : Fields List
        """
        if method=='get_user_info':
            rows = facebook.users.getInfo(facebook.uid, fields)
        if method=='get_friends':
            friends = facebook.friends.get()
            friends.append(facebook.uid)
            rows = facebook.users.getInfo(friends, fields)
        if method=='get_user_events':
            rows_user = facebook.users.getInfo(facebook.uid, ['name'])
            rows = facebook.events.get(facebook.uid)
            map(lambda x:x.update({'user_name': rows_user[0]['name']}), rows)
#            for event in event_ids:# can be used
#                rows_member = facebook.events.getMembers(event)
        if method=='get_user_groups':
            rows = facebook.groups.get()
            group_ids = map(lambda x: x['gid'], rows)
            for group in group_ids:
                rows_member = facebook.groups.getMembers(group)
        # user notes => Beta
        if method=='get_user_notes':
            rows = facebook.notes.get(facebook.uid)
        if method=='get_user_notification':
            rows = facebook.notifications.get()
        if method=='get_user_profile':
            rows = facebook.profile.getInfo(facebook.uid)
        if method=='get_user_pages':
            rows = facebook.pages.getInfo(uid=facebook.uid, fields=['name','written_by']) #Todo : add more fields
        #  fields_pages = 'name', 'written_by', 'website', 'location (street, city, state, country, zip)', 'founded', 'products', 'produced_by'...etc

        # tobe test :  photos.get, photos.getAlbums, status.get , links.get
        if method=='get_user_photos':
            rows = facebook.photos.get(subj_id=facebook.uid)
        if method=='get_user_albums':
            rows = facebook.photos.getAlbums(uid=facebook.uid)
        if method=='get_user_status':# Beta
            rows = facebook.status.get()
        if method=='get_user_links':
            rows = facebook.links.get()

        if method=='set_events':# to be check
            perm = facebook.users.hasAppPermission(ext_perm='create_event')
            event_info = {"name":"Tinyerp Event","category":"1","subcategory":"1","host":"host","location":"location","city":"Palo Alto, CA","start_time":1215929160,"end_time":1215929160}
            event_id = facebook.events.create(event_info=event_info)
        return rows

    def __copy__(self):
        res=facebook_connector(self.facebook_uri, self.email, self.password, self.delay_time)

    def __copy__(self):
        """
        Overrides copy method
        """
        res=facebook_connector(self.facebook_uri, self.email, self.password, self.delay_time,self.name)

        return res

def test():
    """
    Test function
    """
    #TODO
    pass

if __name__ == '__main__':
    test()


