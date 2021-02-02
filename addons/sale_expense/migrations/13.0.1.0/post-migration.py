# Copyright 2021 Bloopark - Bishal Pun
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.delete_records_safely_by_xml_id(
        env, [
            "sale_expense.sale_order_rule_expense_user",
            "hr_expense.product_product_fixed_cost",
        ]
    )
