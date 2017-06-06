# -*- coding: utf-8 -*-
# © 2017 Trescloud <http://trescloud.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

@openupgrade.migrate(use_env=True)
def migrate(env, version):
    
    #field route_sequence
    openupgrade.copy_columns(
        env.cr, {
            'procurement_rule': [
                ('route_sequence', None, None),
            ],             
        })
    openupgrade.float_to_integer(env.cr, 'procurement_rule', 'route_sequence')
    
    #table auto
    openupgrade.copy_columns(
        env.cr, {
            'stock_location_path': [
                ('auto', None, None),
                ('route_sequence', None, None),
            ],
        })
    env.cr.execute(
        """
        UPDATE stock_location_path SET auto = 'manual' WHERE auto = 'auto';
        """)
    openupgrade.float_to_integer(env.cr, 'stock_location_path', 'route_sequence')
    
    
