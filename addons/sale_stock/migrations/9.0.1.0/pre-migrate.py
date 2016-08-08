# -*- coding: utf-8 -*-
# © 2016 Opener B.V. - Stefan Rijnhart
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(cr, version):
    if openupgrade.is_module_installed(cr, 'stock_account'):
        openupgrade.rename_columns(cr, {
            'stock_move': [('invoice_state', None)]})
