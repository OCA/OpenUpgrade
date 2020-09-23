# -*- coding: utf-8 -*-
# Copyright 2017 Eficent - Miquel Raich
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def map_pos_config_state_active(cr):
    openupgrade.map_values(
        cr, 'state', 'active',
        [('deprecated', 'false'), ('inactive', 'false')],
        table='pos_config', write='sql')


@openupgrade.migrate()
def migrate(env, version):
    map_pos_config_state_active(env.cr)
    openupgrade.load_data(
        env.cr, 'point_of_sale', 'migrations/10.0.1.0.1/noupdate_changes.xml',
    )
    openupgrade.set_xml_ids_noupdate_value(
        env, "point_of_sale", ["seq_picking_type_posout"], True)
