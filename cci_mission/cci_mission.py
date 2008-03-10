
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

from osv import fields, osv
import time

class res_partner(osv.osv):
    _inherit = 'res.partner'
    _description = 'res.partner'
    _columns = {
        'asker_name': fields.char('Asker Name',size=50),
        'asker_address': fields.char('Asker Address',size=50),
        'asker_zip_id': fields.many2one('res.partner.zip','Asker Zip Code'),
        'sender_name': fields.char('Sender Name',size=50),
        'insurer_id' : fields.integer('Insurer ID'),
    }

res_partner()

class cci_missions_site(osv.osv):
    _name = 'cci_missions.site'
    _description = 'cci_missions.site'
    _columns = {
        'name' : fields.char('Name of the Site',size=50,required=True)
                }

cci_missions_site()

class cci_missions_embassy_folder(osv.osv):
    _name = 'cci_missions.embassy_folder'
    _description = 'cci_missions.embassy_folder'
    _inherits = {'crm.case': 'crm_case_id'}

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
        'member_price' : fields.boolean('Apply the Member Price'),
        'customer_reference' : fields.char('Folders Reference for the Customer',size=30),
        'destination_id' : fields.many2one('res.country','Destination Country'),
        'link_ids': fields.one2many('cci_missions.dossier','embassy_folder_id','Linked Documents'),
        'internal_note': fields.text('Internal Note'),
        'invoice_note':fields.text('Note to Display on the Invoice',help='to display as the last embassy_folder_line of this embassy_folder.'),
        'embassy_folder_line_ids' : fields.one2many('cci_missions.embassy_folder_line','folder_id','Details'),
        'site_id': fields.many2one('cci_missions.site','Site'),
                }
    _defaults = {
         'section_id': lambda obj, cr, uid, context: obj.pool.get('crm.case.section').search(cr, uid, [('name','=','Embassy Folder')])[0],
                }
    _constraints = [(check_folder_line, 'Error: Only One Embessy Folder line allowed for each type!', [])]

cci_missions_embassy_folder()

class cci_missions_embassy_folder_line (osv.osv):
    _name = 'cci_missions.embassy_folder_line'
    _description = 'cci_missions.embassy_folder_line '

    _columns = {
        'name' : fields.char('Description',size=50,required=True),
        'folder_id' : fields.many2one('cci_missions.embassy_folder','Related Embassy Folder',required=True),
        'courier_cost' : fields.float('Couriers Costs'),
        'customer_amount' : fields.float('Invoiced Amount'),
        'tax_rate': fields.many2one('account.tax','Tax Rate'),#should be corect
        'type' : fields.selection([('CBA','CBA'),('Ministry','Ministry'),('Embassy  Consulate','Embassy Consulate'),('Translation','Translation'),('Administrative','Administrative'),('Travel Costs','Travel Costs'),('Others','Others')],'Type'),
                }

cci_missions_embassy_folder_line()

class cci_missions_certificate_type(osv.osv):
    _name = 'cci_missions.certificate_type'
    _description = 'cci_missions.certificate_type'
    _columns = {
        'code' : fields.char('Code',size=2,required=True),
        'name' : fields.char('Description',size=30,required=True),
        'original_product_id' : fields.many2one('product.product','Reference for Original Copies',required=True,help='for the association with a pricelist'),
        'copy_product_id' : fields.many2one('product.product','Reference for Copies',required=True,help='for the association with a pricelist'),
        'site_id' : fields.many2one('cci_missions.site','Site',required=True),
        'sequence_id' : fields.many2one('ir.sequence','Sequence',required=True,help='for association with a sequence'),
        'section' : fields.selection([('certificate','Certificate'),('legalization','Legalization'),('ATA Carnet','ATA Carnet')],'Type',required=True),
                }

cci_missions_certificate_type()

class cci_missions_dossier(osv.osv):
    _name = 'cci_missions.dossier'
    _description = 'cci_missions.dossier'

    def create(self, cr, uid, vals, *args, **kwargs):
        #overwrite the create: if the text_on_invoice field is empty then fill it with name + destination_id.name + (quantity_original)
        if not vals['text_on_invoice']:
            invoice_text = vals['name']
            if vals['destination_id']:
                destination_data = self.pool.get('res.country').browse(cr,uid,vals['destination_id'])
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
                if partner_info.address!=[]:
                    for add in partner_info.address:
                        if add.type=='default':
                           sender_name=add.name
                           break

            else:
                sender_name=partner_info.sender_name
        result = {'value': {
            'asker_name': asker_name,
            'sender_name': sender_name}
        }
        return result

    def _amount_total(self, cr, uid, ids, name, args, context=None):#today
        #should be check
        res ={}
        data_dosseir = self.browse(cr,uid,ids)
        for data in data_dosseir:
            qty_org = data.quantity_original
            qty_copy = data.quantity_copies
            cost_org = data.type_id.original_product_id.standard_price
            cost_copy = data.type_id.copy_product_id.standard_price
            subtotal =  data.sub_total
            total = ((cost_org * qty_org ) + (cost_copy * qty_copy) + subtotal)
            res[data.id] = total
        return res

    def _amount_subtotal(self, cr, uid, ids, name, args, context=None):
        #should be check
        sum = 0
        res = {}
        data_dosseir = self.browse(cr,uid,ids)
        for data in data_dosseir:
            for product in data.product_ids:
                sum = sum + product.standard_price
            res[data.id] = sum
        return res

    _columns = {
        'name' : fields.char('Reference',size=20,required=True),
        'type_id' : fields.many2one('cci_missions.certificate_type','Certificate Type',required=True),
        'date' : fields.date('Creation Date',required=True),
        'order_partner_id': fields.many2one('res.partner','Billed Customer',required=True),
        'asker_name':fields.char('Asker Name',size=50),
        'sender_name':fields.char('Sender Name',size=50),
        'to_bill':fields.boolean('To Be Billed'),
        'state':fields.selection([('confirmed','Confirmed'),('canceled','Canceled'),('invoiced','Invoiced')],'State',),
        'goods':fields.char('Goods Description',size=100),
        'goods_value':fields.float('Value of the Sold Goods'),#Monetary; must be greater than zero
        'destination_id':fields.many2one('res.country','Destination Country'),
        'embassy_folder_id':fields.many2one('cci_missions.embassy_folder','Related Embassy Folder'),
        'quantity_copies':fields.integer('Number of Copies'),
        'quantity_original' : fields.integer('Quantity of Originals',required=True), #today
        'total':fields.function(_amount_total, method=True, string='Total', store=True),#readonly, sum of the price for copies, originals and extra_products
        'sub_total':fields.function(_amount_subtotal, method=True, string='Sub Total for Extra Products', store=True),#readonly, sum of the extra_products
        'text_on_invoice':fields.text('Text to Display on the Invoice'),
        'product_ids' : fields.many2many('product.product','dossier_product_rel','dossier_id','product_id','Products')

                }
    _defaults = {
        'name': lambda *args: '/',
        'date': lambda *a: time.strftime('%Y-%m-%d'),
        'to_bill' : lambda *b : True,
        'state' : lambda *a : 'confirmed',
        'quantity_original' : lambda *a : 1
    }


cci_missions_dossier()

class cci_missions_custom_code(osv.osv):
    _name= 'cci_missions.custom_code'
    _desctiption = 'cci_missions.custom_code'
    _columns = {
        'name' : fields.char('Name',size=8,required=True),
        'meaning' : fields.char('Meaning',size=250,required=True),
        'official' : fields.boolean('Official Code'),#Invisible ?
                }
    _defaults = {
        'official': lambda *a: False,
    }

cci_missions_custom_code()

class cci_missions_certificate(osv.osv):
    _name = 'cci_missions.certificate'
    _description = 'cci_missions.certificate'
    _inherits = {'cci_missions.dossier': 'dossier_id' }


    def get_certification_details(self, cr, uid, ids,order_partner_id):
        result={}
        asker_name=False
        sender_name=False
        asker_address=False
        zip=False

        if order_partner_id:
            partner_info = self.pool.get('res.partner').browse(cr, uid,order_partner_id)

            if not partner_info.asker_name:

                asker_name=partner_info.name
            else:
                asker_name=partner_info.asker_name

            if not partner_info.sender_name:

                if partner_info.address!=[]:
                    for add in partner_info.address:
                        if add.type=='default':
                           sender_name=add.name
                           break
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
#        Overwrite the name fields to set next sequence according to the sequence in the certification type (type_id)
        if vals['type_id']:
            data = self.pool.get('cci_missions.certificate_type').browse(cr, uid,vals['type_id'])
            seq = self.pool.get('ir.sequence').get(cr, uid,data.sequence_id.code)

            if seq:
                vals.update({'name': seq})
        return super(osv.osv,self).create(cr, uid, vals, *args, **kwargs)

    _columns = {
        'dossier_id' : fields.many2one('cci_missions.dossier','Dossier'),
        'asker_address' : fields.char('Asker Address',size=50),#by default, res.partner->asker_adress or, res_partner.address[default]->street
        'asker_zip_id' : fields.many2one('res.partner.zip','Asker Zip Code'),#by default, res.partner->asker_zip_id or, res_partner.address[default]->zip_id
        'special_reason' : fields.selection([('none','None'),('Commercial Reason','Commercial Reason'),('Substitution','Substitution')],'For special cases'),
        'legalization_ids' : fields.one2many('cci_missions.legalization','certificate_id','Related Legalizations'),
        'customs_ids' : fields.many2many('cci_missions.custom_code','certificate_custome_code_rel','certificate_id','custom_id','Custom Codes'),
        'sending_SPF': fields.date('SPF Sending Date',help='Date of the sending of this record to the external database'),
        'origin_ids' : fields.many2many('res.country','certificate_country_rel','certificate_id','country_id','Origin Countries')
                }
    _defaults = {
        'special_reason': lambda *a: 'none',
    }

cci_missions_certificate()

class cci_missions_legalization(osv.osv):
    _name = 'cci_missions.legalization'
    _description = 'cci_missions.legalization'
    _inherits = {'cci_missions.dossier': 'dossier_id'}

    def get_legalization_details(self, cr, uid, ids,order_partner_id):
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
                if partner_info.address!=[]:
                  for add in partner_info.address:
                        if add.type=='default':
                           sender_name=add.name
                           break

            else:
                sender_name=partner_info.sender_name
        result = {'value': {
            'asker_name': asker_name,
            'sender_name': sender_name}
        }
        return result


    _columns = {
        'dossier_id' : fields.many2one('cci_missions.dossier','Dossier'),#added for inherits
        #'quantity_original' : fields.integer('Quantity of Originals',required=True),
        'certificate_id' : fields.many2one('cci_missions.certificate','Related Certificate'),
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
        'return_address' : fields.selection([('A la CCI','A la CCI'),('Au clent','Au client')],'Address of Return',required=True),#onchange
        'address_name_1' : fields.char('Company Name',size=80),
        'address_name_2' : fields.char('Contact Name',size=80),
        'address_street' : fields.char('Street',size=80),
        'address_city' : fields.char('City',size=80),
        'qtty_to_print' : fields.integer('Number of Sheets'),
        'partner_address_id' : fields.many2one('res.partner.address','Courier'),
                }

cci_missions_courier_log()


