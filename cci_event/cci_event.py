
##############################################################################
#
# Copyright (c) 2007 TINY SPRL. (http://tiny.be) All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from osv import fields,osv
from osv import orm

class event(osv.osv):#added for partner.ods
    _inherit="event.event"
    _description="event.event"
    _columns={
          #Fields present in 'Event Fields'
          'agreement_nbr':fields.char('Agreement Nbr',size=16),
          #'check_accept':fields.many2one('event.event.type.check','Allowed checks'),
          'mail_auto_registr':fields.boolean('Mail Auto Register',help='A mail is send when the registration is confirmed'),
          'mail_auto_confirm':fields.boolean('Mail Auto Confirm',help='A mail is send when the event is confimed'),
          'mail_registr':fields.text('Mail Register',help='Template for the mail'),
          'mail_confirm':fields.text('Mail Confirm',help='Template for the mail'),

          #Fields present in 'Event Views,'
          'note':fields.char('Note',size=256),#should be check
          'fse_code':fields.char('fse code',size=20),#should be corect
          'fse_hours':fields.char('fse hours',size=20),#should be corect
          'signet_type':fields.char('Signet Type',size=20),#should be corect
          'localisation':fields.char('Localisation',size=20),#should be corect
          'account_analytic_id':fields.char('Analytic Account',size=20),#should be corect
          'budget_id':fields.char('Budget',size=20),#should be corect
          'product_id':fields.many2one('product.product','Product'),#should be check
          'mail_auto':fields.char('mail auto',size=20),#should be corect
          'mail_text':fields.char('mail text',size=20),#should be corect
          'sales_open':fields.char('Sales open',size=20),#should be corect
          'sales_draft':fields.char('Sales draft',size=20),#should be corect
        }
event()
