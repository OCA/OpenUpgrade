# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(cr, version):
    openupgrade.map_values(
        cr, openupgrade.get_legacy_name('type'), 'voucher_type',
        [('receipt', 'sale'), ('payment', 'purchase')],
        table='account_voucher')
    cr.execute(
        "insert into account_tax_account_voucher_line_rel "
        "(account_tax_id, account_voucher_line_id) "
        "select v.tax_id, l.id "
        "from account_voucher v "
        "join account_voucher_line l on l.voucher_id=v.id")
