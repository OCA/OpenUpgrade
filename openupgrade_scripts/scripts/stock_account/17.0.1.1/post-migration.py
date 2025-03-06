# Copyright 2024 Viindoo Technology Joint Stock Company (Viindoo)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def _stock_move_convert_analytic_account_line_id_m2o_to_m2m(env):
    openupgrade.m2o_to_x2m(
        env.cr,
        env["stock.move"],
        "stock_move",
        "analytic_account_line_ids",
        "analytic_account_line_id",
    )


def fill_account_move_line_cogs_origin_id(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_move_line aml
        SET cogs_origin_id = line.id
        FROM account_move_line line
        WHERE aml.move_id = line.move_id
            AND line.display_type != 'cogs' AND aml.display_type = 'cogs'
            AND line.product_id = aml.product_id
            AND line.product_uom_id = aml.product_uom_id
            AND line.quantity = aml.quantity
            AND left(line.name, 64) = aml.name""",
    )


def delete_obsolete_ir_model_data(env):
    xml_ids = [
        "stock_account.property_stock_account_input_categ_id",
        "stock_account.property_stock_account_output_categ_id",
    ]
    for xml_id in xml_ids:
        module, name = xml_id.split(".")
        imd = env["ir.model.data"].search(
            [("module", "=", module), ("name", "=", name)]
        )
        imd.unlink()


@openupgrade.migrate()
def migrate(env, version):
    _stock_move_convert_analytic_account_line_id_m2o_to_m2m(env)
    fill_account_move_line_cogs_origin_id(env)
    delete_obsolete_ir_model_data(env)
