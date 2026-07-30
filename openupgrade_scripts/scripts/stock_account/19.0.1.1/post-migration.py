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
        SET value=aggregated_values.value
        FROM (
            SELECT
            move_id, sum(value) value
            FROM
            product_value
            GROUP BY move_id
        ) aggregated_values
        WHERE aggregated_values.move_id=stock_move.id
        """
    )


def product_value_unit_cost(env):
    """
    Convert product.value#value from a total value to a unit cost where 19.0
    expects one.

    17.0 stock.valuation.layer#value held the *total* value of the layer, with
    the per-unit price in the separate unit_cost column. 19.0
    product.value#value is a unit cost for records not linked to a move: those
    are what product.product#_get_last_product_value() reads to determine
    standard_price. Records linked to a move keep total-value semantics and are
    consumed by stock_move_value() above, so they are left alone -- which is
    also why this has to run after it.

    Without this, a move-less record keeps a total value where 19.0 reads a
    unit cost, silently corrupting standard_price and every COGS entry derived
    from it.

    Two sources, in order of directness:

    1. unit_cost, which pre-migration's rename_tables() leaves in place as an
       orphan column. Exact wherever 17.0 populated it.
    2. For manual revaluations 17.0 wrote unit_cost NULL and quantity 0, so the
       unit cost is derived the same way 17.0 itself did in
       product.product#_prepare_valuation_layer_field_values(): the running
       sum(value) / sum(quantity) over the product's layers up to that point.
       Evaluating it per record reproduces the historical cost at each record's
       own date, which matters because _get_last_product_value() selects by
       date.

    Being an accumulation over the layers rather than a per-layer field, (2) is
    cost-method independent and so covers fifo -- where a revaluation is spread
    over the remaining_value of the layers still in stock and never lands in a
    per-product unit cost -- as well as average.
    """
    # The accumulation in (2) sums the 17.0 total values, so snapshot them
    # before (1) starts overwriting them with unit costs.
    openupgrade.logged_query(
        env.cr,
        """
        CREATE TEMPORARY TABLE openupgrade_17_layer_value AS
        SELECT id, product_id, company_id, date, value, quantity
          FROM product_value
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        CREATE INDEX openupgrade_17_layer_value_idx
            ON openupgrade_17_layer_value (product_id, company_id, date, id)
        """,
    )

    openupgrade.logged_query(
        env.cr,
        """
        UPDATE product_value
           SET value = unit_cost
         WHERE move_id IS NULL
           AND quantity IS NOT NULL
           AND unit_cost IS NOT NULL
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        WITH computed AS (
            SELECT target.id,
                   sum(layer.value) / sum(layer.quantity) AS unit_cost
              FROM product_value target
              JOIN openupgrade_17_layer_value layer
                ON layer.product_id = target.product_id
               AND layer.company_id = target.company_id
               AND (layer.date, layer.id) <= (target.date, target.id)
             WHERE target.move_id IS NULL
               AND target.quantity IS NOT NULL
               AND target.unit_cost IS NULL
             GROUP BY target.id
            HAVING sum(layer.quantity) <> 0
        )
        UPDATE product_value
           SET value = computed.unit_cost
          FROM computed
         WHERE product_value.id = computed.id
        """,
    )

    # A product with no quantity on hand at that point has no meaningful unit
    # cost to derive. Leave those alone and say so: a wrong standard_price is
    # silent and ends up in the accounts, so guessing is worse than reporting.
    env.cr.execute(
        """
        SELECT target.id, target.description
          FROM product_value target
          LEFT JOIN LATERAL (
                SELECT sum(layer.quantity) AS quantity
                  FROM openupgrade_17_layer_value layer
                 WHERE layer.product_id = target.product_id
                   AND layer.company_id = target.company_id
                   AND (layer.date, layer.id) <= (target.date, target.id)
               ) accumulated ON TRUE
         WHERE target.move_id IS NULL
           AND target.quantity IS NOT NULL
           AND target.unit_cost IS NULL
           AND coalesce(accumulated.quantity, 0) = 0
        """
    )
    for value_id, description in env.cr.fetchall():
        openupgrade.logger.warning(
            "stock_account: product.value %s keeps its 17.0 total value because "
            "the product had no quantity on hand to derive a unit cost from; "
            "review it manually as it feeds standard_price. Description: %s",
            value_id,
            description,
        )


@openupgrade.migrate()
def migrate(env, version):
    product_value_product_id(env)
    stock_move_account_move_id(env)
    product_category_property_valuation(env)
    stock_location_valuation_account_id(env)
    stock_move_value(env)
    # Must stay last: it rewrites the values stock_move_value() reads.
    product_value_unit_cost(env)
