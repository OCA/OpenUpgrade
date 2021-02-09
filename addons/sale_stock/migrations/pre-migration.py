# Copyright 2021 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.logged_query(
        env.cr, """
        UPDATE account_invoice
        SET incoterm_id = incoterms_id
        WHERE incoterm_id IS NULL
            AND incoterms_id IS NOT NULL
        """
    )
