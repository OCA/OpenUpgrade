# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution	
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

import base64,paramiko
import pooler
from service import security

allowed_auths = 'publickey' # FIX

class Server (paramiko.ServerInterface):
    """ Implements an SSH server """        
    def check_channel_request(self, kind, chanid):
        """ Only allow session requests """
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED    

    def check_security(self, dbname, username, key):        
        db, cr, res = None, None, False
        try:            
            db = pooler.get_db_only(dbname)
            cr = db.cursor()
            cr.execute("SELECT 1 FROM pg_class WHERE relkind = 'r' AND relname = 'ir_module_module'")
            if not cr.fetchone():
                return False
            if allowed_auths == 'publickey':
                cr.execute("select distinct users.login,users.password,users.id from ir_module_module module,res_users users "+ \
                           "where module.name like 'document_sftp' and module.state='installed' "+ \
                           " and users.active=True and users.login='%s'"%(username))
                results = cr.fetchone()
                if results:
                    pool = pooler.get_pool(cr.dbname)
                    user = pool.get('res.users').browse(cr,results[2],results[2])
                    key_obj = pool.get('sftp.public.keys')
                    for k in user.ssh_key_ids:
                        user_pubkey = k.ssh_key
                        if user_pubkey: 
                            filekey = user_pubkey.split(' ')
                            if len(filekey)> 1:
                                user_pubkey = filekey[1]
                            else:
                                continue
                            custKey = paramiko.RSAKey(data=base64.decodestring(user_pubkey))
                            if custKey == key:
                                res = results[2]
                                break
                            else:
                                continue

            elif allowed_auths == 'password':
                cr.execute("select distinct users.login,users.password,users.id from ir_module_module module,res_users users "+ \
                           "where module.name like 'document%' and module.state='installed' "+ \
                           " and users.active=True and users.login='%s' and users.password='%s'"%(username,key))
                results = cr.fetchone()                 
                if results and results[1] == key:                                       
                    res = results[2]
            else:                    
                cr.execute("select distinct users.login,users.password,users.id from ir_module_module module, res_users users "+ \
                           "where module.name like 'document%' and module.state='installed' "+ \
                           " and users.active=True")
                if results:                    
                    res = results[2]                         
            
        finally:
            if cr is not None:
                cr.close()                        
        return res    

    def check_auth_publickey(self, username, key):
        """ Ensure proper authentication """ 
        self.username = username
        self.key = key         
        return paramiko.AUTH_SUCCESSFUL        

    def check_auth_password (self, username, password):
        self.username = username
        self.key = key 
        return paramiko.AUTH_SUCCESSFUL        

    def get_allowed_auths(self, username):
        """ Only allow public key authentication """        
        return allowed_auths
        # return 'publickey', 'password'
