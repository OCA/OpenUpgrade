# -*- coding: utf-8 -*-
# Copyright 2017 Trescloud <http://trescloud.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

def update_picking_type_id(env):
    """Updates picking_type_id, defaulting to some value, guessing by looking at source
    and destination locations, and warehouse.  
    :param env: enviroment variable (self)
    """
    #load xml data to be used for filling in missing info
    xml_stock_picking_type_internal = env.ref("stock.picking_type_internal")
    xml_stock_picking_type_out = env.ref("stock.picking_type_out")
    xml_stock_picking_type_in = env.ref("stock.picking_type_in")
    xml_stock_picking_type_manufacturing = env.ref("mrp.picking_type_manufacturing")
    #verify for each procument rule to set
    procurement_rules_to_set = env['procurement.rule'].search([])
    for procurement_rule in procurement_rules_to_set:
        if not procurement_rule.picking_type_id:
            picking_type_id = False
            env.cr.execute(
                '''
                SELECT id from stock_picking_type 
                WHERE warehouse_id = %s AND 
                      default_location_dest_id = %s AND 
                      default_location_src_id = %s''' % (
                    procurement_rule.warehouse_id, 
                    procurement_rule.location_id,
                    procurement_rule.location_src_id,
                )
            )
            picking_type_ids = cr.fetchone()
            if picking_type_ids:
                picking_type_id = picking_type_ids[0]
            if not picking_type_id: #fallback values when everything else fails
                if procurement_rule.action == 'buy':
                    #location_src_id is not considered as is not mandatory in this case
                    if xml_stock_picking_type_in:
                        picking_type_id = xml_stock_picking_type_in.id
                elif procurement_rule.action == 'move':
                    if procurement_rule.location_id and procurement_rule.location_id.usage == 'customer':
                        #special case when is a delivarable to a customer location
                        if xml_stock_picking_type_out:
                            picking_type_id = xml_stock_picking_type_out.id
                    else:
                        if xml_stock_picking_type_internal:
                            picking_type_id = xml_stock_picking_type_internal.id
                elif procurement_rule.action == 'manufacture':
                    if xml_stock_picking_type_manufacturing:
                        picking_type_id = xml_stock_picking_type_manufacturing.id
            procurement_rule.write({'picking_type_id': picking_type_id})

def update_ordered_qty(env):
    """ Set the value of new field ordered_qty as:
      - for stock moves the value of field product_uom_qty
      - for stock_pack_operation the value of product_qty  
    :param env: enviroment variable (self)
    """
    env.cr.execute(
        '''
        UPDATE stock_move SET ordered_qty = product_uom_qty
        ''')
    env.cr.execute(
        '''
        UPDATE stock_pack_operation SET ordered_qty = product_qty
        ''')
    
def populate_stock_scrap(env):
    """ Fills up new object "stock.scrap" based on moves with destination scrap  
    :param env: enviroment variable (self)
    """
    env.cr.execute(
        '''
        SELECT id from stock_location 
        WHERE scrap_location is True
        '''
        )
    scrap_location_ids = env.cr.fetchone()
    #do not call stock_scrap.create as it will create a duplicated stock move, use SQL instead
    #field package_id not set as no value is defined    
    env.cr.execute(
        '''
        INSERT INTO stock_scrap (date_expected,location_id,lot_id,move_id,name,origin,owner_id,picking_id,product_id,product_uom_id,scrap_location_id,scrap_qty,state)
            SELECT date_expected,location_id,restrict_lot_id,id,name,origin,restrict_partner_id,picking_id,product_id,product_uom,location_dest_id,product_uom_qty,state
            FROM stock_move
            WHERE location_id IN %s AND product_uom_qty < 0.0 AND state = 'done' 
                OR location_dest_id IN %s AND product_uom_qty >= 0.0 AND state = 'done'
        ''',(scrap_location_ids,scrap_location_ids))
    
@openupgrade.migrate(use_env=True)
def migrate(env, version):
    update_picking_type_id(env)
    update_ordered_qty(env)
    populate_stock_scrap(env)