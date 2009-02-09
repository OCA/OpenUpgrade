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
import pooler

form="""<?xml version="1.0"?>
<form string="Evaluation Computation" colspan="4">
    <label string="All the evaluations have been recomputed successfully." />
</form>
"""

fields = {}

class wizard_recompute_votes(wizard.interface):
    
    def _recompute(self, cr, uid, data, context):
        pool = pooler.get_pool(cr.dbname)        
        obj_factor = pool.get('comparison.factor')
        obj_item = pool.get('comparison.item')
        obj_factor_result = pool.get('comparison.factor.result')
        obj_vote_values = pool.get('comparison.vote.values')
        
        top_level_ids = obj_factor.search(cr, uid, [('parent_id','=',False)])
        
        for top_records in obj_factor.browse(cr, uid, top_level_ids, context):
            #TODO : Calculate from bottom to top.
            pass
        
        return {}

    states = {
        'init' : {
            'actions' : [_recompute],
            'result' : {'type' : 'form' , 'arch' : form,'fields' : fields,'state' : [('end','Ok')]}
        },
    }
wizard_recompute_votes("recompute.evaluations")
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: