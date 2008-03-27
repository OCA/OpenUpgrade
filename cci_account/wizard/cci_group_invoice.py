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
    cr.execute("select partner_id,id,date_invoice from account_invoice where state=%s group by partner_id,id,date_invoice", ('draft',))
    a=cr.fetchall()
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
                    in_dict['date']=t[2]
                    in_lst.append(t[1])
                    flag=0
                else:
                    if in_dict['date']==t[2]:
                        in_lst.append(t[1])
                    else:
                        in_dict['inv_id']=in_lst
                        t_in_dict=in_dict.copy()
                        in_lst2.append(t_in_dict)
                        in_dict['date']=t[2]
                        in_lst=[]
                        in_lst.append(t[1])
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
    print lst
    return {'nbr_invoice' : str(10)}

class group_invoice(wizard.interface):
    states = {
        'init' : {
               'actions' : [_group_invoice],
               'result': {'type': 'form', 'arch': form, 'fields': fields, 'state':[('end','Ok')]}
            },
    }
group_invoice("account.group_invoice")
