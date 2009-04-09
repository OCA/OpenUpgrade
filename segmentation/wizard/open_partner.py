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
import pooler
import wizard

def _open_partner(self, cr, uid, data, context):

    if (data['id'] in data['ids'])|(data['ids'] == []):
        ids_to_check = pooler.get_pool(cr.dbname).get('segmentation.profile').get_parents(cr, uid, data['ids']) 
    else:       
        ids_to_check = pooler.get_pool(cr.dbname).get('segmentation.profile').get_parents(cr, uid, [data['id']])

    [yes_answers, no_answers] = pooler.get_pool(cr.dbname).get('segmentation.profile').get_answers(cr, uid, ids_to_check)

    query = "select partner from partner_question_rel "
    query_end = "group by partner"

    if yes_answers != []:
        query = query + """
        where answer in (%s) """    % (','.join([str(a) for a in yes_answers])) 

        #rebuild the end of the query
        query_end = """
        group by partner
        having count(*) >= %s """ % len(yes_answers)

    if no_answers != []:
        if yes_answers != []:
            query = query + "and "
        else:
            query = query + "where "

        query = query + """
        partner not in (
            select partner from partner_question_rel 
            where answer in (%s)) """ % ( ','.join([str(a) for a in no_answers]))

    query = query + query_end
    cr.execute(query)
    
    action= {
        'name': 'Matching partners',
        'view_type': 'form',
        'view_mode': 'tree,form',
        'res_model': 'res.partner',
        'type': 'ir.actions.act_window'
        }

    (res,) =cr.fetchall(),
    if len(res)==1:
        action['domain']= "[('id','=',(%s))]" % str(res[0][0])
    else:
        action['domain']= "[('id','in',(%s))]" % ','.join([str(x[0]) for x in res])
        
    return action

class open_partner(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type': 'action', 'action': _open_partner, 'state':'end'}
        }
    }

open_partner('open_partner')
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

