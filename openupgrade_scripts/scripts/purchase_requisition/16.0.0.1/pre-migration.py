# Copyright 2024 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade, openupgrade_160


@openupgrade.migrate()
def migrate(env, version):
    openupgrade_160.fill_analytic_distribution(
        env,
        table="purchase_requisition_line",
        m2m_rel="account_analytic_tag_purchase_requisition_line_rel",
        m2m_column1="purchase_requisition_line_id",
        analytic_account_column="account_analytic_id",
    )
