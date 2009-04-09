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

form = """<?xml version="1.0"?>
<form string="Switch Values">
    <label string="Are you sure you want to switch debit-credit for selected entries?"/>
</form>
"""
fields = {}

class switch_debit_credit(wizard.interface):
    def _open_lines(self, cr, uid, data, context):

        pool_obj = pooler.get_pool(cr.dbname)

        model_data_ids = pool_obj.get('ir.model.data').search(cr,uid,[('model','=','ir.ui.view'),('name','=','view_move_form')])
        resource_id = pool_obj.get('ir.model.data').read(cr,uid,model_data_ids,fields=['res_id'])[0]['res_id']

        data['new_ids']=[]
        for id in data['ids']:

            ids_lines=pool_obj.get('account.move.line').search(cr,uid,[('move_id','=',id)])
            move_id=False

            for line_id in ids_lines:

                vals=pool_obj.get('account.move.line').read(cr, uid,line_id)

                vals['state']='draft'
                temp =vals['debit']
                vals['debit']=vals['credit']
                vals['credit']=temp
                del vals['id']
                del vals['move_id']
                vals['reconcile_id']= False
                if move_id:
                    vals['move_id']=move_id
                for field in vals:
                    if isinstance(vals[field],tuple):
                        vals[field]=vals[field][0]

                new_id=pool_obj.get('account.move.line').create(cr, uid, vals, context)
                obj_move_line=pool_obj.get('account.move.line').browse(cr,uid,new_id)
                if not move_id:
                    move_id=obj_move_line.move_id.id

            data['new_ids'].append(move_id)


        result= {
            'domain': "[('id','in', ["+','.join(map(str,data['new_ids']))+"])]",
            'name': 'Entries',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'views': [(False,'tree'),(resource_id,'form')],
            'type': 'ir.actions.act_window'
        }
        return result

    states = {
        'init' : {
            'actions' : [],
            'result' : {'type' : 'form' , 'arch' : form,'fields' : fields,'state' : [('end','No'),('open','Yes')]}
        },
        'open': {
            'actions': [],
            'result': {'type':'action', 'action':_open_lines, 'state':'end'}
            }
    }

switch_debit_credit("cci_debit_credit_switch")
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

