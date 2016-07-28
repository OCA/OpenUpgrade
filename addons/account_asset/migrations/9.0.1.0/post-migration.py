# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(cr, version):
    cr.execute(
        "update account_move m set asset_id=l.asset_id "
        "from account_move_line l "
        "where l.move_id=m.id and l.asset_id is not null")
    cr.execute(
        "update account_asset_asset a set invoice_id=i.id "
        "from account_invoice i "
        "join account_move m on i.move_id=m.id "
        "where m.asset_id=a.id")
