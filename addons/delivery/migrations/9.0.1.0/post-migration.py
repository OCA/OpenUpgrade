# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# Copyright 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(cr, version):
    cr.execute(
        """
        UPDATE delivery_carrier dc
        SET delivery_type='base_on_rule',
            free_if_more_than = old_dc.free_if_more_than,
            fixed_price = old_dc.normal_price
        FROM %s old_dc
        WHERE old_dc.use_detailed_pricelist
            AND old_dc.id = dc.%s
        """ % (
            openupgrade.get_legacy_name('delivery_carrier'),
            openupgrade.get_legacy_name('carrier_id'),
        )
    )
