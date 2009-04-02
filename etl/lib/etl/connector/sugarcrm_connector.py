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
#from sugarcrm.sugarsoap_services_types import *
#from sugarcrm.sugarsoap_services import *
class sugarcrm_connector(connector):
    """
    This is an ETL connector that use to provide connectivity with SugarCRM server.
    """
    def __init__(self, username, password, url='http://localhost/sugarcrm', encoding='utf-8', name='sugarcrm_connector'):
        """ 
        Required Parameters ::
        username: Userid of SugarCRM server
        password: Password 
        Extra Parameters ::
        url     : URL of SugarCRM server
        encoding: Encoding format
        name    : Name of connector
        """
        super(sugarcrm_connector, self).__init__(name)
        self.url=url                
        self.username = username
        self.password = password
        self.encoding=encoding


    def open(self):        
        super(sugarcrm_connector, self).open()
        
        loc = sugarsoapLocator();
        request = loginRequest();
        uauth = ns0.user_auth_Def(request);
        request._user_auth = uauth;
        uauth._user_name = self.username;
        uauth._password = md5.new(self.password).hexdigest();
        uauth._version = '1.1';
        portType = loc.getsugarsoapPortType(self.url);
        response = portType.login(request);
        if -1 == response._return._id:
            raise LoginError(response._return._error._description);
        return (portType, response._return._id);

    def search(self, portType, session_id, module, offset=0, row_limit=0, query=None):        
        se_req = get_entry_listRequest()
        se_req._session =session_id;
        se_req._module_name =module
        se_req._offset = offset;
        se_req._max_results = row_limit;
        #se_req._order_by = 'id';
        if query != None:
            se_req._query = query;
        #end if
        se_resp = portType.get_entry_list(se_req);
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

    def edit(self, portType, session_id, module, values):        
        gui_req = get_user_idRequest();
        gui_req._session = session_id;
        user_id =portType.get_user_id(gui_req)._return;

        se_req = set_entryRequest();
        se_req._session = session_id;
        se_req._module_name =module;
        se_req._name_value_list = [];
        name =[];

        for (n, v) in values:
            nvl = ns0.name_value_Def('name_value');
            nvl._name = n;
            nvl._value = v;
            se_req._name_value_list.append(nvl);
        #end for
        se_resp = portType.set_entry(se_req);
        account_id = se_resp._return._id;
        return account_id;

    def close(self, connector):  
        super(sugarcrm_connector, self).close()          
        return connector.close()

    def __copy__(self): 
        res=sugarcrm_connector(self.username, self.password, self.url, self.encoding, self.name)
        return res

def test():    
    #TODO
    pass

if __name__ == '__main__':
    test()
