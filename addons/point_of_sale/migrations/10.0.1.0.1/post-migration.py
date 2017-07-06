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
