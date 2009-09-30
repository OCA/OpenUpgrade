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

from osv import osv, fields

class sftp_public_keys(osv.osv):
    _name = 'sftp.public.keys'
    _description = "Public Keys"
    _rec_name = 'ssh_key'
    _columns = {
        'ssh_key': fields.text('SSH Public key'),
        'user_id' : fields.many2one('res.users', 'User')
    }    
    
sftp_public_keys()

class res_users(osv.osv):
    _name = 'res.users'
    _inherit = 'res.users'    
    _columns = {
        'ssh_key_ids': fields.one2many('sftp.public.keys', 'user_id', 'SSH Public key'),
    }    
res_users()
