# Copyright 2026 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


def product_value_product_id(env):
    """
    Fill product.value#product_id from move_id.product_id
    """
    env.cr.execute(
        """
        UPDATE product_value
        SET product_id=stock_move.product_id
        FROM stock_move
        WHERE product_value.move_id=stock_move.id
        AND product_value.product_id IS NULL
        """
    )


def stock_move_account_move_id(env):
    """
    Fill stock.move#account_move_id from account.move#stock_move_id
    """
    env.cr.execute(
        """
        UPDATE stock_move
        SET account_move_id=account_move.id
        FROM account_move
        WHERE
        account_move.stock_move_id=stock_move.id
        AND stock_move.account_move_id IS NULL
        """
    )


def product_category_property_valuation(env):
    """
    Change value 'manual_periodic' to 'periodic'
    """
    env["ir.default"].search(
        [
            ("field_id.name", "=", "property_valuation"),
            ("field_id.model_id.model", "=", "product.category"),
            ("json_value", "=", '"manual_periodic"'),
        ]
    ).write({"json_value": '"periodic"'})

    for company in env["res.company"].search([]):
        env.cr.execute(
            f"""
            UPDATE product_category
            SET
            property_valuation = property_valuation || '{{"{company.id}": "periodic"}}'
            WHERE
            property_valuation->>'{company.id}' = 'manual_periodic'
            """
        )


def stock_location_valuation_account_id(env):
    """
    Set stock.location#valuation_account_id from valuation_in_account_id and
    valuation_out_account_id if they are the same
    """
    env.cr.execute(
        """
        UPDATE stock_location
        SET valuation_account_id=valuation_in_account_id
        WHERE
        valuation_in_account_id=valuation_out_account_id
        """
    )


def stock_move_value(env):
    """
    Set stock.move#value to sum of product.value#value for this move
    """
    env.cr.execute(
        """
        UPDATE stock_move
        SET value=aggregated_values.agg_value
        FROM (
            SELECT
            move_id, sum(value) AS agg_value
            FROM
            product_value
            GROUP BY move_id
        ) aggregated_values
        WHERE aggregated_values.move_id=stock_move.id
        """
    )


@openupgrade.migrate()
def migrate(env, version):
    product_value_product_id(env)
    stock_move_account_move_id(env)
    product_category_property_valuation(env)
    stock_location_valuation_account_id(env)
    stock_move_value(env)
