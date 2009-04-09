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
import wizard
import netsvc
import pooler
import create_invoice_carnet
import create_invoice_embassy
import create_invoice
from event.wizard import make_invoice
import time
from osv import fields, osv

form = """<?xml version="1.0"?>
<form string="Inovoice Grouped">
    <field name="date_invoice"/>
    <newline/>
    <field name="period_id"/>
    <newline/>
    <field name="registration"/>
</form>
"""
fields = {
      'registration': {'string':'Include Events Registrations', 'type':'boolean' ,'default': lambda *a: False },
      'date_invoice': {'string':'Date Invoiced', 'type':'date' ,'default': lambda *a: time.strftime('%Y-%m-%d')},
      'period_id': {'string':'Force Period (keep empty to use current period)','type':'many2one','relation':'account.period'},
}
form_msg = """<?xml version="1.0"?>
<form string="Inovoice Grouped">
    <separator string="Invoices Grouped for Following Partners." colspan="4" />
    <newline/>
    <field name="message" nolabel="1" colspan="5"/>
</form>
"""
fields_msg = {
      'message': {'string':'','type':'text', 'readonly':True, 'size':'500'},
}

def _group_invoice(self, cr, uid, data, context):
    date_inv = data['form']['date_invoice']
    force_period = data['form']['period_id']
    today_date = time.strftime('%Y-%m-%d')
    pool_obj=pooler.get_pool(cr.dbname)
    obj_inv=pool_obj.get('account.invoice')
    dict_info=[]
    models=['cci_missions.certificate','cci_missions.legalization','cci_missions.embassy_folder','cci_missions.ata_carnet']
    if data['form']['registration']:
        models.append('event.registration')

    for model in models:
        if model=='cci_missions.embassy_folder' or model=='event.registration':
            model_ids=pool_obj.get(model).search(cr,uid,[('state','=','open')])
        else:
            model_ids=pool_obj.get(model).search(cr,uid,[('state','=','draft')])

        if model_ids:
            read_ids=pool_obj.get(model).read(cr,uid,model_ids,['partner_id','order_partner_id','date','creation_date','partner_invoice_id'])
            for element in read_ids:
                part_info={}
                if ('partner_id' in element) and element['partner_id']:
                    part_info['partner_id']=element['partner_id'][0]
                    part_info['id']=element['id']
                    part_info['model']=model

                if ('order_partner_id' in element) and element['order_partner_id']:
                    part_info['partner_id']=element['order_partner_id'][0]
                    part_info['id']=element['id']
                    part_info['model']=model

                if ('partner_invoice_id' in element) and element['partner_invoice_id']:
                    part_info['partner_id']=element['partner_invoice_id'][0]
                    part_info['id']=element['id']
                    part_info['model']=model

                if 'date' in element:
                    part_info['date']=element['date']

                if 'creation_date' in element:
                    part_info['date']=element['creation_date']

                if part_info:
                    dict_info.append(part_info)

    if not dict_info:
        data['form']['invoice_ids']=[]
        if data['form']['registration']:
            data['form']['message']="No invoices grouped  because no invoices for ATA Carnet, Legalizations, Certifications and (Embassy Folders and Registrations) are in 'Draft' state."
        else:
            data['form']['message']="No invoices grouped  because no invoices for ATA Carnet, Legalizations, Certifications and Embassy Folders are in 'Draft' state."
        return data['form']

    partner_ids = list(set([x['partner_id'] for x in dict_info]))
    partner_ids.sort()
    disp_msg=''

    list_invoice=[]
    for partner_id in partner_ids:
        partner=pool_obj.get('res.partner').browse(cr, uid,partner_id)
        final_info={}
        list_info=[]
        list_invoice_ids=[]
        self.invoice_info=[]
        for element in dict_info:
            final_info={}
            if element['partner_id']==partner_id:
                data={'model':element['model'],'form':{},'id':element['id'],'ids':[element['id']],'report_type': 'pdf'}
                final_info['ids']=[]
                final_info['date']=element['date'][0:10]

                if element['model']=='cci_missions.ata_carnet':
                    result=create_invoice_carnet._createInvoices(self,cr,uid,data,context)

                    if result['inv_rejected']>0 and result['inv_rej_reason']:
                        disp_msg +='\nFor Partner '+ partner.name +' On ATA Carnet with ' + result['inv_rej_reason']
                        continue
                    if result['invoice_ids']:
                        list_invoice_ids.append(result['invoice_ids'][0])
                        final_info['ids'].append(result['invoice_ids'][0])
                        list_info.append(final_info)
                        final_info={}
                        final_info['id']=element['id']
                        final_info['model']=element['model']
                        self.invoice_info.append(final_info)

                if element['model']=='cci_missions.embassy_folder':
                    result=create_invoice_embassy._createInvoices(self,cr,uid,data,context)

                    if result['inv_rejected']>0 and result['inv_rej_reason']:
                        disp_msg +='\nFor Partner '+ partner.name +' On Embassy Folder with ' + result['inv_rej_reason']
                        continue
                    if result['invoice_ids']:
                        list_invoice_ids.append(result['invoice_ids'][0])
                        final_info['ids'].append(result['invoice_ids'][0])
                        list_info.append(final_info)
                        final_info={}
                        final_info['id']=element['id']
                        final_info['model']=element['model']
                        self.invoice_info.append(final_info)

                if element['model'] in ('cci_missions.certificate','cci_missions.legalization'):
                    result=create_invoice._createInvoices(self,cr,uid,data,context)

                    if result['inv_rejected']>0 and result['inv_rej_reason']:
                        disp_msg +='\nFor Partner '+ partner.name +' On Certificate or Legalization with ' + result['inv_rej_reason']
                        continue
                    if result['invoice_ids']:
                        list_invoice_ids.append(result['invoice_ids'][0])
                        final_info['ids'].append(result['invoice_ids'][0])
                        list_info.append(final_info)
                        final_info={}
                        final_info['id']=element['id']
                        final_info['model']=element['model']
                        self.invoice_info.append(final_info)

                if element['model']=='event.registration':
                    result=make_invoice._makeInvoices(self,cr,uid,data,context)

                    if result['inv_rejected']>0 and result['inv_rej_reason']:
                        disp_msg +='\nFor Partner '+ partner.name +' On Event Registration ' + result['inv_rej_reason']
                        continue
                    if result['invoice_ids']:
                        list_invoice_ids.append(result['invoice_ids'][0])
                        final_info['ids'].append(result['invoice_ids'][0])
                        list_info.append(final_info)
                        final_info={}
                        final_info['id']=element['id']
                        final_info['model']=element['model']
                        self.invoice_info.append(final_info)

        done_date=[]
        date_id_dict={}
        done_date=list(set([x['date'] for x in list_info]))
        done_date.sort()
        final_list=[]
        for date in done_date:
            date_id_dict={}
            date_id_dict['date']=date
            date_id_dict['ids']=[]
            for item in list_info:
                if date==item['date']:
                    date_id_dict['ids'] +=item['ids']
            final_list.append(date_id_dict)

        count=0
        list_inv_lines=[]
        #marked

        if not final_list:
            continue
        for record in final_list:
            customer_ref = record['date']
            line_obj = pool_obj.get('account.invoice.line')
            id_note=line_obj.create(cr,uid,{'name':customer_ref,'state':'title','sequence':count})
            count=count+1
            list_inv_lines.append(id_note)
            data_inv=obj_inv.browse(cr,uid,record['ids'])
            notes = ''
            for invoice in data_inv:
                if invoice.reference:
                    customer_ref = customer_ref +' ' + invoice.reference
                if invoice.comment:
                    notes = (notes + ' ' + invoice.comment)

                for line in invoice.invoice_line:
                    if invoice.name:
                        name = invoice.name +' '+ line.name
                    else:
                        name = line.name
                    #pool_obj.get('account.invoice.line').write(cr,uid,line.id,{'name':name,'sequence':count})
#                    inv_line = line_obj.create(cr, uid, {'name': name,'account_id':line.account_id.id,'price_unit': line.price_unit,'quantity': line.quantity,'discount': False,'uos_id': line.uos_id.id,'product_id':line.product_id.id,'invoice_line_tax_id': [(6,0,line.invoice_line_tax_id)],'note':line.note,'sequence' : count})
                    inv_line = line_obj.create(cr, uid, {'name': name,'account_id':line.account_id.id,'price_unit': line.price_unit,'quantity': line.quantity,'discount': False,'uos_id': line.uos_id.id,'product_id':line.product_id.id,'invoice_line_tax_id': [(6,0,line.invoice_line_tax_id)],'note':line.note,'sequence' : count,'cci_special_reference': line.cci_special_reference})
                    count=count+1
                    list_inv_lines.append(inv_line)
    #            If we want to cancel ==> obj_inv.write(cr,uid,invoice.id,{'state':'cancel'}) here
    #            If we want to delete ==> obj_inv.unlink(cr,uid,list_invoice_ids) after new invoice creation.

            line_obj.write(cr,uid,[id_note],{'name':customer_ref})
            id_note1=line_obj.create(cr,uid,{'name':notes,'state':'text','sequence':count})# a new line of type 'note' with all the old invoice note
            count=count+1
            list_inv_lines.append(id_note1)
            id_linee=line_obj.create(cr,uid,{'state':'line','sequence':count}) #a new line of type 'line'
            count=count+1
            list_inv_lines.append(id_linee)
            id_stotal=line_obj.create(cr,uid,{'name':'Subtotal','state':'subtotal','sequence':count})#a new line of type 'subtotal'
            count=count+1
            list_inv_lines.append(id_stotal)
        #end-marked
        inv = {
                'name': 'Grouped Invoice - ' + partner.name,
                'origin': 'Grouped Invoice',
                'type': 'out_invoice',
                'reference': False,
                'account_id': invoice.account_id.id,
                'partner_id': invoice.partner_id.id,
                'address_invoice_id':invoice.address_invoice_id.id,
                'address_contact_id':invoice.address_contact_id.id,
                'invoice_line': [(6,0,list_inv_lines)],
                'currency_id' :invoice.currency_id.id,# 1
                'comment': "",
                'payment_term':invoice.payment_term.id,
                'date_invoice':date_inv or today_date,
                'period_id':force_period or False,
                'fiscal_position': invoice.partner_id.property_account_position.id
            }
        inv_id = obj_inv.create(cr, uid, inv)
        for item in self.invoice_info:
            pool_obj.get(item['model']).write(cr, uid,[item['id']], {'invoice_id' : inv_id})
        disp_msg +='\n'+ partner.name + ': '+ str(len(data_inv)) +' Invoice(s) Grouped.'
        list_invoice.append(inv_id)
        obj_inv.unlink(cr,uid,list_invoice_ids)
    data['form']['invoice_ids']=list_invoice
    data['form']['message']=disp_msg
    return data['form']

class mission_group_invoice(wizard.interface):
    def _list_invoice(self, cr, uid, data, context):
        pool_obj = pooler.get_pool(cr.dbname)
        model_data_ids = pool_obj.get('ir.model.data').search(cr,uid,[('model','=','ir.ui.view'),('name','=','invoice_form')])
        resource_id = pool_obj.get('ir.model.data').read(cr,uid,model_data_ids,fields=['res_id'])[0]['res_id']
        print "ici"
        return {
            'domain': "[('id','in', ["+','.join(map(str,data['form']['invoice_ids']))+"])]",
            'name': 'Invoices',
            'view_type': 'form',
            'view_mode': 'form,tree',
            'res_model': 'account.invoice',
            'views': [(resource_id,'form')],
            'context': "{'type':'out_invoice',}",
            'type': 'ir.actions.act_window'
        }
    states = {
        'init' : {
               'actions' : [],
               'result': {'type': 'form', 'arch': form, 'fields': fields, 'state':[('end','Cancel'),('open','Group Invoice')]}
            },
        'open': {
            'actions': [_group_invoice],
            'result': {'type':'form', 'arch': form_msg, 'fields': fields_msg, 'state':[('end','Ok'),('open_inv','Open Invoices')]}
            },
        'open_inv': {
            'actions': [],
            'result': {'type':'action', 'action':_list_invoice, 'state':'end'}
            }
    }
mission_group_invoice("cci_missions.make_invoice_common")
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

