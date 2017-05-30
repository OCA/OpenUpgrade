# -*- coding: utf-8 -*-
# © 2017 bloopark systems (<http://bloopark.de>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate(use_env=False)
def migrate(cr, version):
    # map old False value to new value 'rate', old True / new 'rate_and_ship'
    # values are set per default
    cr.execute("""
        UPDATE delivery_carrier SET integration_level = 'rate'
        WHERE %(shipping_enabled)s IS False
    """ % {
        'shipping_enabled': openupgrade.get_legacy_name('shipping_enabled')
    })
