# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def map_product_template(cr):
    openupgrade.map_values(
        cr,
        openupgrade.get_legacy_name('auto_create_task'),
        'track_service',
        [(True, 'task')],
        table='product_template', write='sql')


@openupgrade.migrate()
def migrate(cr, version):
    map_product_template(cr)
