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

import paramiko
class AuthHandler (paramiko.AuthHandler):
    """
    Internal class to handle the mechanics of authentication.
    """
    def _parse_userauth_request(self, m):
        if not self.transport.server_mode:
            # er, uh... what?
            m = Message()
            m.add_byte(chr(MSG_USERAUTH_FAILURE))
            m.add_string('none')
            m.add_boolean(0)
            self.transport._send_message(m)
            return
        if self.authenticated:
            # ignore
            return
        username = m.get_string()
        service = m.get_string()
        method = m.get_string()
        self.transport._log(DEBUG, 'Auth request (type=%s) service=%s, username=%s' % (method, service, username))
        if service != 'ssh-connection':
            self._disconnect_service_not_available()
            return
        if (self.auth_username is not None) and (self.auth_username != username):
            self.transport._log(WARNING, 'Auth rejected because the client attempted to change username in mid-flight')
            self._disconnect_no_more_auth()
            return
        self.auth_username = username

        if method == 'none':
            result = self.transport.server_object.check_auth_none(username)
        elif method == 'password':
            changereq = m.get_boolean()
            password = m.get_string()
            try:
                password = password.decode('UTF-8')
            except UnicodeError:
                # some clients/servers expect non-utf-8 passwords!
                # in this case, just return the raw byte string.
                pass
            if changereq:
                # always treated as failure, since we don't support changing passwords, but collect
                # the list of valid auth types from the callback anyway
                self.transport._log(DEBUG, 'Auth request to change passwords (rejected)')
                newpassword = m.get_string()
                try:
                    newpassword = newpassword.decode('UTF-8', 'replace')
                except UnicodeError:
                    pass
                result = AUTH_FAILED
            else:
                result = self.transport.server_object.check_auth_password(username, password)
        elif method == 'publickey':
            sig_attached = m.get_boolean()
            keytype = m.get_string()
            keyblob = m.get_string()
            try:
                key = self.transport._key_info[keytype](Message(keyblob))
            except SSHException, e:
                self.transport._log(INFO, 'Auth rejected: public key: %s' % str(e))
                key = None
            except:
                self.transport._log(INFO, 'Auth rejected: unsupported or mangled public key')
                key = None
            if key is None:
                self._disconnect_no_more_auth()
                return
            # first check if this key is okay... if not, we can skip the verify
            result = self.transport.server_object.check_auth_publickey(username, key)
            if result != AUTH_FAILED:
                # key is okay, verify it
                if not sig_attached:
                    # client wants to know if this key is acceptable, before it
                    # signs anything...  send special "ok" message
                    m = Message()
                    m.add_byte(chr(MSG_USERAUTH_PK_OK))
                    m.add_string(keytype)
                    m.add_string(keyblob)
                    self.transport._send_message(m)
                    return
                sig = Message(m.get_string())
                blob = self._get_session_blob(key, service, username)
                if not key.verify_ssh_sig(blob, sig):
                    self.transport._log(INFO, 'Auth rejected: invalid signature')
                    result = AUTH_FAILED
        elif method == 'keyboard-interactive':
            lang = m.get_string()
            submethods = m.get_string()
            result = self.transport.server_object.check_auth_interactive(username, submethods)
            if isinstance(result, InteractiveQuery):
                # make interactive query instead of response
                self._interactive_query(result)
                return
        else:
            result = self.transport.server_object.check_auth_none(username)
        # okay, send result
        self._send_auth_result(username, method, result)
        

