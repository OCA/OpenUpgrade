# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def fill_account_date(cr):
    """
    Fills account_date as copy of date from move_id
    :param cr: cursor variable (self.env)
    """
    cr.execute(
        """
        UPDATE account_voucher
        SET account_date = account_move.date
        FROM account_move
        WHERE account_move.id = account_voucher.move_id
        """)


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    fill_account_date(cr)
