# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
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
import copy
import pooler
import ir
from tools.translate import _

_form_init =  '''<?xml version="1.0"?>
        <form title="help for generation of variants">
        <separator string="help for variants creation" colspan="4"/>
            <field name="template_id"/>
            <field name="characteristic_ids"/>
        <separator string="message" colspan="4"/>
            <field name="message"/>
        </form>'''

_fields_init = {
        'template_id':{'string': 'template', 'type': 'many2one','relation':'product.product','domain':(('variants','=',False),)},
        'characteristic_ids': {'string': 'characteristic to combine', 'type': 'many2many','relation':'mrp.characteristic'},
        'message':{'string':'', 'type': 'char' ,'readonly':True,'size':'100'}
    }

# wizard for helping generation of variants
# give characteristics for a template, and the program will create all variants as combination of
# every characteristics in groups given

def combine(seqin):
    '''returns a list of all combinations of argument sequences.
for example: combine((1,2),(3,4)) returns
[[1, 3], [1, 4], [2, 3], [2, 4]]'''

    def rloop(seqin,listout,comb):
        '''recursive looping function'''
        if seqin:                       # any more sequences to process?
            for item in seqin[0]:
                newcomb=comb+[item]     # add next item to current comb
                # call rloop w/ rem seqs, newcomb
                rloop(seqin[1:],listout,newcomb)
        else:                           # processing last sequence
            listout.append(comb)        # comb finished, add to list
    listout=[]                      # listout initialization
    rloop(seqin,listout,[])         # start recursive process
    return listout


class fashion_help_wizard(wizard.interface):
    def _complete(self, cr, uid, data, context):
        def field_value(f):
                res=data['form'][f]
                if isinstance(res, list):
                    if len(res):
                        res=res[0][2]
                    else:
                        res=False
                return res

        newfields={
            'message': '',
            'template_id' : field_value('template_id'),
            'characteristic_ids' : field_value('characteristic_ids')
             }

        if field_value('template_id') and (field_value('characteristic_ids')):
            pool = pooler.get_pool(cr.dbname)
            template= pool.get('product.product').browse(cr, uid, field_value('template_id'))
            groups={}
            for char in pool.get('mrp.characteristic').browse(cr, uid,field_value('characteristic_ids')):
                if not char.group_id.id in groups :
                    groups[char.group_id.id]=()
                groups[char.group_id.id]=groups[char.group_id.id]+(char.id,)
            combi=combine(groups.values())
            if len(combi)>100:
                newfields['message']='too much variants (more than 100), check values.'
                return newfields

            newfields['message']= '%s variants of %s created' % (len(combi),template.name)
            for chars in combi:
                var_id=pool.get('product.product').copy(cr, uid,field_value('template_id'))
                pool.get('product.product').write(cr, uid,[var_id],{'characteristic_ids':[(6,0,chars,)]})
                return newfields
                # bom?
                #self.pool.get('product.product').create(cr,uid,{'id':var_id,'name':template.name,'type':'phantom'})
        else:
            newfields['message']= 'check data entries'
            return newfields

    states = {
        'init': {
            'actions': [],
            'result': {'type': 'form', 'arch':_form_init, 'fields':_fields_init,  'state':[('end','Quit'),('complete','create')]}
        },
        'complete': {
            'actions': [_complete],
            'result': {'type': 'state', 'state': 'init'}
        }
    }


fashion_help_wizard('fashion.help.wizard')