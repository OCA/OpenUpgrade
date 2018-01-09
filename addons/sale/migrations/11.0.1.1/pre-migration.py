# -*- coding: utf-8 -*-
# Copyright 2018 - Nicolas JEUDY
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

_xmlid_renames = [
    ('account.group_proforma_invoices', 'sale.group_proforma_sales'),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_xmlids(env.cr, _xmlid_renames)
