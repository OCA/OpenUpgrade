# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2004-2008 Tiny SPRL (<http://tiny.be>). All Rights Reserved
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
from osv import fields,osv

class EmailAddress(osv.osv):
    _name = "res.company.address"
    _columns = {
        'company_id' : fields.many2one('res.company', 'Company' , required=True),
        'email': fields.many2one('email.smtpclient', 'Email Address',  required=True),
        'name' : fields.selection([("default", "Default"),("inoice", "Invoice"),("sale","Sale"),("delivery","Delivery")], "Address Type",required=True)
    }
EmailAddress()

class Company(osv.osv):
    _inherit = "res.company"
    _columns = {
        'addresses': fields.one2many('res.company.address', 'company_id', 'Email Addresses'),
    }
Company()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

