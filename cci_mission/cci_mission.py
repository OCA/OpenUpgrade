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
import time
from datetime import date,timedelta
import datetime
import pooler
import netsvc

STATE = [
    ('none', 'Non Member'),
    ('canceled', 'Cancelled Member'),
    ('old', 'Old Member'),
    ('waiting', 'Waiting Member'),
    ('invoiced', 'Invoiced Member'),
    ('associated', 'Associated Member'),
    ('free', 'Free Member'),
    ('paid', 'Paid Member'),
]

class res_partner(osv.osv):
    _inherit = 'res.partner'
    _description = 'res.partner'

    _columns = {
        'asker_name': fields.char('Asker Name',size=50),
        'asker_address': fields.char('Asker Address',size=50),
        'asker_zip_id': fields.many2one('res.partner.zip','Asker Zip Code'),
        'sender_name': fields.char('Sender Name',size=50),
        'insurer_id' : fields.char('Insurer ID',size=50),
    }

res_partner()

class cci_missions_site(osv.osv):
    _name = 'cci_missions.site'
    _description = 'cci_missions.site'

    _columns = {
        'name' : fields.char('Name of the Site',size=50,required=True),
        'official_name_1' : fields.char('Official Name of the Site',size=50,required=True),
        'official_name_2' : fields.char('Official Name of the Site',size=50),
        'official_name_3' : fields.char('Official Name of the Site',size=50),
        'official_name_4' : fields.char('Official Name of the Site',size=50),
        'embassy_sequence_id' : fields.many2one('ir.sequence','Sequence for Embassy Folder',required=True),
    }

cci_missions_site()

class cci_missions_embassy_folder(osv.osv):
    _name = 'cci_missions.embassy_folder'
    _description = 'cci_missions.embassy_folder'
    _inherits = {'crm.case': 'crm_case_id'}

    def _cci_mission_send(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'state':'pending',})
        cases = self.browse(cr, uid, ids)
        self._history(cr, uid, cases, 'Send', history=True,)
        return True

    def _cci_mission_got_back(self,cr,uid,ids,*args):
        self.write(cr, uid, ids, {'state':'open',})
        cases = self.browse(cr, uid, ids)
        self._history(cr, uid, cases, 'Got Back', history=True)
        for id in self.browse(cr, uid, ids):
            data = {}
            obj_folder_line = self.pool.get('cci_missions.embassy_folder_line')
            temp = obj_folder_line.search(cr, uid, [('folder_id','=',id.id),('type','=','Translation')])
            if temp:
                translation_line = obj_folder_line.browse(cr, uid, [temp[0]])[0]
                if translation_line.awex_eligible and id.partner_id.awex_eligible == 'yes':
                    #look for an existing credit line in the current time
                    credit_line = self.pool.get('credit.line').search(cr, uid, [('from_date','<=',time.strftime('%Y-%m-%d')), ('to_date', '>=', time.strftime('%Y-%m-%d'))])
                    if credit_line:
                        #if there is one available: get available amount from it
                        amount = self.pool.get('credit.line').browse(cr, uid,[credit_line[0]])[0].get_available_amount(cr, uid, credit_line[0], translation_line.customer_amount, id.partner_id.id)
                        if amount > 0:
                            data['awex_amount'] = amount
                            data['credit_line_id'] =  credit_line[0]
                        else:
                            data['awex_eligible'] = False
                    obj_folder_line.write(cr, uid, [translation_line.id], data)
        return True

    def _cci_mission_done_folder(self,cr,uid,ids,*args):
        self.write(cr, uid, ids, {'state':'done','invoice_date': time.strftime('%Y-%m-%d %H:%M:%S')})
        cases = self.browse(cr, uid, ids)
        self._history(cr, uid, cases, 'Invoiced', history=True)
        return True

    def _history(self, cr, uid,ids,keyword, history=False, email=False, context={}):
        for case in ids:
            data = {
                'name': keyword,
                'som': case.som.id,
                'canal_id': case.canal_id.id,
                'user_id': uid,
                'case_id': case.crm_case_id.id
            }
            obj = self.pool.get('crm.case.log')
            obj.create(cr, uid, data, context)
        return True

    def create(self, cr, uid, vals, *args, **kwargs):
#       Overwrite the name field to set next sequence according to the sequence in for the embassy folder related in the site_id
        if vals['site_id']:
            data = self.pool.get('cci_missions.site').browse(cr, uid,vals['site_id'])
            seq = self.pool.get('ir.sequence').get(cr, uid,data.embassy_sequence_id.code)
            if seq:
                vals.update({'name': seq})
        temp = super(osv.osv,self).create(cr, uid, vals, *args, **kwargs)
        self._history(cr, uid,self.browse(cr, uid, [temp]), 'Created', history=True)
        return temp



    def onchange_partner_id(self, cr, uid, ids, part):
        if not part:
            return {'value':{'partner_address_id': False}}
        part_obj = self.pool.get('res.partner')
        data_partner = part_obj.browse(cr,uid,part)
        if data_partner.alert_legalisations:
                raise osv.except_osv('Error!',data_partner.alert_explanation or 'Partner is not valid')
        addr = part_obj.address_get(cr, uid, [part], ['contact'])
        data = {'partner_address_id':addr['contact']}
        return {'value':data}

    def check_folder_line(self, cr, uid, ids):
        #CONSTRAINT: For each embassy Folder, it can only be one embassy_folder_line of each type.
        data_folder = self.browse(cr,uid,ids)
        list = []
        for folder in data_folder:
            for line in folder.embassy_folder_line_ids:
                if line.type and line.type in list:
                    return False
                list.append(line.type)
        return True

    _columns = {
        'crm_case_id' : fields.many2one('crm.case','Case'),
        'member_price' : fields.boolean('Member Price Allowed'),
        'customer_reference' : fields.char('Folders Reference for the Customer',size=30),
        'destination_id' : fields.many2one('cci.country','Destination Country', domain=[('valid4embassy','=',True)]),
        'link_ids': fields.one2many('cci_missions.dossier','embassy_folder_id','Linked Documents'),
        'internal_note': fields.text('Internal Note'),
        'invoice_note':fields.text('Note to Display on the Invoice',help='to display as the last embassy_folder_line of this embassy_folder.'),
        'embassy_folder_line_ids' : fields.one2many('cci_missions.embassy_folder_line','folder_id','Details'),
        'site_id': fields.many2one('cci_missions.site','Site', required=True),
        'invoice_date' : fields.datetime('Invoice Date', readonly=True) ,
        "invoice_id":fields.many2one("account.invoice","Invoice"),
    }

    _defaults = {
        'section_id': lambda obj, cr, uid, context: obj.pool.get('crm.case.section').search(cr, uid, [('name','=','Embassy Folder')])[0],
        'invoice_date': lambda *a: False,
        'name': lambda *args: '/',
        'state' :  lambda *a : 'draft',
        "date": lambda *a: time.strftime("%Y-%m-%d %H:%M:%S")
    }

    _constraints = [(check_folder_line, 'Error: Only One Embassy Folder line allowed for each type!', ['embassy_folder_line_ids'])]

cci_missions_embassy_folder()

class cci_missions_embassy_folder_line (osv.osv):
    _name = 'cci_missions.embassy_folder_line'
    _description = 'cci_missions.embassy_folder_line '


    def create(self, cr, uid, vals, *args, **kwargs):
        prod_name= vals['type'] + str(' Product')
        cr.execute('select id from product_template where name='"'%s'"''%str(prod_name))
        prod=cr.fetchone()

        if prod:
            product_id=prod[0]
            prod_info = self.pool.get('product.product').browse(cr, uid,product_id)
            account =  prod_info.product_tmpl_id.property_account_income.id
            if not account:
                account = prod_info.categ_id.property_account_income_categ.id
            vals['account_id']=account
        return super(osv.osv,self).create(cr, uid, vals, *args, **kwargs)

    def write(self, cr, uid, ids, vals, *args, **kwargs):
        if vals.has_key('type'):
            prod_name = vals['type'] + str(' Product')
            cr.execute('select id from product_template where name='"'%s'"''%str(prod_name))
            prod=cr.fetchone()
            if prod:
                product_id=prod[0]
                prod_info = self.pool.get('product.product').browse(cr, uid,product_id)
                account =  prod_info.product_tmpl_id.property_account_income.id
                if not account:
                    account = prod_info.categ_id.property_account_income_categ.id
                vals['account_id']=account
        return super(osv.osv,self).write( cr, uid, ids,vals, *args, **kwargs)

    def onchange_line_type(self,cr,uid,ids,type):
        data={}
        data['courier_cost']=data['customer_amount']=data['account_id']=data['name']=False

        if not type:
            return {'value' : data }

        data['name']=type
        prod_name= str(type) + str(' Product')
        cr.execute('select id from product_template where name='"'%s'"''%str(prod_name))
        prod=cr.fetchone()

        if not prod:
            return {'value' : data }

        product_id=prod[0]
        prod_info = self.pool.get('product.product').browse(cr, uid,product_id)
        data['courier_cost']=prod_info.standard_price
        data['customer_amount']=prod_info.list_price
        data['tax_rate'] = prod_info.taxes_id and prod_info.taxes_id[0].id or False
        account =  prod_info.product_tmpl_id.property_account_income.id
        if not account:
            account = prod_info.categ_id.property_account_income_categ.id
        data['account_id']=account

        return {'value' : data }

    _columns = {
        'name' : fields.char('Description',size=50,required=True),
        'folder_id' : fields.many2one('cci_missions.embassy_folder','Related Embassy Folder',required=True),
        'courier_cost' : fields.float('Couriers Costs'),
        'customer_amount' : fields.float('Invoiced Amount'),
        'tax_rate': fields.many2one('account.tax','Tax Rate'),
        'type' : fields.selection([('CBA','CBA'),('Ministry','Ministry'),('Embassy Consulate','Embassy Consulate'),('Translation','Translation'),('Administrative','Administrative'),('Travel Costs','Travel Costs'),('Others','Others')],'Type',required=True),
        'account_id' : fields.many2one('account.account', 'Account',required=True),
        'awex_eligible':fields.boolean('AWEX Eligible'),
        'awex_amount':fields.float('AWEX Amount', readonly=True),
        'credit_line_id':fields.many2one('credit.line', 'Credit Line', readonly=True),
    }

cci_missions_embassy_folder_line()

class cci_missions_dossier_type(osv.osv):
    _name = 'cci_missions.dossier_type'
    _description = 'cci_missions.dossier_type'

    _columns = {
        'code' : fields.char('Code',size=3,required=True),
        'name' : fields.char('Description',size=50,required=True),
        'original_product_id' : fields.many2one('product.product','Reference for Original Copies',required=True,help='for the association with a pricelist'),
        'copy_product_id' : fields.many2one('product.product','Reference for Copies',required=True,help='for the association with a pricelist'),
        'site_id' : fields.many2one('cci_missions.site','Site',required=True),
        'sequence_id' : fields.many2one('ir.sequence','Sequence',required=True,help='for association with a sequence'),
        'section' : fields.selection([('certificate','Certificate'),('legalization','Legalization'),('ATA','ATA Carnet')],'Type',required=True),
        'warranty_product_1': fields.many2one('product.product', 'Warranty product for ATA carnet if Own Risk'),
        'warranty_product_2': fields.many2one('product.product', 'Warranty product for ATA carnet if not own Risk'),
        'id_letter' : fields.char('ID Letter', size=1, help='for identify the type of certificate by the federation' ),
    }

cci_missions_dossier_type()

class cci_missions_dossier(osv.osv):
    _name = 'cci_missions.dossier'
    _description = 'cci_missions.dossier'

    def create(self, cr, uid, vals, *args, **kwargs):
        #overwrite the create: if the text_on_invoice field is empty then fill it with name + destination_id.name + (quantity_original)
        if not vals['text_on_invoice']:
            invoice_text = vals['name']
            if vals['destination_id']:
                destination_data = self.pool.get('cci.country').browse(cr,uid,vals['destination_id'])
                invoice_text = vals['name'] + ' ' + destination_data.name + ' (' + str(vals['quantity_original'])  + ')'
            vals.update({'text_on_invoice': invoice_text})
        return super(osv.osv,self).create(cr, uid, vals, *args, **kwargs)

    def get_partner_details(self, cr, uid, ids,order_partner_id):
        result={}
        asker_name=False
        sender_name=False
        if order_partner_id:
            partner_info = self.pool.get('res.partner').browse(cr, uid,order_partner_id)
            if not partner_info.asker_name:
                asker_name=partner_info.name
            else:
                asker_name=partner_info.asker_name
            if not partner_info.sender_name:
                sender_name=partner_info.name
            else:
                sender_name=partner_info.sender_name
        result = {'value': {
            'asker_name': asker_name,
            'sender_name': sender_name}
        }
        return result

    def _amount_subtotal(self, cr, uid, ids, name, args, context=None):
        res={}
        data_dosseir = self.browse(cr,uid,ids)
        for data in data_dosseir:
            sum=0.00
            for product in data.product_ids:
                sum += product.price_subtotal
            res[data.id]=sum
        return res

    _columns = {
        'id': fields.integer('ID', readonly=True),
        'name' : fields.char('Reference',size=20,required=True),
        'type_id' : fields.many2one('cci_missions.dossier_type','Dossier Type',required=True),
        'date' : fields.date('Creation Date',required=True),
        'order_partner_id': fields.many2one('res.partner','Billed Customer',required=True),
        'asker_name':fields.char('Asker Name',size=50),
        'sender_name':fields.char('Sender Name',size=50),
        'to_bill':fields.boolean('To Be Billed'),
        'state':fields.selection([('draft','Confirmed'),('invoiced','Invoiced'),('cancel_customer','Canceled by Customer'),('cancel_cci','Canceled by the CCI')],'State',),
        'goods':fields.char('Goods Description',size=100),
        'goods_value':fields.float('Value of the Sold Goods'),#Monetary; must be greater than zero
        'destination_id':fields.many2one('cci.country','Destination Country', domain=[('valid4certificate','=',True)]),
        'embassy_folder_id':fields.many2one('cci_missions.embassy_folder','Related Embassy Folder'),
        'quantity_copies':fields.integer('Number of Copies'),
        'quantity_original' : fields.integer('Quantity of Originals',required=True),
        'sub_total':fields.function(_amount_subtotal, method=True, string='Sub Total for Extra Products', store=True),
        'text_on_invoice':fields.text('Text to Display on the Invoice'),
        'product_ids': fields.one2many('product.lines', 'dossier_product_line_id', 'Products'),
        'invoice_id':fields.many2one("account.invoice","Invoice"),
        'invoiced_amount': fields.float('Total'),
    }

    _defaults = {
        'name': lambda *args: '/',
        'date': lambda *a: time.strftime('%Y-%m-%d'),
        'to_bill' : lambda *b : True,
        'state' : lambda *a : 'draft',
        'quantity_original' : lambda *a : 1
    }

cci_missions_dossier()

class cci_missions_custom_code(osv.osv):
    _name= 'cci_missions.custom_code'
    _description = 'cci_missions.custom_code'
    _columns = {
        'name' : fields.char('Name',size=8,required=True),
        'meaning' : fields.text('Meaning',required=True),
        'official' : fields.boolean('Official Code'),
    }

    _defaults = {
        'official': lambda *a: False,
    }

cci_missions_custom_code()

class cci_missions_certificate(osv.osv):
    _name = 'cci_missions.certificate'
    _description = 'cci_missions.certificate'
    _inherits = {'cci_missions.dossier': 'dossier_id' }

    def _amount_total(self, cr, uid, ids, name, args, context=None):
        res ={}
        data_dosseir = self.browse(cr,uid,ids)

        for data in data_dosseir:
            if data.state =='draft':
                data_partner = self.pool.get('res.partner').browse(cr,uid,data.order_partner_id.id)
                context.update({'partner_id':data_partner})
                context.update({'force_member':False})
                context.update({'force_non_member':False})
                context.update({'date':data.date})
                context.update({'value_goods':data.goods_value})
                context.update({'pricelist':data_partner.property_product_pricelist.id})
                price_org = self.pool.get('product.product')._product_price(cr, uid, [data.type_id.original_product_id.id], False, False, context)
                price_copy = self.pool.get('product.product')._product_price(cr, uid, [data.type_id.copy_product_id.id], False, False, context)
                cost_org=price_org[data.type_id.original_product_id.id]
                cost_copy=price_copy[data.type_id.copy_product_id.id]
                qty_org = data.quantity_original
                qty_copy = data.quantity_copies
                subtotal =  data.sub_total
                if qty_org < 0 or qty_copy < 0:
                    raise osv.except_osv('Input Error!','No. of Copies and Quantity of Originals should be positive.')
                total = ((cost_org * qty_org ) + (cost_copy * qty_copy) + subtotal)
                res[data.id] = total
            else :
                res[data.id]=data.invoiced_amount
        return res

    def cci_dossier_cancel_cci(self, cr, uid, ids, *args):
        data=self.browse(cr,uid,ids[0])
        if data.invoice_id.state == 'paid':
            new_ids = self.pool.get('account.invoice').refund(cr, uid,[data.invoice_id.id])
            self.write(cr, uid,ids, {'invoice_id' : new_ids[0]})
        else:
            wf_service = netsvc.LocalService('workflow')
            wf_service.trg_validate(uid, 'account.invoice', data.invoice_id.id, 'invoice_cancel', cr)
        self.write(cr, uid, ids, {'state':'cancel_cci',})
        return True

    def get_certification_details(self, cr, uid, ids,order_partner_id):
        result={}
        asker_name=False
        sender_name=False
        asker_address=False
        zip=False

        if order_partner_id:
            partner_info = self.pool.get('res.partner').browse(cr, uid,order_partner_id)
            if partner_info.alert_legalisations:
                raise osv.except_osv('Error!',partner_info.alert_explanation or 'Partner is not valid')
            if not partner_info.asker_name:
                asker_name=partner_info.name
            else:
                asker_name=partner_info.asker_name
            if not partner_info.sender_name:
                sender_name=partner_info.name
            else:
                sender_name=partner_info.sender_name
            if not partner_info.asker_address:
                if partner_info.address!=[]:
                    for add in partner_info.address:
                        if add.type=='default':
                            asker_address=add.street
                            break
            else:
                asker_address=partner_info.asker_address
            if not partner_info.asker_zip_id.id:
                if partner_info.address!=[]:
                    for add in partner_info.address:
                        if add.type=='default':
                            zip=add.zip_id.id
                            break
            else:
                zip=partner_info.asker_zip_id.id

        result = {'value': {
            'asker_name': asker_name,
            'asker_address': asker_address,
            'asker_zip_id': zip,
            'sender_name': sender_name}
        }
        return result

    def create(self, cr, uid, vals, *args, **kwargs):
#       Overwrite the name fields to set next sequence according to the sequence in the certification type (type_id)
        if vals['type_id']:
            data = self.pool.get('cci_missions.dossier_type').browse(cr, uid,vals['type_id'])
            seq = self.pool.get('ir.sequence').get(cr, uid,data.sequence_id.code)
            if seq:
                vals.update({'name': seq})
        return super(osv.osv,self).create(cr, uid, vals, *args, **kwargs)

    _columns = {
        'dossier_id' : fields.many2one('cci_missions.dossier','Dossier'),
        'total':fields.function(_amount_total, method=True, string='Total', store=True),# sum of the price for copies, originals and extra_products
        'asker_address' : fields.char('Asker Address',size=50),#by default, res.partner->asker_adress or, res_partner.address[default]->street
        'asker_zip_id' : fields.many2one('res.partner.zip','Asker Zip Code'),#by default, res.partner->asker_zip_id or, res_partner.address[default]->zip_id
        'special_reason' : fields.selection([('none','None'),('Commercial Reason','Commercial Reason'),('Substitution','Substitution')],'For special cases'),
        'legalization_ids' : fields.one2many('cci_missions.legalization','certificate_id','Related Legalizations'),
        'customs_ids' : fields.many2many('cci_missions.custom_code','certificate_custome_code_rel','certificate_id','custom_id','Custom Codes'),
        'sending_spf': fields.date('SPF Sending Date',help='Date of the sending of this record to the external database'),
        'origin_ids' : fields.many2many('cci.country','certificate_country_rel','certificate_id','country_id','Origin Countries',domain=[('valid4certificate','=',True)])
    }

    _defaults = {
        'special_reason': lambda *a: 'none',
    }

cci_missions_certificate()

class cci_missions_legalization(osv.osv):
    _name = 'cci_missions.legalization'
    _description = 'cci_missions.legalization'
    _inherits = {'cci_missions.dossier': 'dossier_id'}

    def _amount_total(self, cr, uid, ids, name, args, context=None):
        res ={}
        data_dosseir = self.browse(cr,uid,ids)

        for data in data_dosseir:
            if data.state =='draft':
                data_partner = self.pool.get('res.partner').browse(cr,uid,data.order_partner_id.id)

                force_member=force_non_member=False
                if data.member_price==1:
                    force_member=True
                else:
                    force_non_member=True
                context.update({'partner_id':data_partner})
                context.update({'force_member':force_member})
                context.update({'force_non_member':force_non_member})
                context.update({'date':data.date})
                context.update({'value_goods':data.goods_value})
                context.update({'pricelist':data_partner.property_product_pricelist.id})
                price_org = self.pool.get('product.product')._product_price(cr, uid, [data.type_id.original_product_id.id], False, False, context)
                price_copy = self.pool.get('product.product')._product_price(cr, uid, [data.type_id.copy_product_id.id], False, False, context)
                cost_org=price_org[data.type_id.original_product_id.id]
                cost_copy=price_copy[data.type_id.copy_product_id.id]
                qty_org = data.quantity_original
                qty_copy = data.quantity_copies
                subtotal =  data.sub_total

                if qty_org < 0 or qty_copy < 0:
                    raise osv.except_osv('Input Error!','No. of Copies and Quantity of Originals should be positive.')
                total = ((cost_org * qty_org ) + (cost_copy * qty_copy) + subtotal)
                res[data.id] = total
            else :
                res[data.id]=data.invoiced_amount
        return res

    def cci_dossier_cancel_cci(self, cr, uid, ids, *args):
        data=self.browse(cr,uid,ids[0])
        if data.invoice_id.state == 'paid':
            new_ids = self.pool.get('account.invoice').refund(cr, uid,[data.invoice_id.id])
            self.write(cr, uid,ids, {'invoice_id' : new_ids[0]})
        else:
            wf_service = netsvc.LocalService('workflow')
            wf_service.trg_validate(uid, 'account.invoice', data.invoice_id.id, 'invoice_cancel', cr)
        self.write(cr, uid, ids, {'state':'cancel_cci',})
        return True

    def get_legalization_details(self, cr, uid, ids,order_partner_id):
        result={}
        asker_name=False
        sender_name=False
        member_state=False
        if order_partner_id:
            partner_info = self.pool.get('res.partner').browse(cr, uid,order_partner_id)
            if partner_info.alert_legalisations:
                raise osv.except_osv('Error!',partner_info.alert_explanation or 'Partner is not valid')
            if partner_info.membership_state == 'none': #the boolean "Apply the member price" should be set to TRUE or FALSE when the partner is changed in regard of the membership state of him.
                member_state = False
            else:
                member_state = True
            if not partner_info.asker_name:
                asker_name=partner_info.name
            else:
                asker_name=partner_info.asker_name
            if not partner_info.sender_name:
                sender_name=partner_info.name
            else:
                sender_name=partner_info.sender_name
        result = {'value': {
            'asker_name': asker_name,
            'sender_name': sender_name,
            'member_price':member_state
            }
        }
        return result

    def create(self, cr, uid, vals, *args, **kwargs):
#       Overwrite the name fields to set next sequence according to the sequence in the legalization type (type_id)
        if vals['type_id']:
            data = self.pool.get('cci_missions.dossier_type').browse(cr, uid,vals['type_id'])
            seq = self.pool.get('ir.sequence').get(cr, uid,data.sequence_id.code)
            if seq:
                vals.update({'name': seq})
        return super(osv.osv,self).create(cr, uid, vals, *args, **kwargs)

    def _get_member_state(self, cr, uid, ids, name, args, context=None):
        res={}
        leg_ids = self.browse(cr,uid,ids)
        for p_id in leg_ids:
            res[p_id.id]=p_id.dossier_id.order_partner_id.membership_state
        return res

    _columns = {
        'dossier_id' : fields.many2one('cci_missions.dossier','Dossier'),
        'total':fields.function(_amount_total, method=True, string='Total', store=True),# sum of the price for copies, originals and extra_products
        'certificate_id' : fields.many2one('cci_missions.certificate','Related Certificate'),
        'partner_member_state': fields.function(_get_member_state, method=True,selection=STATE,string='Member State of the Partner',readonly=True,type="selection"),
        'member_price' : fields.boolean('Apply the Member Price'),
    }

cci_missions_legalization()

class cci_missions_courier_log(osv.osv):
    _name = 'cci_missions.courier_log'
    _description = 'cci_missions.courier_log'
    _columns = {
        'embassy_folder_id' : fields.many2one('cci_missions.embassy_folder','Related Embassy Folder',required=True),
        'cba': fields.boolean('CBA'),
        'ministry' :  fields.boolean('Ministry'),
        'translation' : fields.boolean('Translation'),
        'embassy_name' : fields.char('Embassy Name',size=30),
        'consulate_name' : fields.char('Consulate Name',size=30),
        'others' : fields.char('Others',size=200),
        'copy_cba' : fields.boolean('Photocopy Before CBA'),
        'copy_ministry' : fields.boolean('Photocopy Before Ministry'),
        'copy_embassy_consulate' : fields.boolean('Photocopy Before Embassy or Consulate'),
        'documents' : fields.integer('Number of Documents to Legalize'),
        'documents_certificate' : fields.text('List of Certificates'),
        'documents_invoice' : fields.text('List of Invoices'),
        'documents_others' : fields.text('Others'),
        'message' : fields.text('Message to the Courier'),
        'return_address' : fields.selection([('A la CCI','A la CCI'),('Au client','Au client')],'Address of Return',required=True),
        'address_name_1' : fields.char('Company Name',size=80),
        'address_name_2' : fields.char('Contact Name',size=80),
        'address_street' : fields.char('Street',size=80),
        'address_city' : fields.char('City',size=80),
        'qtty_to_print' : fields.integer('Number of Sheets'),
        'partner_address_id' : fields.many2one('res.partner.address','Courier'),
    }

cci_missions_courier_log()

#~ class cci_missions_area(osv.osv):
    #~ _name = 'cci_missions.area'
    #~ _description = 'cci_missions.area'
    #~ _columns = {
        #~ 'name' : fields.char('Description',size=50,required=True,translate=True),
        #~ 'country_ids': fields.many2many('res.country','area_country_rel','area','country',"Countries"),
    #~ }

#~ cci_missions_area()

class cci_missions_ata_usage(osv.osv):
    _name = 'cci_missions.ata_usage'
    _description = 'cci_missions.ata_usage'
    _columns = {
        'name' : fields.char('Usage',size=80,required=True),
    }

cci_missions_ata_usage()

class cci_missions_ata_carnet(osv.osv):
    _name = 'cci_missions.ata_carnet'
    _description = 'cci_missions.ata_carnet'

    def create(self, cr, uid, vals, *args, **kwargs):
        context = {}
        data_partner=self.pool.get('res.partner').browse(cr,uid,vals['partner_id'])
        context.update({'pricelist':data_partner.property_product_pricelist.id})

        if 'creation_date' in vals:
            context.update({'date':vals['creation_date']})
            context.update({'emission_date':vals['creation_date']})
        if 'partner_id' in vals:
            context.update({'partner_id':vals['partner_id']})
        if 'goods_value' in vals:
            context.update({'value_goods':vals['goods_value']})
        if 'double_signature' in vals:
            context.update({'double_signature':vals['double_signature']})
        force_member=force_non_member=False
        if 'member_price' in vals and vals['member_price']==1:
            force_member=True
        else:
            force_non_member=True
        context.update({'force_member':force_member})
        context.update({'force_non_member':force_non_member})

        data = self.pool.get('cci_missions.dossier_type').browse(cr, uid,vals['type_id'])
        if 'own_risk' in vals and vals['own_risk']:
            warranty_product = data.warranty_product_1.id
        else:
            warranty_product = data.warranty_product_2.id

        warranty= self.pool.get('product.product').price_get(cr,uid,[warranty_product],'list_price', context)[warranty_product]
        vals.update({'warranty_product_id' : warranty_product, 'warranty': warranty})

        seq = self.pool.get('ir.sequence').get(cr, uid,data.sequence_id.code)
        if seq:
            vals.update({'name': seq})
        return super(osv.osv,self).create(cr, uid, vals, *args, **kwargs)

    def write(self, cr, uid, ids,vals, *args, **kwargs):
        data_carnet = self.browse(cr,uid,ids[0])
        context = {}
        if 'creation_date' in vals:
            context.update({'date':vals['creation_date']})
            context.update({'emission_date':vals['creation_date']})
        else:
            context.update({'date':data_carnet.creation_date})
            context.update({'emission_date':data_carnet.creation_date})

        if 'partner_id' in vals:
            context.update({'partner_id':vals['partner_id']})
            data_partner=self.pool.get('res.partner').browse(cr,uid,vals['partner_id'])
        else:
            context.update({'partner_id':data_carnet.partner_id.id})
            data_partner=self.pool.get('res.partner').browse(cr,uid,data_carnet.partner_id.id)

        if 'goods_value' in vals:
            context.update({'value_goods':vals['goods_value']})
        else:
            context.update({'value_goods':data_carnet.goods_value})
        if 'double_signature' in vals:
            context.update({'double_signature':vals['double_signature']})
        else:
            context.update({'double_signature':data_carnet.double_signature})
        force_member=force_non_member=False

        context.update({'pricelist':data_partner.property_product_pricelist.id})
        if 'member_price' in vals:
            if vals['member_price']==1:
                force_member=True
            else:
                force_non_member=True
        else:
            if data_carnet.member_price==1:
                force_member=True
            else:
                force_non_member=True
        context.update({'force_member':force_member})
        context.update({'force_non_member':force_non_member})

        if 'own_risk' in vals:
            if vals['own_risk']:
                warranty_product = data_carnet.type_id.warranty_product_1.id
            else:
                warranty_product = data_carnet.type_id.warranty_product_2.id
        else:
            if data_carnet.own_risk:
                warranty_product = data_carnet.type_id.warranty_product_1.id
            else:
                warranty_product = data_carnet.type_id.warranty_product_2.id
        warranty= self.pool.get('product.product').price_get(cr,uid,[warranty_product],'list_price', context)[warranty_product]

        vals.update({'warranty_product_id' : warranty_product, 'warranty': warranty})
        super(cci_missions_ata_carnet,self).write(cr, uid, ids,vals, *args, **kwargs)
        return True

    def button_uncertain(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'state':'pending',})
        return True

    def button_correct(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'state':'correct','ok_state_date':time.strftime('%Y-%m-%d')})
        return True

    def button_dispute(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'state':'dispute',})
        return True

    def button_closed(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'state':'closed',})
        return True

    def cci_ata_created(self, cr, uid, ids):
        self.write(cr, uid, ids, {'state':'created','return_date':time.strftime('%Y-%m-%d')})
        return True

    def _get_insurer_id(self, cr, uid, ids, name, args, context=None):
        res={}
        partner_ids = self.browse(cr,uid,ids)
        for p_id in partner_ids:
            res[p_id.id]=p_id.partner_id.insurer_id
        return res

    def onchange_type_carnet(self, cr, uid, ids,type_id,own_risk):
        data={'warranty_product_id' : False,'warranty':False}
        if not type_id:
            return {'value':data}
        data_carnet_type = self.pool.get('cci_missions.dossier_type').browse(cr,uid,type_id)
        if own_risk:
            warranty_prod=data_carnet_type.warranty_product_1.id
        else:
            warranty_prod=data_carnet_type.warranty_product_2.id
        data['warranty_product_id'] =warranty_prod
        dict1=self.onchange_warranty_product_id(cr,uid,ids,warranty_prod)
        data.update(dict1['value'])
        return {'value':data}

    def onchange_own_risk(self,cr,uid,ids,type_id,own_risk):
        data={'warranty_product_id' : False,'warranty':False}
        if not type_id:
            return {'value': data}
        warranty_prod = False
        data_carnet_type = self.pool.get('cci_missions.dossier_type').browse(cr,uid,type_id)
        if own_risk:
            warranty_prod =data_carnet_type.warranty_product_1.id
        else:
            warranty_prod = data_carnet_type.warranty_product_2.id
        data['warranty_product_id'] =warranty_prod
        dict1=self.onchange_warranty_product_id(cr,uid,ids,warranty_prod)
        data.update(dict1['value'])
        return {'value':data}

    def _get_member_state(self, cr, uid, ids, name, args, context=None):
        res={}
        partner_ids = self.browse(cr,uid,ids)
        for p_id in partner_ids:
            res[p_id.id]=p_id.partner_id.membership_state
        return res

    def check_ata_carnet(self,cr, uid, ids):
        data_carnet=self.browse(cr, uid, ids)
        for data in data_carnet:
            if (data.own_risk) or (data.insurer_agreement > 0 and data.partner_id.insurer_id > 0):
                return True
        return False

    def _default_validity_date(self,cr,uid,context={}):
        creation_date=datetime.datetime.today()
        year=datetime.date(creation_date.year + 1,creation_date.month,creation_date.day)
        validity_date= year - timedelta(days=1)
        return validity_date.strftime('%Y-%m-%d')

    def _tot_products(self, cr, uid, ids, name, args, context=None):
        res={}
        carnet_ids = self.browse(cr,uid,ids)
        for p_id in carnet_ids:
            sum=0.00
            for line_id in p_id.product_ids:
                sum += line_id.price_subtotal
            res[p_id.id]=sum
        return res

    def onchange_partner_id(self,cr,uid,ids,partner_id):
        #the boolean "Apply the member price" should be set to TRUE or FALSE when the partner is changed in regard of the membership state of him.
        member_state = False
        if partner_id:
            partner_info = self.pool.get('res.partner').browse(cr, uid,partner_id)
            if partner_info.alert_legalisations:
                raise osv.except_osv('Error!',partner_info.alert_explanation or 'Partner is not valid')
            if partner_info.membership_state == 'none':
                member_state = False
            else:
                member_state = True
        return {'value':{'member_price' : member_state}}

    def onchange_warranty_product_id(self,cr,uid,ids,prod_id):
        warranty_price= False
        if prod_id:
            prod_info = self.pool.get('product.product').browse(cr, uid,prod_id)
            warranty_price=prod_info.list_price
        return {'value':{'warranty' : warranty_price}}

    _columns = {
        'id': fields.integer('ID', readonly=True),
        'type_id' : fields.many2one('cci_missions.dossier_type','Related Type of Carnet',required=True),
        'creation_date' : fields.date('Emission Date',required=True),
        'validity_date' : fields.date('Validity Date',required=True),
        'partner_id': fields.many2one('res.partner','Partner',required=True),
        'holder_name' : fields.char('Holder Name',size=50),
        'holder_address' : fields.char('Holder Address',size=50),
        'holder_city' : fields.char('Holder City',size=50),
        'representer_name' : fields.char('Representer Name',size=50),
        'representer_address' : fields.char('Representer Address',size=50),
        'representer_city' : fields.char('Representer City',size=50),
        'usage_id': fields.many2one('cci_missions.ata_usage','Usage',required=True),
        'goods': fields.char('Goods',size=80),
        'area_id': fields.many2one('cci.country','Area',required=True,domain=[('valid4ata','=',True)]),
        'insurer_agreement' : fields.char('Insurer Agreement',size=50),
        'own_risk' : fields.boolean('Own Risks'),
        'goods_value': fields.float('Goods Value',required=True),
        'double_signature' : fields.boolean('Double Signature'),
        'initial_pages' : fields.integer('Initial Number of Pages',required=True),
        'additional_pages' : fields.integer('Additional Number of Pages'),
        'warranty':fields.float('Warranty',readonly=True),
        'warranty_product_id': fields.many2one('product.product','Related Warranty Product',required=True),
        'return_date' : fields.date('Date of Return'),
        'state':fields.selection([('draft','Draft'),('created','Created'),('pending','Pending'),('dispute','Dispute'),('correct','Correct'),('closed','Closed')],'State',required=True,readonly=True),
        'ok_state_date' : fields.date('Date of Closure'),
        'federation_sending_date' : fields.date('Date of Sending to the Federation', readonly=True),
        'name' : fields.char('Name',size=50,required=True),
        'partner_insurer_id': fields.function(_get_insurer_id, method=True,string='Insurer ID of the Partner',readonly=True),
        'partner_member_state': fields.function(_get_member_state, method=True,selection=STATE,string='Member State of the Partner',readonly=True,type="selection"),
        'member_price' : fields.boolean('Apply the Member Price'),
        'product_ids': fields.one2many('product.lines', 'product_line_id', 'Products'),
        'letter_ids':fields.one2many('cci_missions.letters_log','ata_carnet_id','Letters'),
        'sub_total': fields.function(_tot_products, method=True, string='Subtotal of Extra Products',type="float"),
        "invoice_id":fields.many2one("account.invoice","Invoice"),
    }

    _defaults = {
        'own_risk' : lambda *b : False,
        'double_signature' : lambda *b : False,
        'state' : lambda *a : 'draft',
        'validity_date' : _default_validity_date,
        'name': lambda *args: '/',
        'creation_date': lambda *a: time.strftime('%Y-%m-%d'),
    }
    _constraints = [(check_ata_carnet, 'Error: Please Select (Own Risk) OR ("Insurer Agreement" and "Parnters Insure id" should be greater than Zero)', ['own_risk','insurer_agreement','partner_insurer_id'])]

cci_missions_ata_carnet()

class cci_missions_letters_log(osv.osv):
    _name = 'cci_missions.letters_log'
    _description = 'cci_missions.letters_log'
    _rec_name = 'date'
    _columns = {
        'ata_carnet_id' : fields.many2one('cci_missions.ata_carnet','Related ATA Carnet',required=True),
        'letter_type' :  fields.selection([('Rappel avant echeance','Rappel avant echeance'),('Rappel apres echeance','Rappel apres echeance'),('Suite lettre A','Suite lettre A'),('Suite lettre C','Suite lettre C'),('Suite lettre C1','Suite lettre C1'),('Suite lettre I','Suite lettre I'),('Demande de remboursement','Demande de remboursement'),('Rappel a remboursement','Rappel a remboursement'),('Mise en demeure','Mise en demeure')],'Type of Letter',required=True),
        'date' : fields.date('Date of Sending',required=True),
    }
    _defaults = {
        'date': lambda *args: time.strftime('%Y-%m-%d')
    }

cci_missions_letters_log()

class product_lines(osv.osv):
    _name = "product.lines"
    _description = "Product Lines"

    def create(self, cr, uid, vals, *args, **kwargs):
        if vals['product_id']:
            accnt_dict = {}
            data_product = self.pool.get('product.product').browse(cr,uid,vals['product_id'])
            a =  data_product.product_tmpl_id.property_account_income.id
            if not a:
                a = data_product.categ_id.property_account_income_categ.id
            accnt_dict['account_id']=a
            vals.update(accnt_dict)
        return super(product_lines,self).create(cr, uid, vals, *args, **kwargs)

    def write(self, cr, uid, ids,vals, *args, **kwargs):
        data_product_line= self.pool.get('product.lines').browse(cr,uid,ids[0])
        if (not data_product_line.product_id.id == vals['product_id']):
            accnt_dict = {}
            data_product = self.pool.get('product.product').browse(cr,uid,vals['product_id'])
            a =  data_product.product_tmpl_id.property_account_income.id
            if not a:
                a = data_product.categ_id.property_account_income_categ.id
            accnt_dict['account_id']=a
            vals.update(accnt_dict)
        return super(product_lines,self).write( cr, uid, ids,vals, *args, **kwargs)

    def _product_subtotal(self, cr, uid, ids, name, args, context=None):
        res = {}
        for line in self.browse(cr, uid, ids):
            res[line.id] = round(line.price_unit * line.quantity)
        return res

    def product_id_change(self, cr, uid, ids,product_id,):
        price_unit=uos_id=prod_name=data_partner=False
        if product_id:
            data_product = self.pool.get('product.product').browse(cr,uid,product_id)
            uos_id=data_product.uom_id.id
            price=self.pool.get('product.product').price_get(cr,uid,[product_id])
            price_unit=price[product_id]
            prod_name=data_product.name
        return {'value': {
            'uos_id': uos_id,
            'price_unit': price_unit,
            'name':prod_name,
            }
        }

    _columns = {
        'name': fields.char('Description', size=256, required=True),
        'product_line_id': fields.many2one('cci_missions.ata_carnet', 'Product Ref',select=True),
        'dossier_product_line_id': fields.many2one('cci_missions.dossier', 'Product Ref',select=True),
        'uos_id': fields.many2one('product.uom', 'Unit', ondelete='set null'),
        'product_id': fields.many2one('product.product', 'Product', ondelete='set null',required=True),
        'price_unit': fields.float('Unit Price', required=True, digits=(16,2)),
        'price_subtotal': fields.function(_product_subtotal, method=True, string='Subtotal'),
        'quantity': fields.float('Quantity', required=True),
        'account_id' : fields.many2one('account.account', 'Account', required=True),
    }
    _defaults = {
        'quantity': lambda *a: 1,
    }
product_lines()


class Product(osv.osv):
    '''Product'''
    _inherit = 'product.product'

    #this function will have to be corrected in order to match the criteria grid of the CCI
    def price_get(self, cr, uid, ids, ptype='list_price',context={}):

        res = {}
        product_uom_obj = self.pool.get('product.uom')
        # force_member works for forcing member price if partner is non member, same reasonning for force_non_member
        for product in self.browse(cr, uid, ids, context=context):
            if ptype == 'member_price':
                res[product.id] = product['list_price']
                if context and ('partner_id' in context):
                    state = self.pool.get('res.partner').browse(cr, uid, [context['partner_id']])[0].membership_state
                    if (state in ['waiting','associated','free','paid','invoiced']):
                        res[product.id] = product['member_price']
                if context and ('force_member' in context):
                    if context['force_member']:
                        res[product.id] = product['member_price']
                if context and ('force_non_member' in context):
                    if context['force_non_member']:
                        res[product.id] = product['list_price']
            else:
                res[product.id] = product[ptype] or 0.0
                if ptype == 'list_price':
                    res[product.id] = (res[product.id] * product.price_margin) + \
                            product.price_extra
            if 'uom' in context:
                uom = product.uos_id or product.uom_id
                res[product.id] = product_uom_obj._compute_price(cr, uid,
                        uom.id, res[product.id], context['uom'])

        for product in self.browse(cr, uid, ids, context=context):
            #change the price only for ATA originals
            if product.name.find('ATA - original') != -1:
                if context and ('value_goods' in context):
                    if context['value_goods'] < 25000:
                        res[product.id] = res[product.id] + context['value_goods']*0.008903875
                    elif 25000 <= context['value_goods'] < 75000 :
                        res[product.id] = res[product.id] + context['value_goods']*0.006937375
                    elif 75000 <= context['value_goods'] < 250000 :
                        res[product.id] = res[product.id] + context['value_goods']*0.004446475
                    else:
                        res[product.id] = res[product.id] + context['value_goods']*0.002764025
                if context and ('double_signature' in context):
                    if context['double_signature'] == False:
                        res[product.id] = res[product.id] + 5.45

            #change the price only for warranty own risk on ATA carnet
            if product.name.find('ATA - Own Risk Warranty') != -1:
                if context and ('value_goods' in context):
                    if context['value_goods'] > 15000:
                        res[product.id] = round(context['value_goods']*0.03)

        return res

Product()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

