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

class configurator(osv.osv_memory):
    _name = "sale_product_multistep_configurator.configurator"
    _columns = {}
    
configurator()

class configurator_step(osv.osv):
    _name = "sale_product_multistep_configurator.configurator.step"
    _columns = {
                'name': fields.char('Value Name', size=64, select=1), #TODO related?
                'model_id': fields.many2one('ir.model', 'Object ID', required=True, select=True),
                'sequence' : fields.integer('Sequence', help="Determine in which order step are executed"),
                }
    
configurator_step()


class ir_actions_act_window(osv.osv):
    _inherit = 'ir.actions.act_window'

    def read(self, cr, uid, ids, fields=None, context={}, load='_classic_read'):

        if isinstance(ids, (int, long)):
            read_ids = [ids]
        else:
            read_ids = ids
         
        result = super(ir_actions_act_window, self).read(cr, uid, read_ids, ['context'], context, load)[0]

        if eval(result['context']).get('multistep_wizard_dispatch', False):
            print "*** DISPATCHING FOR CONFIGURATOR ***"
            configurator_context = eval(result['context'])
            print "inherited configurator_context", configurator_context
            
            #TODO get action_id from configurator_step model?
            #TODO do not hardcode the flow logic anymore, get it form configurator_step!
            action_id = self.search(cr, uid, [('name', '=', 'product_variant_configurator.action_product_configure')])[0]
            
            result = super(ir_actions_act_window, self).read(cr, uid, action_id, fields, context, load)
            configurator_context.update(eval(result['context']))#used to pass active_id_object_type and make sure we will dispatch here again eventually, see corresponding act_window      
            configurator_context.update({'next_step':'bom_customization.configurator'})#TODO have a back system + TODO be dynamic here
            print "specific configurator_context", configurator_context
            result['context'] = unicode(configurator_context)
            return result
        else:
            return super(ir_actions_act_window, self).read(cr, uid, ids, fields, context, load)

ir_actions_act_window()

