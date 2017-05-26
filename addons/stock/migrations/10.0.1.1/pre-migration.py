# -*- coding: utf-8 -*-
# Copyright 2017 Trescloud <http://trescloud.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

column_copies = {
    'procurement_rule': [
        ('route_sequence', None, None),
    ],
    'stock_location_path': [
        ('auto', None, None),
        ('route_sequence', None, None),
    ],
}


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    cr = env.cr
    openupgrade.copy_columns(cr, column_copies)
    openupgrade.float_to_integer(cr, 'procurement_rule', 'route_sequence')
    openupgrade.float_to_integer(cr, 'stock_location_path', 'route_sequence')
