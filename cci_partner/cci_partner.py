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

import netsvc
from osv import fields, osv

class res_partner(osv.osv):
    _inherit = "res.partner"
    _description = "res.partner"
    _columns = {
        'employee_nbr': fields.integer('Nbr of Employee (Area)',help="Nbr of Employee in the area of the CCI"),
        'employee_nbr_total':fields.integer('Nbr of Employee (Tot)',help="Nbr of Employee all around the world"),
        'invoice_paper':fields.selection([('transfer belgian','Transfer belgian'),('transfer iban ','Transfer iban')], 'Bank Transfer Type',required=True),
        'invoice_public':fields.boolean('Invoice Public'),
        'invoice_special':fields.boolean('Invoice Special'),
        'state_id':fields.char('Partner State',size=20,help='status of activity of the partner'),#should be corect
        'state_id2':fields.char('Customer State',size=20,help='status of the partner as a customer'),#should be corect

        'activity_description':fields.text('Activity Description',traslate=True),
        'activity_code_ids':fields.one2many('res.activity.code','partner_id','Activity Codes'),

        'export_procent':fields.integer('Export(%)'),
        'export_year':fields.date('Export date',help='year of the export_procent value'),
        'import_procent':fields.integer('Import (%)'),
        'import_year':fields.date('Import Date',help='year of the import_procent value'),
        'domiciliation':fields.boolean('Domiciliation'),
        'domiciliation_cotisation':fields.boolean('Domiciliation (cotisation)',help='year of the import_procent value'),
        'invoice_nbr':fields.integer('Nbr of invoice to print',help='number of additive invoices to be printed for this customer'),
        'name_official':fields.char('Official Name',size=80),
        'name_old':fields.char('Former Name',size=80),
        'wall_exclusion':fields.boolean('In Walloon DB',help='exclusion of this partner from the walloon database'),
        'mag_send':fields.selection([('never','Never'),('always','Always'),('managed_by_poste','Managed_by_Poste'),('prospect','Prospect')], 'Send mag.',required=True),
        'date_founded':fields.date('Founding Date',help='Date of foundation of this company'),
        'training_authorization':fields.char('Training Auth.',size=12,help='Formation Checks Authorization number'),
        'lang_authorization':fields.char('Lang. Auth.',size=12,help='Language Checks Authorization number'),
        'alert_advertising':fields.boolean('Adv.Alert',help='Partners description to be shown when inserting new advertising sale'),
        'alert_events':fields.boolean('Event Alert',help='Partners description to be shown when inserting new subscription to a meeting'),
        'alert_legalisations':fields.boolean('Legal. Alert',help='Partners description to be shown when inserting new legalisation'),
        'alert_membership':fields.boolean('Membership Alert',help='Partners description to be shown when inserting new ship sale'),
        'alert_others':fields.boolean('Other alert',help='Partners description to be shown when inserting new sale not treated by _advertising, _events, _legalisations, _Membership'),
        'dir_name':fields.char('Name in Menber Dir.',size=250,help='Name under wich the partner will be inserted in the members directory'),
        'dir_name2':fields.char('1st Shortcut name ',size=250,help='First shortcut in the members directory, pointing to the dir_name field'),
        'dir_name3':fields.char('2nd Shortcut name ',size=250,help='Second shortcut'),
        'dir_date_last':fields.date('Partner Data Date',help='Date of latest update of the partner data by itself (via paper or Internet)'),
        'dir_date_accept':fields.date("Good to shoot Date",help='Date of last acceptation of Bon à Tirer'),
        'dir_presence':fields.boolean('Dir. Presence',help='Présence dans le répertoire des entreprises'),
        'dir_date_publication':fields.date('Publication Date'),
        'dir_exclude':fields.boolean('Dir. exclude',help='Exclusion from the Members directory'),

        'magazine_subscription':fields.boolean('Magazine subscription'),
        'country_relation':fields.one2many('res.partner.country.relation','country_id','Country Relation') #add for view
        #Never,Always,Managed_by_Poste,Prospect
        #virement belge,virement iban
        }
    _defaults = {
                 'wall_exclusion' : lambda *a: False,
                 'dir_presence' : lambda *a: False,
                 'dir_exclude':lambda *a: False,
                 }
res_partner()

class res_partner_zip(osv.osv):
    _name = "res.partner.zip"
    _description = 'res.partner.zip'
    _columns = {
        'name':fields.char('Zip Code',size=4),
        'city':fields.char('City',size=60,traslate=True),
        'partner_id':fields.selection([('temp','temp')],'Master Cci'),
        'post_center_id':fields.char('Post Center',size=40),
        'post_center_special':fields.boolean('Post Center Special'),
        'user_id':fields.many2one('res.users','User'),
        'groups_id': fields.many2many('res.groups', 'partner_zip_group_rel', 'zip_id', 'group_id', 'Groups'),#should be corect
        'distance':fields.integer('Distance',help='Distance (km) between zip location and the cci.')
                }
res_partner_zip()

class res_partner_zip_group_type(osv.osv):
     _name = "res.partner.zip.group.type"
     _description = 'res.partner.zip.group.type'
     _columns = {
         'name':fields.char('Name',size=50),
                }
res_partner_zip_group_type()

class res_partner_zip_group(osv.osv):
     _name = "res.partner.zip.group"
     _description = 'res.partner.zip.group'
     _columns = {
         'type_id':fields.many2one('res.partner.zip.group.type','Type'),#should be correct
         'name':fields.char('Name',size=50),
                }
res_partner_zip_group()

class res_partner_address(osv.osv):
    _inherit = "res.partner.address"
    _description = 'res.partner.address'
    _columns = {
        'state': fields.selection([('correct','Correct'),('to check','To check')],'Code'),
        'zip_id':fields.many2one('res.partner.zip','Zip'),
        'function_code_id':fields.many2one('res.partner.function', 'Function Code'),#should be corect
        'date_start':fields.date('Date start'),
        'date_end':fields.date('Date end'),
        'sequence_partner':fields.integer('Sequence (Partner)',help='order of importance of this address in the list of addresses of the linked partner'),
        'sequence_contact':fields.integer('Sequence (Contact)',help='order of importance of this address in the list of addresses of the linked contact'),
        'canal_id':fields.many2one('res.partner.canal','Canal',help='favorite chanel for communication'),
        'active':fields.boolean('Active'),
        'who_presence':fields.boolean('In Whos Who'),
        'dir_presence':fields.boolean('In Directory'),
    }
    _defaults = {
                 'state' : lambda *a: 'Correct',
                 'who_presence' : lambda *a: True,
                 'dir_presence' : lambda *a: True,
               }

    def unlink(self, cr, uid, ids, context={}):
        #Unlink related contact if: no other Address AND not self_sufficient
        data_address=self.pool.get('res.partner.address').browse(cr, uid, ids)
        id_contact=data_address[0].contact_id.id
        super(res_partner_address,self).unlink(cr, uid, ids,context=context)
        data_contact=self.pool.get('res.partner.contact').browse(cr, uid,[id_contact])
        if (not data_contact[0].self_sufficent)  and (not data_contact[0].address_ids):
            self.pool.get('res.partner.contact').unlink(cr, uid,[data_contact[0].id], context)
        return True

res_partner_address()

class res_activity_code(osv.osv):
    _name = "res.activity.code"
    _description = 'res.activity.code'

    def name_get(self, cr, uid, ids, context={}):
        print "hello world"
        if not len(ids):
            return []
        reads = self.read(cr, uid, ids, ['code','name'], context)
        res = []
        str1=''
        for record in reads:
            if record['name']:
                str1=record['name']+' '+'-'+' '+record['code']
            res.append((record['id'], str1))
        return res

    _columns = {
        'code': fields.char('Code',size=6),
        'name':fields.char('Name',size=250,transtale=True,required=True),
        'description':fields.text('Description'),
        'code_relations':fields.many2many('res.activity.code','res_activity_code_rel','code_id1','code_id2','Related codes'), #should be correct
        'partner_id':fields.many2one('res.partner','Partner'),
    }
res_activity_code()

class res_partner_function(osv.osv):
    _inherit = 'res.partner.function'
    _description = 'Function of the contact inherit'

    def name_get(self, cr, uid, ids, context={}):
        print "hello world"
        if not len(ids):
            return []
        reads = self.read(cr, uid, ids, ['code','name'], context)
        res = []
        str1=''
        for record in reads:
            if record['name'] or record['code']:
                str1=record['name']+'('+record['code']+')'
            res.append((record['id'], str1))
        return res
res_partner_function()

