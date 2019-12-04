# Copyright 2020 ForgeFlow <http://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def fill_stock_valuation_layer(env):
    openupgrade.logged_query(
        env.cr, """
        ALTER TABLE stock_valuation_layer
        ADD COLUMN old_product_price_history_id integer""",
    )
    product_ids = env['product.product'].search(
        [('type', '=', 'product')]).ids
    if product_ids:
        openupgrade.logged_query(
            env.cr, """
            INSERT INTO stock_valuation_layer (old_product_price_history_id,
                company_id, product_id, quantity, unit_cost, description,
                create_uid, create_date, write_uid, write_date)
            SELECT pph.id, pph.company_id, pph.product_id, 0, pph2.cost,
                pt.name, pph2.create_uid, pph2.create_date, pph2.write_uid,
                pph2.write_date
            FROM (SELECT max(id) as id, company_id, product_id
                FROM product_price_history
                GROUP BY company_id, product_id
                ORDER BY id
                ) pph
            JOIN product_price_history pph2 ON pph.id = pph2.id
            JOIN product_product pp ON pph.product_id = pp.id
            JOIN product_template pt ON pp.product_tmpl_id = pt.id
            WHERE pp.id IN %s""", (tuple(product_ids), ),
        )
        # NOTE: It seems to be incomplete (without the link of the stock move)


@openupgrade.migrate()
def migrate(env, version):
    fill_stock_valuation_layer(env)
    openupgrade.delete_records_safely_by_xml_id(
        env, [
            "stock_account.default_cost_method",
            "stock_account.default_valuation",
            "stock_account.property_stock_account_input_prd",
            "stock_account.property_stock_account_output_prd",
        ]
    )
