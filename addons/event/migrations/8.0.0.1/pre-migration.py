# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright 2014 Onestein
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.openupgrade import openupgrade

column_renames = {
#                   'procurement_order' : [
#                        ('message' , None),
#                        ('note' , None),
#                        ('move_id' , None),
#                        ('procure_method', None),
#                  ],
#                   'product_template' : [
#                        ('supply_method' , None),
#                        ('procure_method', None),
#                  ],
                    'event_event': [
                        ('note', None),
                    ],
            }

xmlid_renames = [
    ('procurement.access_stock_warehouse_orderpoint',
     'stock.access_stock_warehouse_orderpoint'),
    ('procurement.access_stock_warehouse_orderpoint_system',
     'stock.access_stock_warehouse_orderpoint_system'),
    ('procurement.stock_warehouse_orderpoint_rule',
     'stock.stock_warehouse_orderpoint_rule'),
    ('procurement.access_mrp_property',
     'mrp.access_mrp_property'),
    ('procurement.access_mrp_property_group',
     'mrp.access_mrp_property_group'),
    ('procurement.sequence_mrp_op',
     'stock.sequence_mrp_op'),
    ('procurement.sequence_mrp_op_type',
     'stock.sequence_mrp_op_type'),
    ]

@openupgrade.migrate()
def migrate(cr, version):
#     openupgrade.rename_columns(cr, column_renames)
    openupgrade.rename_xmlids(cr, xmlid_renames)
    # The workflow must be deleted because set_last_post_message() calls the ORM write method.
    openupgrade.delete_model_workflow(cr, 'procurement.order')