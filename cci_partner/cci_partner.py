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

class res_partner_state(osv.osv):
    _name = "res.partner.state"
    _description = 'res.partner.state'
    _columns = {
        'name': fields.char('State',size=20,required=True),
    }
res_partner_state()

class res_partner_state2(osv.osv):
    _name = "res.partner.state2"
    _description = 'res.partner.state2'
    _columns = {
        'name': fields.char('State2',size=20,required=True),
    }
res_partner_state2()

class res_partner_article_review(osv.osv):
    _name = "res.partner.article.review"
    _description = 'res.partner.article.review'
    _columns = {
        'name': fields.char('Name',size=50),
        'date':fields.date('Date'),
        'article_ids':fields.one2many('crm_press.article','review_id','Articles',size=20),
    }
res_partner_article_review()


class res_partner_article_keywords(osv.osv):
    _name = "res.partner.article.keywords"
    _description = 'res.partner.article.keywords'
    _columns = {
        'name': fields.char('Name',size=20,required=True),
        'article_ids':fields.many2many('crm_press.article','partner_article_keword_rel','keyword_id','article_id','Articles')
    }
res_partner_article_keywords()

class crm_press_article(osv.osv):
    _name = "crm_press.article"
    _description = 'crm_press.article'
    _rec_name = 'article_id'
    _columns = {
        'article_id': fields.char('Article',size=256),
        'page':fields.integer('Page',size=16),
        'article_length':fields.float('Length'),
        'picture':fields.boolean('Picture'),
        'data':fields.boolean('Data'),
        'graph':fields.boolean('Graph'),
        'keywords_ids':fields.many2many('res.partner.article.keywords','article_keyword_rel','article_id','keyword_id','Keywords'),
        'summary':fields.text('Summary'),
        'partners_ids':fields.one2many('res.partner','article_id','Partners'),
        'contact_ids':fields.one2many('res.partner.contact','contact_id','Contacts'),
        'source_id':fields.char('Source',size=256),
        'date':fields.date('Date'),
        'title':fields.char('Title',size=100),
        'subtitle':fields.text('Subtitle'),
        'press_review':fields.boolean('In the next press review',help='Must be inserted on the next press review'),
        'canal_id':fields.char('Link',size=200,help='A text with or without a link incorporated'),
        'review_id':fields.many2one('res.partner.article.review','Review')#add for one2many field,
    }
    _defaults = {
                 'press_review' : lambda *a: False,
                 }
crm_press_article()

class res_partner(osv.osv):
    _inherit = "res.partner"
    _description = "res.partner"

    def create(self, cr, uid, vals, *args, **kwargs):
        new_id = super(osv.osv,self).create(cr, uid, vals, *args, **kwargs)
        #complete the user_id (salesman) automatically according to the zip code of the main address. Use res.partner.zip to select salesman according to zip code
        if vals['address']:
            for add in vals['address']:
                if add[2]['zip_id'] and add[2]['type']=='default':
                    data=self.pool.get('res.partner.zip').browse(cr, uid, add[2]['zip_id'])
                    saleman_id = data.user_id.id
                    self.write(cr,uid,[new_id],{'user_id':saleman_id})
        return new_id

    def write(self, cr, uid, ids,vals, *args, **kwargs):
        super(osv.osv,self).write(cr, uid, ids,vals, *args, **kwargs)
        if 'address' in vals:
            for add in vals['address']:
                if add[2]['zip_id'] and add[2]['type']=='default':
                    data=self.pool.get('res.partner.zip').browse(cr, uid, add[2]['zip_id'])
                    saleman_id = data.user_id.id
                    self.write(cr,uid,ids,{'user_id':saleman_id})
                else:
                    self.write(cr,uid,ids,{'user_id':False})
        return True

    def check_address(self, cr, uid, ids):
        #constraints to ensure that there is only one default address by partner.
        data_address=self.browse(cr, uid, ids)
        list=[]
        for add in data_address[0].address:
            if add.type in list:
                return False
            list.append(add.type)
        return True

    _columns = {
        'employee_nbr': fields.integer('Nbr of Employee (Area)',help="Nbr of Employee in the area of the CCI"),
        'employee_nbr_total':fields.integer('Nbr of Employee (Tot)',help="Nbr of Employee all around the world"),
        'invoice_paper':fields.selection([('transfer belgian','Transfer belgian'),('transfer iban ','Transfer iban')], 'Bank Transfer Type'),
        'invoice_public':fields.boolean('Invoice Public'),
        'invoice_special':fields.boolean('Invoice Special'),
        'state_id':fields.many2one('res.partner.state','Partner State',help='status of activity of the partner'),
        'state_id2':fields.many2one('res.partner.state2','Customer State',help='status of the partner as a customer'),
        'activity_description':fields.text('Activity Description',traslate=True),
        'activity_code_ids':fields.one2many('res.partner.activity','partner_id','Activity Codes'),
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
        'mag_send':fields.selection([('never','Never'),('always','Always'),('managed_by_poste','Managed_by_Poste'),('prospect','Prospect')], 'Send mag.'),
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
        'country_relation':fields.one2many('res.partner.country.relation','country_id','Country Relation'), #add for view
        'article_id':fields.many2one('crm_press.article','Partner'),#should be corect,add for one2many relation

        #Never,Always,Managed_by_Poste,Prospect
        #virement belge,virement iban
        }
    _defaults = {
                 'wall_exclusion' : lambda *a: False,
                 'dir_presence' : lambda *a: False,
                 'dir_exclude':lambda *a: False,
                 }
    _constraints = [(check_address, 'Error: Only one default address is allowed!', [])]
res_partner()

class res_partner_zip_group_type(osv.osv):
     _name = "res.partner.zip.group.type"
     _description = 'res.partner.zip.group.type'
     _columns = {
         'name':fields.char('Name',size=50,required=True),
                }
res_partner_zip_group_type()

class res_partner_zip_group(osv.osv):
     _name = "res.partner.zip.group"
     _description = 'res.partner.zip.group'
     _columns = {
         'type_id':fields.many2one('res.partner.zip.group.type','Type'),
         'name':fields.char('Name',size=50,required=True),
                }
res_partner_zip_group()

class res_partner_zip(osv.osv):
    _name = "res.partner.zip"
    _description = 'res.partner.zip'
    def check_group_type(self, cr, uid, ids):
        data=self.browse(cr, uid, ids)
        for id in ids:
            sql = '''
            select group_id from partner_zip_group_rel1 where zip_id=%d
            ''' % (id)
            cr.execute(sql)
            groups = cr.fetchall()
        list_group=[]
        for group in groups:
            list_group.append(group[0])
        data_zip = self.pool.get('res.partner.zip.group').browse(cr, uid,list_group)
        list_zip=[]
        for data in data_zip:
            if data.type_id.id in list_zip:
                return False
            list_zip.append(data.type_id.id)
        return True

    _constraints = [(check_group_type, 'Error: Only one group of the same group type is allowed!', [])]
    _columns = {
        'name':fields.char('Zip Code',size=4,required=True),
        'city':fields.char('City',size=60,traslate=True),
        'partner_id':fields.selection([('temp','temp')],'Master Cci'),
        'post_center_id':fields.char('Post Center',size=40),
        'post_center_special':fields.boolean('Post Center Special'),
        'user_id':fields.many2one('res.users','User'),
        'groups_id': fields.many2many('res.partner.zip.group', 'partner_zip_group_rel1', 'zip_id', 'group_id', 'Groups'),
        'distance':fields.integer('Distance',help='Distance (km) between zip location and the cci.')
                }
res_partner_zip()

class res_partner_address(osv.osv):
    _inherit = "res.partner.address"
    _description = 'res.partner.address'
    _columns = {
        'state': fields.selection([('correct','Correct'),('to check','To check')],'Code'),
        'zip_id':fields.many2one('res.partner.zip','Zip'),
        #'function_code_id':fields.many2one('res.partner.function', 'Function Code'),#should be corect
        'function_label':fields.char('Function Label',size=128),
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
        data_addresses=self.pool.get('res.partner.address').browse(cr, uid, ids)
        for address in data_addresses:
            id_contact=address.contact_id.id
            super(res_partner_address,self).unlink(cr, uid, ids,context=context)
            data_contact=self.pool.get('res.partner.contact').browse(cr, uid,[id_contact])
            for data in data_contact:
                if (not data.self_sufficent)  and (not data.address_ids):
                    self.pool.get('res.partner.contact').unlink(cr, uid,[data.id], context)
        return True

res_partner_address()

class res_partner_activity_list(osv.osv):#new object added!
    _name = "res.partner.activity.list"
    _description = 'res.partner.activity.list'
    _columns = {
        'name': fields.char('Code list',size=256,required=True),
        'abbreviation':fields.char('Abbreviation',size=16),
    }
res_partner_activity_list()

class res_partner_activity(osv.osv):#modfiy res.activity.code to res.partner.activity
    _name = "res.partner.activity"
    _description = 'res.partner.activity'

    def name_get(self, cr, uid, ids, context={}):
        #return somethong like”list_id.abbreviation or list_id.name – code”
        if not len(ids):
            return []
        data_activity = self.read(cr, uid, ids, ['list_id','code'], context)
        res = []
        list_obj = self.pool.get('res.partner.activity.list')
        for read in data_activity:
            if read['list_id']:
                data=list_obj.read(cr, uid, read['list_id'][0],['abbreviation','name'], context)
                if data['abbreviation']:
                    res.append((read['id'], data['abbreviation']))
                else:
                    str=data['name']+'-'+read['code']
                    res.append((read['id'],str))
        return res
    _columns = {
        'code': fields.char('Code',size=6),
        'name':fields.char('Name',size=250,transtale=True,required=True),
        'description':fields.text('Description'),
        'code_relations':fields.many2many('res.partner.activity','res_activity_code_rel','code_id1','code_id2','Related codes'),
        'partner_id':fields.many2one('res.partner','Partner'),
        'list_id':fields.many2one('res.partner.activity.list','List',required=True)
    }
res_partner_activity()

class res_partner_activity_relation(osv.osv):#new object added!
    _name = "res.partner.activity.relation"
    _description = 'res.partner.activity.relation'
    _columns = {
        'importance': fields.selection([('main','Main'),('primary','Primary'),('secondary','Secondary')],'Importance'),
        'activity_id':fields.many2one('res.partner.activity','Activity'),
    }
res_partner_activity_relation()

class res_partner_function(osv.osv):
    _inherit = 'res.partner.function'
    _description = 'Function of the contact inherit'

    def name_get(self, cr, uid, ids, context={}):
        if not len(ids):
            return []
        reads = self.read(cr, uid, ids, ['code','name'], context)
        res = []
        str1=''
        for record in reads:
            if record['name'] or record['code']:
                str1=record['name']+'('+(record['code'] or '')+')'
            res.append((record['id'], str1))
        return res
res_partner_function()

class res_partner_relation(osv.osv): # move from cci_base_contact to here
    _name = "res.partner.relation"
    _description = 'res.partner.relation'
    _rec_name = 'partner_id'
    _columns = {
        'partner_id': fields.char('Partner',size=50),#should be correct
        'partner_relation_id':fields.char('Partner Relation',size=50),#should be correct
        'description':fields.text('Description'),
        'type_id':fields.many2one('res.contact.relation.type','Type'), #should be correct
    }
res_partner_relation()

class res_partner_contact(osv.osv):
    _inherit='res.partner.contact'
    _columns = {
        'contact_id':fields.many2one('crm_press.article','Contact')#add for one2many relation only,,,
        }
res_partner_contact()

