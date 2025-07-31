# Copyright 2025 Tecnativa - Carlos Lopez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade

column_creates = [("stock.landed.cost", "company_id", "many2one")]


def fill_stock_landed_cost_company_id(env):
    """
    Set company_id for stock landed costs from journal entry.
    """
    env.cr.execute(
        """
        UPDATE stock_landed_cost slc
        SET
            company_id = aj.company_id
        FROM account_journal aj
        WHERE aj.id = slc.account_journal_id AND slc.company_id IS NULL
        """
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.add_columns(env, column_creates)
    fill_stock_landed_cost_company_id(env)
