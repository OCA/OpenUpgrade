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
from osv import osv

finished_form = """<?xml version="1.0"?>
<form string="Merge Picking">
    <separator string="Merged All Customers Picking Goods!!!" />
</form>"""

def find_partner(self,cr,uid,ids,context=None):
        state = 'assigned'
        type = 'out'
        
        cr.execute("select address_id from stock_picking where type='%s' and state='%s' and address_id is not null group by address_id,state,type" % (type,state))
        partner_ids=cr.dictfetchall()
        
        for partner in partner_ids:   
            find_max_invid(self,cr,uid,ids,partner['address_id'],state,type)
                   
        return {}

def find_max_invid(self,cr,uid,ids,address_id,state,type):
    stk_move_obj = pooler.get_pool(cr.dbname).get('stock.picking')
    stk_move = pooler.get_pool(cr.dbname).get('stock.move')
    
    cr.execute("select max(id) from stock_picking where type='%s' and state='%s' and address_id=%d" % (type,state,address_id))
    max_picking_id=cr.fetchall()[0][0]
    
    cr.execute('select * from stock_picking where id=%d' %(max_picking_id))
    rec_dict=cr.dictfetchall()
    
    rec_dict[0].__delitem__('perm_id')
    rec_dict[0].__delitem__('create_uid')
    rec_dict[0].__delitem__('create_date')
    rec_dict[0].__delitem__('write_date')
    rec_dict[0].__delitem__('write_uid')
    rec_dict[0].__delitem__('id')   
    
    rec_dict[0]['name']="OUT:"+str(max_picking_id+1)
    rec_dict[0]['state']="draft"
    
    cr.execute("select * from stock_picking pc where type='%s' and state='%s' and address_id=%d" % (type,state,address_id))
    picking_info=cr.dictfetchall()
    
    if len(picking_info) > 1:
        cr_id=stk_move_obj.create(cr,uid,rec_dict[0],context=None)
        
        for picking in picking_info:
            pick_ids=stk_move.search(cr,uid,[('picking_id','=',picking['id'])])
            
            for pick_id in pick_ids:
                stk_move.write(cr,uid,pick_id,{'picking_id':cr_id})
                
            wf_service = netsvc.LocalService("workflow")
            wf_service.trg_validate(uid, 'stock.picking', picking['id'], 'button_cancel', cr)
            
        wf_service = netsvc.LocalService("workflow")
        wf_service.trg_validate(uid, 'stock.picking', cr_id, 'button_confirm', cr)
    
        stk_move_obj.action_assign(cr,uid,[cr_id])    
    return True    


class wiz_stock_picking_merge(wizard.interface):
    states = {
        'init': {                 
            'actions': [find_partner],
            'result': {'type': 'form', 'arch' : finished_form, 'fields' : {}, 'state' : [('end', 'Ok')]},
        }
    }
wiz_stock_picking_merge('stock.move.picking.merge')
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

