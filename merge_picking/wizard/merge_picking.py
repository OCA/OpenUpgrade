import wizard
import netsvc
import pooler

from osv import osv

finished_form = """<?xml version="1.0"?>
<form string="Merge Picking">
    <separator string="Merged All Customers Picking Goods!!!" />
</form>"""

def find_partner(self,cr,uid,ids,context=None):
        # partner id is denoted by address_id in stock.picking
        cr.execute("select address_id from stock_picking where type='out' and state='confirmed' and address_id is not null group by address_id,state,type")
        partner_ids=cr.dictfetchall()
        for partner in partner_ids:            
            find_max_invid(self,cr,uid,ids,partner['address_id'])            
        return {}

def find_max_invid(self,cr,uid,ids,address_id,type='out',state='confirmed'):
    
    cr.execute("select max(id) from stock_picking where type='%s' and state='%s' and address_id=%d"%(type,state,address_id))
    max_picking_id=cr.fetchall()[0][0]
    
    cr.execute("select * from stock_picking pc where type='out' and state='confirmed' and address_id=%d"%(address_id))
    picking_info=cr.dictfetchall()
    
    for data in picking_info:
        copy_move_line(self,cr,uid,ids,data['id'],max_picking_id)        
        if data['id']<max_picking_id:
            cr.execute("update stock_picking set state='cancel' where id=%d"%(data['id']))
    return True

def copy_move_line(self,cr,uid,ids,picking_id,max_picking_id):
    
    stk_move_obj = pooler.get_pool(cr.dbname).get('stock.move')   
    
    cr.execute("select * from stock_move where picking_id=%d"%(picking_id))
    stock_move_info=cr.dictfetchall()

    for data in stock_move_info:
            if data['picking_id']<max_picking_id:   
                data['picking_id']=max_picking_id
                data.__delitem__('perm_id')
                data.__delitem__('create_uid')
                data.__delitem__('create_date')
                data.__delitem__('write_date')
                data.__delitem__('write_uid')
                data.__delitem__('id')                
                stk_move_obj.create(cr,uid,data)          
    return True      
            
class wiz_stock_picking_merge(wizard.interface):
    states = {
        'init': {
                 
            'actions': [find_partner],
            'result': {'type': 'form', 'arch' : finished_form, 'fields' : {}, 'state' : [('end', 'Ok')]},
        }
    }
wiz_stock_picking_merge('stock.move.picking.merge')
