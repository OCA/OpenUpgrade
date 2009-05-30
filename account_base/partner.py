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

from osv import fields, osv

class Partner(osv.osv):
    _inherit = "res.partner"
    _columns = {
        'vat_no' : fields.char('VAT Number', size=256),
        'cst_no' : fields.char('CST Number', size=256),
        'pan_no' : fields.char('PAN Number', size=256),
        'ser_tax': fields.char('Service Tax Number', size=256),
        'excise' : fields.char('Exices Number', size=256),
        'range'  : fields.char('Range', size=256),
        'div'    : fields.char('Division', size=256),
    }
Partner()
