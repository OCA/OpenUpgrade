# Copyright 2021 ForgeFlow S.L.  <https://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def fast_fill_lunch_supplier_company_id(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE lunch_supplier
        ADD COLUMN company_id integer""",
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE lunch_supplier ls
        SET company_id = rp.company_id
        FROM res_partner rp
        WHERE ls.partner_id = rp.id""",
    )


@openupgrade.migrate()
def migrate(env, version):
    fast_fill_lunch_supplier_company_id(env)
    openupgrade.set_xml_ids_noupdate_value(
        env,
        "lunch",
        [
            "lunch_mind_other_food_money",
            "lunch_mind_your_own_food_money",
            "lunch_order_rule_delete",
            "lunch_order_rule_write",
            "lunch_order_rule_write_manager",
        ],
        True,
    )
