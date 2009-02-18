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

from osv import fields, osv


class proforma_followup_step(osv.osv):
    _name = 'proforma.followup_step'
    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'description': fields.text('Description'),
        'proforma_line': fields.one2many('proforma.followup.line', 'proforma_id', 'Proforma Follow-Up Line'),
        'company_id': fields.many2one('res.company', 'Company'),
    }
proforma_followup_step()

class proforma_followup_line(osv.osv):
    _name = 'proforma.followup.line'
    _description = 'PRO-Forma Followup Criteria'
    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'sequence': fields.integer('Sequence'),
        'subject': fields.char('Subject', size=64),
        'email_body': fields.text('E-mail Body' , translate=True),
        'days': fields.integer('Days of delay'),
        'proforma_id': fields.many2one('proforma.followup_step', 'Proforma step', required=True, ondelete="cascade"),
        'function': fields.text('Function to call'),
        'send_email': fields.boolean('Send E-mail?'),
        'call_function': fields.boolean('Call function?'),
        'cancel_invoice': fields.boolean('Cancel Invoice?'),
    }
proforma_followup_line()




# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

