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

import time
import netsvc
from tools.misc import UpdateableStr, UpdateableDict
import pooler

import wizard
from osv import osv

arch = UpdateableStr()
fields = UpdateableDict()


def get_default(val):
    def fct(uid, data, state):
        return val
    return fct


def _get_cases(self, cr, uid, data, context):
    wrk_obj=pooler.get_pool(cr.dbname).get('mrp.production.workcenter.line').browse(cr,uid,data['id'])
    prod_obj=pooler.get_pool(cr.dbname).get('product.product').browse(cr,uid,wrk_obj.production_id.product_id.id)
    fields.clear()

    arch_lst = ['<?xml version="1.0"?>', '<form string="Quality Testing">']

    arch_lst.append('<field name="test_date"/>')
    fields['test_date'] = {'string':'Testing Date','type':'date','default': get_default(time.strftime('%Y-%m-%d'))}

    arch_lst.append('<field name="tester" colspan="1"/>')
    fields['tester'] = {'string': 'Tester','type': 'many2one', 'relation': 'hr.employee'}

    arch_lst.append('<field name="product"/>')
    fields['product'] = {'string': 'Product','readonly':True,
                    'type': 'many2one', 'relation': 'product.product',
                    'default':get_default(prod_obj.id)}
    arch_lst.append('\n')

    if prod_obj.production_test:

        for case in prod_obj.production_test:
            arch_lst.append('<label colspan="4" string="%s :" />' % case.name.name)
            arch_lst.append('\n')
            arch_lst.append('<separator colspan="4"/>')
            arch_lst.append('\n')
            arch_lst.append('<field name="min%s" colspan="1"/>' % (case.name.id,))
            fields['min'+'%s'%case.name.id]={'string':'Min Limit',
                                                    'type':'float','readonly':True,'default':get_default(case.min_limit)}
            arch_lst.append('<field name="max%s" colspan="1"/>' % (case.name.id,))
            fields['max'+'%s'%case.name.id]={'string':'Max Limit',
                                                    'type':'float','readonly':True,'default':get_default(case.max_limit)}
            arch_lst.append('<field name="actual%s" colspan="1"/>' % (case.name.id,))
            fields['actual'+'%s'%case.name.id]={'string':'Actual','type':'float'}
            arch_lst.append('<field name="uom%s" colspan="1"/>' % (case.name.id,))
            fields['uom'+'%s'%case.name.id] = {'string': 'UOM','readonly':True,
                        'type': 'many2one', 'relation': 'product.uom',
                        'default':get_default(case.uom.id)}

            arch_lst.append('<field name="active%s" colspan="1"/>' % (case.name.id,))
            fields['active'+'%s'%case.name.id] = {'string': 'Active',
                        'type': 'boolean'}
            arch_lst.append('\n')

    arch_lst.append('\n')
    arch_lst.append('</form>')
    arch.string = ''.join(arch_lst)
    return {}

def check(self, cr, uid, data, context):
    test_obj=pooler.get_pool(cr.dbname).get('testing.result')
    test_config=pooler.get_pool(cr.dbname).get('quality.test.config')
    wrk=pooler.get_pool(cr.dbname).get('mrp.production.workcenter.line')
    wrk_obj=wrk.browse(cr,uid,data['id'])
    prod_obj=pooler.get_pool(cr.dbname).get('product.product').browse(cr,uid,wrk_obj.production_id.product_id.id)

    if prod_obj.production_test:
        flag=False
        res={}
        res={'type':'in_prod','product':data['form']['product'],'tester':data['form']['tester'],'test_date':data['form']['test_date']}
        test_id=test_obj.create(cr,uid,res)

        for case in prod_obj.production_test:

            actual=data['form']['actual%s'%(case.name.id,)]
            min=data['form']['min%s'%(case.name.id,)]
            max=data['form']['max%s'%(case.name.id,)]

            if data['form']['active%s'%(case.name.id,)]:
                if actual> 0.00:
                    val={}
                    if (actual >=min and actual <= max):
                       state='accepted'
                    else:
                       state='rejected'
                       flag=True
                    val={'name':case.name.id,'min_limit':case.min_limit,'max_limit':case.max_limit,'uom':case.uom.id,
                             'actual_val':actual,'state':state,'test_id':test_id}
                    test_config.create(cr,uid,val)

        if flag:
            wrk.write(cr,uid,data['id'],{'qlty_test_reject':True})
            wrk.write(cr,uid,data['id'],{'qlty_test_accept':False})
        else:
            wrk.write(cr,uid,data['id'],{'qlty_test_accept':True})
            wrk.write(cr,uid,data['id'],{'qlty_test_reject':False})

    return {}

class wizard_qty_test_prod(wizard.interface):

    states = {
        'init': {
            'actions': [_get_cases],
            'result': {'type':'form', 'arch':arch, 'fields':fields, 'state':[('end','Cancel'),('ok','OK')]}
        },
        'ok': {
            'actions': [check],
            'result': {'type': 'state', 'state': 'end'},
        }

    }
wizard_qty_test_prod('qty_test_prod')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: