
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

class event_check_type(osv.osv):
    _name="event.check.type"
    _description="event.check.type"
    _columns={
          'name':fields.char('Name',size=20),
        }
event_check_type()

class event(osv.osv):#added for partner.ods
    _inherit="event.event"
    _description="event.event"
    _columns={
          'state': fields.selection([('draft','Draft'),('open','Open'),('confirm','Confirmed'),('done','Done'),('cancel','Canceled'),('closed','Closed')], 'State', readonly=True, required=True),#override field to add some states on it.
          'agreement_nbr':fields.char('Agreement Nbr',size=16),
          'check_accept':fields.many2one('event.check.type','Allowed checks'),
          'mail_auto_registr':fields.boolean('Mail Auto Register',help='A mail is send when the registration is confirmed'),
          'mail_auto_confirm':fields.boolean('Mail Auto Confirm',help='A mail is send when the event is confimed'),
          'mail_registr':fields.text('Mail Register',help='Template for the mail'),
          'mail_confirm':fields.text('Mail Confirm',help='Template for the mail'),
          'note':fields.char('Note',size=256),
          'fse_code':fields.char('Fse code',size=64),
          'fse_hours':fields.integer('Fse Hours'),
          'signet_type':fields.selection([('temp','temp')], 'Signet type'),#type is defined so temp,
          'localisation':fields.char('Localisation',size=20),#should be corect
          'account_analytic_id':fields.many2one('account.analytic.account','Analytic Account'),
          'budget_id':fields.many2one('account.budget.post','Budget'),
          'product_id':fields.many2one('product.product','Product'),
          'sales_open':fields.char('Sales open',size=20),#should be corect
          'sales_draft':fields.char('Sales draft',size=20),#should be corect
        }
event()

class event_check(osv.osv):
    _name="event.check"
    _description="event.check"
    _columns={
        "name": fields.char('Name', size=128, required=True),
        "code": fields.char('Code', size=64),
        "case_id": fields.char('Inscriptions',size=20),#many2one to ?.....
        "state": fields.selection([('open','Open'),('block','Blocked'),('paid','Paid'),('refused','Refused'),('asked','Asked')], 'State', readonly=True, required=True),#should be check
        "unit_nbr": fields.integer('Units'),
        "type_id":fields.many2one('event.check.type','Type'),#should be check
        "date_reception":fields.date("Reception Date"),
        "date_limit":fields.date('Limit Date'),
        "date_submission":fields.date("Submission Date"),
        }
event_check()

class event_type(osv.osv):
    _inherit = 'event.type'
    _description= 'Event type'
    _columns = {
        'check_type': fields.many2one('event.check.type','Check Type'),
    }
event_type()

class event_group(osv.osv):#should be corect (not complete)
    _name= 'event.group'
    _description = 'event.group'
    _columns = {
        "name":fields.char('Name',size=20,required=True),
        "cavalier":fields.boolean('Cavalier',help="Check if we should print papers with participant name"),#should be check
        "type":fields.selection([('image','Image'),('text','Text')], 'Type',)#image,text,none #should be corect
                }
event_group()

class event_subscription(osv.osv):
    _name="event.subscription"
    _description="event.subscription"
    _columns={
        "unit_price": fields.float('Unit Price'),
        "cavalier": fields.boolean('Cavalier'),
        "group_id": fields.many2one('event.group','Event Group'),
        "canal_id" :fields.many2one('res.partner.canal',"Channel"),#should be check, res.chanel (default manual ?)
        "check_mode":fields.boolean('Check Mode'),
        }
event_subscription()
