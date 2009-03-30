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

    """

    def __init__(self,facebook_connector,method,domain=[],fields=['name'],name='component.input.facebook_in',transformer=None,row_limit=0):
        super(facebook_in, self).__init__(name,transformer=transformer)
        self.facebook_connector = facebook_connector
        self.method=method
        self.domain=domain
        self.fields=fields
        self.row_limit=row_limit
        self.facebook = False

    def action_start(self,key,singal_data={},data={}):
        super(facebook_in, self).action_start(key,singal_data,data)
        self.facebook=self.facebook_connector.open()


    def action_end(self,key,singal_data={},data={}):
        super(facebook_in, self).action_end(key,singal_data,data)
        if self.facebook_connector:
            self.facebook_connector.close()
            self.facebook=False

    def process(self):
        rows=[]
        if self.method=='get_user_info':
            rows = self.facebook.users.getInfo(self.facebook.uid, self.fields)
        if self.method=='get_friends':
            friends = self.facebook.friends.get()
            rows = self.facebook.users.getInfo(friends, self.fields)
        if self.method=='get_user_events':
            rows = self.facebook.events.get(self.facebook.uid)
            for event in event_ids:# can be used
                rows_member = self.facebook.events.getMembers(event)
        if self.method=='get_user_groups':
            rows = self.facebook.groups.get()
            group_ids = map(lambda x: x['gid'], rows)
            for group in group_ids:
                rows_member = self.facebook.groups.getMembers(group)
        # user notes => Beta
        if self.method=='get_user_notes':
            rows = self.facebook.notes.get(self.facebook.uid)
        if self.method=='get_user_notification':
            rows = self.facebook.notifications.get()
        if self.method=='get_user_profile':
            rows = self.facebook.profile.getInfo(self.facebook.uid)
        if self.method=='get_user_pages':
            rows = self.facebook.pages.getInfo(uid=self.facebook.uid, fields=['name','written_by']) #Todo : add more fields
        #  fields_pages = 'name', 'written_by', 'website', 'location (street, city, state, country, zip)', 'founded', 'products', 'produced_by'...etc

        # tobe test :  photos.get, photos.getAlbums, status.get , links.get
        if self.method=='get_user_photos':
            rows = self.facebook.photos.get(subj_id=self.facebook.uid)
        if self.method=='get_user_albums':
            rows = self.facebook.photos.getAlbums(uid=self.facebook.uid)
        if self.method=='get_user_status':# Beta
            rows = self.facebook.status.get()
        if self.method=='get_user_links':
            rows = self.facebook.links.get()

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
