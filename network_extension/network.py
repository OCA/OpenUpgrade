# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2008 Zikzakmedia S.L. (http://zikzakmedia.com) All Rights Reserved.
#                       Jordi Esteve <jesteve@zikzakmedia.com>
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

import time
from osv import fields, osv
import base64
from tools.translate import _

#--------------------------------------------------------------
# A network is composed of all kind of networkable materials
#--------------------------------------------------------------
class network_network(osv.osv):
    _inherit = "network.network"
    _columns = {
        'gateway': fields.char('Gateway', size=100),
        'dns': fields.char('DNS', size=100, help="List of DNS servers, separated by commas"),
        'public_ip_address': fields.char('Public IP address', size=100),
        'public_domain': fields.char('Public domain', size=100),
    }
network_network()


#----------------------------------------------------------
# A software installed on a material
#----------------------------------------------------------
class network_software(osv.osv):
    _inherit = "network.software"
    _columns = {
        'type': fields.many2one('network.software.type',
                                'Software Type', required=True, select=1),
        'service_ids': fields.one2many('network.service', 'software_id', string='Service'),
    }

    def _default_material(self, cursor, user, context=None):
        if not context.get('material_id', False):
            return False
        value = context['material_id']
        return value

    _defaults = {
        'material_id': lambda obj, cursor, user, context: obj._default_material(cursor, user, context=context),
    }
network_software()


#------------------------------------------------------------
# Couples of login/password
#------------------------------------------------------------
class network_software_logpass(osv.osv):
    _inherit = "network.software.logpass"
    _columns = {
        'name': fields.char('Name', size=100),
        'note': fields.text('Note'),
        'material': fields.related('software_id', 'material_id', type='many2one', relation='network.material', string='Material', readonly=True),
        'encrypted': fields.boolean('Encrypted'),
    }

    _defaults = {
        'encrypted': lambda obj, cursor, user, context: False,
    }

    def onchange_password(self, cr, uid, ids, encrypted, context={}):
        return {'value':{'encrypted': False}}


    def _encrypt_password(self, cr, uid, ids, *args):
        for rec in self.browse(cr, uid, ids):
            try:
                from Crypto.Cipher import ARC4
            except ImportError:
                raise osv.except_osv(_('Error !'), _('Package python-crypto no installed.'))

            if not rec.encrypted:
                obj_encrypt_password = self.pool.get('network.encrypt.password')
                encrypt_password_ids = obj_encrypt_password.search(cr, uid, [('create_uid','=',uid),('write_uid','=',uid)])
                encrypt_password_id = encrypt_password_ids and encrypt_password_ids[0] or False
                if encrypt_password_id:
                    passwordkey = obj_encrypt_password.browse(cr, uid, encrypt_password_id).name
                    enc = ARC4.new(passwordkey)
                    try:
                        encripted = base64.b64encode(enc.encrypt(rec.password))
                    except UnicodeEncodeError:
                        break
                    self.write(cr, uid, [rec.id], {'password': encripted, 'encrypted': True})
                else:
                    raise osv.except_osv(_('Error !'), _('Not encrypt/decrypt password has given.'))
        return True


    def _decrypt_password(self, cr, uid, ids, *args):
        for rec in self.browse(cr, uid, ids):
            try:
                from Crypto.Cipher import ARC4
            except ImportError:
                raise osv.except_osv(_('Error !'), _('Package python-crypto no installed.'))

            if rec.encrypted:
                obj_encrypt_password = self.pool.get('network.encrypt.password')
                encrypt_password_ids = obj_encrypt_password.search(cr, uid, [('create_uid','=',uid),('write_uid','=',uid)])
                encrypt_password_id = encrypt_password_ids and encrypt_password_ids[0] or False
                if encrypt_password_id:
                    passwordkey = obj_encrypt_password.browse(cr, uid, encrypt_password_id).name
                    dec = ARC4.new(passwordkey)
                    try:
                        desencripted = dec.decrypt(base64.b64decode(rec.password))
                        unicode(desencripted, 'ascii')
                        raise osv.except_osv(rec.login+_(' password:'), desencripted)
                    except UnicodeDecodeError:
                        raise osv.except_osv(_('Error !'), _('Wrong encrypt/decrypt password.'))
                else:
                    raise osv.except_osv(_('Error !'), _('Not encrypt/decrypt password has given.'))
        return True

network_software_logpass()


#----------------------------------------------------------
# Protocol (ssh, http, smpt, ...)
#----------------------------------------------------------
class network_protocol(osv.osv):
    _name = "network.protocol"
    _description = "Protocol"
    _columns = {
        'name': fields.char('Name', size=64, select=1),
    }
network_protocol()


#----------------------------------------------------------
# Services
#----------------------------------------------------------
class network_service(osv.osv):
    _name = "network.service"
    _description = "Service Network"
    _columns = {
        'name': fields.char('Name', size=64, select=1),
        'software_id': fields.many2one('network.software', 'Software', required=True),
        'material':fields.related('software_id', 'material_id', type='many2one', relation='network.material', string='Material', readonly=True),
        'protocol_id': fields.many2one('network.protocol', 'Protocol', select=1),
        'path': fields.char('Path', size=100),
        'port': fields.integer('Port', required=True, select=2),
        'public_port': fields.integer('Public port', select=2, help="Sometimes public and private ports are different."),
        'private_url': fields.char('Private URL', size=256),
        'public_url': fields.char('Public URL', size=256),
    }

    def _compute_public_url(self, cr, uid, ids, *args):
        for rec in self.browse(cr, uid, ids):
            if not rec.protocol_id or not rec.software_id:
                continue
            protocol = rec.protocol_id.name+"://"
            port = rec.port and ":"+str(rec.port) or ""
            public_port = rec.public_port and ":"+str(rec.public_port) or ""
            path = rec.path and rec.path or ""

            # Compute Private URL from Material IP
            ip_address = rec.software_id.material_id.ip_addr
            if ip_address:
                service2 = protocol+ip_address+port+path
                self.write(cr, uid, [rec.id], {'private_url' : service2})

            # Compute Public URL from Network IP
            if not rec.software_id.material_id.network_id:
                continue
            public_ip_address = rec.software_id.material_id.network_id.public_ip_address
            public_domain = rec.software_id.material_id.network_id.public_domain
            if public_domain:
                service1 = protocol+public_domain+public_port+path
                self.write(cr, uid, [rec.id], {'public_url' : service1})
            elif public_ip_address:
                service1 = protocol+public_ip_address+public_port+path
                self.write(cr, uid, [rec.id], {'public_url' : service1})

        return True


    def onchange_port(self, cr, uid, ids, port, context={}):
        if not port:
            return {}
        return {'value':{'public_port': port}}

network_service()


class network_encrypt_password(osv.osv_memory):
    _name = 'network.encrypt.password'
    _columns = {
        'name': fields.char('Encrypt/Decrypt password', size=100),
    }

    def create(self, cr, uid, vals, context=None):
        encrypt_password_ids = self.search(cr, uid, [('create_uid','=',uid),('write_uid','=',uid)], context=context)
        self.unlink(cr, uid, encrypt_password_ids, context=context)
        return super(osv.osv_memory, self).create(cr, uid, vals, context=context)

network_encrypt_password()
