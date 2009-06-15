# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2009 Smile.fr. All Rights Reserved
#    authors: Raphaël Valyi, Xavier Fernandez
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


def next_step(context):
    index = context.get('next_step', False)
    context.update({'next_step': index+1 })
    model_list= context.get('step_list', False)
    model = 'sale.order.line'
    if index and model_list and index < len(model_list):
        model = model_list[index]
        return {
                'view_type': 'form',
                "view_mode": 'form',
                'res_model': model,
                'type': 'ir.actions.act_window',
                'target':'new',
                'context': context,
            }
    else:
        if context.get('active_id_object_type', False) == 'sale.order.line':
            return {
                    'type': 'ir.actions.act_window_close',
                }
        else:
            return {
                    'view_type': 'form',
                    "view_mode": 'form',
                    'res_model': 'sale.order.line',
                    'type': 'ir.actions.act_window',
                    'target':'new',
                    'res_id': context.get('sol_id', False),
                    'buttons': True,
                    'context': context,
                }
        


class sale_product_multistep_configurator_configurator(osv.osv_memory):
    _name = "sale_product_multistep_configurator.configurator"
    _columns = {}
        
sale_product_multistep_configurator_configurator()

class sale_product_multistep_configurator_configurator_step(osv.osv):
    _name = "sale_product_multistep_configurator.configurator.step"
    _columns = {
                'name': fields.char('Value Name', size=64, select=1), #TODO related?
                'model_id': fields.many2one('ir.model', 'Object ID', required=True, select=True),
                'sequence' : fields.integer('Sequence', help="Determine in which order step are executed"),
                }
    _order = 'sequence'
    
sale_product_multistep_configurator_configurator_step()


class ir_actions_act_window(osv.osv):
    _inherit = 'ir.actions.act_window'

    def read(self, cr, uid, ids, fields=None, context={}, load='_classic_read'):

        if isinstance(ids, (int, long)):
            read_ids = [ids]
        else:
            read_ids = ids
         
        result = super(ir_actions_act_window, self).read(cr, uid, read_ids, ['context'], context, load)[0]

        try:
            if eval(result['context']).get('multistep_wizard_dispatch', False):
                configurator_context = eval(result['context'])
                
                list_of_step_ids = self.pool.get('sale_product_multistep_configurator.configurator.step').search(cr, uid, [])
                list_of_steps = self.pool.get('sale_product_multistep_configurator.configurator.step').read(cr, uid, list_of_step_ids)
                model_names = [i['model_id'][1] for i in list_of_steps]
                action_id = self.search(cr, uid, [('res_model', '=', model_names[0])])[0]
                
                result = super(ir_actions_act_window, self).read(cr, uid, action_id, fields, context, load)
                configurator_context.update(eval(result['context']))#used to pass active_id_object_type and make sure we will dispatch here again eventually, see corresponding act_window      
                configurator_context.update({'next_step':1})#TODO have a back system + TODO be dynamic here
                configurator_context.update({'step_list': model_names})
                result['context'] = unicode(configurator_context)
                return result
            else:
                return super(ir_actions_act_window, self).read(cr, uid, ids, fields, context, load)
        except Exception, e:
            return super(ir_actions_act_window, self).read(cr, uid, ids, fields, context, load)

ir_actions_act_window()
