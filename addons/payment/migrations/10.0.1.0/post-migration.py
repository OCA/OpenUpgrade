# -*- coding: utf-8 -*-
# Copyright 2017 Eficent - Miquel Raich
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def map_adquirer_auto_confirm(cr):
    openupgrade.map_values(
        cr,
        openupgrade.get_legacy_name('auto_confirm'), 'auto_confirm',
        [('at_pay_confirm', 'confirm_so'),
         ('at_pay_now', 'generate_and_pay_invoice')],
        table='payment_acquirer', write='sql')


@openupgrade.migrate()
def migrate(env, version):
    map_adquirer_auto_confirm(env.cr)
