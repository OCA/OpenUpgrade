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

from etl.connector import connector
class sugarcrm_connector(connector):
    def __init__(self,username,password,url='http://localhost/sugarcrm',encoding='utf-8'):
        super(sugarcrm_connector, self).__init__()
        self.url=url
        self.request = False
        self.uauth = False
        self.sessionid=False
        self.username = username
        self.password = password
        self.encoding=encoding


    def open(self):
        super(sugarcrm_connector, self).open()
        from sugarcrm.sugarsoap_services_types import *
        from sugarcrm.sugarsoap_services import *
        self.loc = sugarsoapLocator();
        self.request = loginRequest();
        self.uauth = ns0.user_auth_Def(self.request);
        self.request._user_auth =self. uauth;
        self.uauth._user_name = self.username;
        self.uauth._password = md5.new(self.password).hexdigest();
        self.uauth._version = '1.1';
        self.portType = self.loc.getsugarsoapPortType(self.url);
        (self.portType,self.sessionid)=self.login()
        return self.connector

    def login(self):
        from sugarcrm.sugarsoap_services_types import *
        from sugarcrm.sugarsoap_services import *
        self.response = self.portType.login(self.request);
        if -1 == self.response._return._id:
            raise LoginError(self.response._return._error._description);
        return (self.portType, self.response._return._id);

    def search(self,module,search=None):
        from sugarcrm.sugarsoap_services_types import *
        from sugarcrm.sugarsoap_services import *
        se_req = get_entry_listRequest()
        se_req._session =self.response._return._id;
        se_req._module_name ='Contacts'
        se_req._offset = 0;
        se_req._max_results = 20;
        #se_req._order_by = 'id';
        if search != None:
            se_req._query = search;
        #end if
        se_resp = self.portType.get_entry_list(se_req);
        list = se_resp._return._entry_list;

        ans_list = [];

        for i in list:
            ans_dir = {};
            for j in i._name_value_list:
                ans_dir[j._name.encode(self.encoding)] = j._value.encode(self.encoding)
            #end for
            ans_list.append(ans_dir);
        #end for
        return ans_list;

    def edit(self,module,values):
        from sugarcrm.sugarsoap_services_types import *
        from sugarcrm.sugarsoap_services import *
        gui_req = get_user_idRequest();
        gui_req._session = self.response._return._id;
        user_id =self.portType.get_user_id(gui_req)._return;

        se_req = set_entryRequest();
        se_req._session = self.response._return._id;
        se_req._module_name =module;
        se_req._name_value_list = [];
        name =[];

        for (n, v) in values:
            nvl = ns0.name_value_Def('name_value');
            nvl._name = n;
            nvl._value = v;
            se_req._name_value_list.append(nvl);
        #end for
        se_resp = self.portType.set_entry(se_req);
        account_id = se_resp._return._id;
        return account_id;
