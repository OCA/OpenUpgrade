##############################################################################
#
# Copyright (c) 2005-2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
#
# $Id: make_invoice.py 1070 2005-07-29 12:41:24Z nicoe $
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

import wizard
import netsvc
import pooler

from osv import fields, osv
form = """<?xml version="1.0"?>
<form string="Inovoice Grouped">
    <field name="nbr_invoice"/>
</form>
"""
fields = {
      'nbr_invoice': {'string':'Invoice Grouped', 'type':'char', 'readonly':True},
          }
def _group_invoice(self, cr, uid, data, context):
    pool_obj=pooler.get_pool(cr.dbname)
    obj_inv=pool_obj.get('account.invoice')
    state = 'draft'
    cr.execute("select partner_id,date_invoice,id from account_invoice where state=%s and type in ('out_invoice','in_invoice') group by partner_id,id,date_invoice", ('draft',))
    a=cr.fetchall()
    a.sort()
    ls=([i[0] for i in a])
    ls=list(set([i for i in ls]))
    ls.sort()
    lst=[]
    for id in ls:
        data={}
        in_lst=[]
        in_lst2=[]
        in_dict={}
        data['p_id']=id
        flag=1
        for t in a:
            if id==t[0]:
                if flag:
                    in_dict['date']=t[1]
                    in_lst.append(t[2])
                    flag=0
                else:
                    if in_dict['date']==t[1]:
                        in_lst.append(t[2])
                    else:
                        in_dict['inv_id']=in_lst
                        t_in_dict=in_dict.copy()
                        in_lst2.append(t_in_dict)
                        in_dict['date']=t[1]
                        in_lst=[]
                        in_lst.append(t[2])
            else:
                if id>t[0]:
                    continue
                data['invoices']=in_lst2
                in_dict['inv_id']=in_lst
                in_lst2.append(in_dict)
                lst.append(data)
                break
    in_dict['inv_id']=in_lst
    in_lst2.append(in_dict)
    data['invoices']=in_lst2
    lst.append(data)
    part_count = 0
    list_invoice = []
    for l in lst:
        part_count = part_count + 1
        line_list =[]
        count = 0
        for data in l['invoices']:
            customer_ref = ''
            line_obj = pool_obj.get('account.invoice.line')
            id_note=line_obj.create(cr,uid,{'name':customer_ref,'state':'text','sequence':count}) # a new line of type 'note' with all the customer reference (if there is/are one/several on some invoices of this bloc)
            count=count+1
            line_list.append(id_note)
            data_inv=obj_inv.browse(cr,uid,data['inv_id'])
            notes = ''
            for m in data_inv:
                if m.reference:
                    customer_ref = customer_ref +' ' + m.reference
                if m.comment:
                    notes = (notes + m.comment)
                for line in m.invoice_line:
                    #all the lines copied and ordered by name (the new name)
                    if m.name:
                        name = m.name +' '+ line.name
                    else:
                        name = line.name
                    #pool_obj.get('account.invoice.line').write(cr,uid,line.id,{'name':name,'sequence':count})
                    inv_line = pool_obj.get('account.invoice.line').create(cr, uid, {'name': name,'account_id':line.account_id.id,'price_unit': line.price_unit,'quantity': line.quantity,'discount': False,'uos_id': line.uos_id.id,'product_id':line.product_id.id,'invoice_line_tax_id': [(6,0,line.invoice_line_tax_id)],'note':False,'sequence' : count})
                    count=count+1
                    line_list.append(inv_line)
                obj_inv.write(cr,uid,m.id,{'state':'cancel'})
            line_obj.write(cr,uid,id_note,{'name':customer_ref})
            id_note1=line_obj.create(cr,uid,{'name':notes,'state':'text','sequence':count})# a new line of type 'note' with all the old invoice note
            count=count+1
            line_list.append(id_note1)
            id_linee=line_obj.create(cr,uid,{'state':'line','sequence':count}) #a new line of type 'line'
            count=count+1
            line_list.append(id_linee)
            id_stotal=line_obj.create(cr,uid,{'name':'Subtotal','state':'subtotal','sequence':count})#a new line of type 'subtotal'
            count=count+1
            line_list.append(id_stotal)
        inv = {
                'name': 'Grouped Invoice',
                'origin': 'Grouped Invoice',
                'type': 'out_invoice',
                'reference': False,
                'account_id': m.account_id.id,
                'partner_id': m.partner_id.id,
                'address_invoice_id':m.address_invoice_id.id,
                'address_contact_id':m.address_contact_id.id,
                'invoice_line': [(6,0,line_list)],
                'currency_id' :m.currency_id.id,# 1
                'comment': "",
                'payment_term':m.payment_term.id,
            }
        inv_id = obj_inv.create(cr, uid, inv)
        list_invoice.append(inv_id)
    return {'nbr_invoice' : str(part_count),'invoice_ids':list_invoice}

class group_invoice(wizard.interface):
    def _list_invoice(self, cr, uid, data, context):
        pool_obj = pooler.get_pool(cr.dbname)
        model_data_ids = pool_obj.get('ir.model.data').search(cr,uid,[('model','=','ir.ui.view'),('name','=','invoice_form')])
        resource_id = pool_obj.get('ir.model.data').read(cr,uid,model_data_ids,fields=['res_id'])[0]['res_id']
        return {
            'domain': "[('id','in', ["+','.join(map(str,data['form']['invoice_ids']))+"])]",
            'name': 'Invoices',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.invoice',
            'views': [(False,'tree'),(resource_id,'form')],
            'context': "{'type':'out_invoice'}",
            'type': 'ir.actions.act_window'
        }
    states = {
        'init' : {
               'actions' : [_group_invoice],
               'result': {'type': 'form', 'arch': form, 'fields': fields, 'state':[('end','Ok'),('open','Open')]}
            },
        'open': {
            'actions': [],
            'result': {'type':'action', 'action':_list_invoice, 'state':'end'}
            }
    }
group_invoice("account.group_invoice")
