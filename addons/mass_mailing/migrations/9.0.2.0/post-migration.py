# -*- coding: utf-8 -*-
# © 2016 Tecnativa - Vicent Cubells <vicent.cubells@tecnativa.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def map_template_state(cr):
    openupgrade.map_values(
        cr,
        openupgrade.get_legacy_name('state'),
        'state',
        [('test', 'draft')],
        table='mail_mass_mailing', write='sql')


@openupgrade.migrate()
def migrate(cr, version):
    map_template_state(cr)
