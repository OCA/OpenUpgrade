from openupgradelib import openupgrade

_models_renames = [
    ("stock.location.route", "stock.route"),
    ("stock.production.lot", "stock.lot"),
]

_tables_renames = [
    ("stock_location_route", "stock_route"),
    ("stock_production_lot", "stock_lot"),
    ("stock_location_route_categ", "stock_route_categ"),
    ("stock_location_route_packaging", "stock_route_packaging"),
    ("stock_location_route_move", "stock_route_move"),
]

_fields_renames = [
    ("stock.move.line", "stock_move_line", "product_qty", "reserved_qty"),
    ("stock.move.line", "stock_move_line", "product_uom_qty", "reserved_uom_qty"),
    ("stock.rule", "stock_rule", "location_id", "location_dest_id"),
    ("stock.picking", "stock_picking", "move_lines", "move_ids"),
]
_xmlids_renames = [
    ("stock.access_stock_production_lot_user", "stock.access_stock_lot_user")
]


def _update_stock_quant_storage_category_id(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE stock_quant
        ADD COLUMN IF NOT EXISTS storage_category_id INTEGER
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE stock_quant
        SET storage_category_id = stock_location.storage_category_id
        FROM stock_location
        WHERE stock_quant.location_id = stock_location.id
        """,
    )


def _update_sol_product_category_name(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE stock_move_line
        ADD COLUMN IF NOT EXISTS product_category_name CHARACTER VARYING
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE stock_move_line AS sml
        SET product_category_name = category.complete_name
        FROM product_product AS product
        JOIN product_template AS product_tmpl
        ON product_tmpl.id = product.product_tmpl_id
        JOIN product_category AS category
        ON category.id = product_tmpl.categ_id
        WHERE sml.product_id = product.id
        """,
    )


def _compute_stock_location_replenish_location(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE stock_location
        ADD COLUMN IF NOT EXISTS replenish_location BOOLEAN
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        WITH location_info as (
            SELECT sl.id as id,
            CASE
                WHEN sl.usage = 'internal' AND sl.id = sw.lot_stock_id THEN True
                ELSE FALSE
            END as replenish_location_status
            FROM stock_location sl
            LEFT JOIN stock_warehouse sw
            ON sw.lot_stock_id = sl.id
        )
        UPDATE stock_location sl
        SET replenish_location = info.replenish_location_status
        FROM location_info info
        WHERE sl.id = info.id
        """,
    )


def _update_stock_quant_package_pack_date(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE stock_quant_package
        ADD COLUMN IF NOT EXISTS pack_date DATE
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE stock_quant_package
        SET pack_date = DATE(create_date)
        """,
    )


def _handle_stock_picking_backorder_strategy(env):
    # Handle the merge of OCA/stock-logistics-workflow/stock_picking_backorder_strategy
    # feature in odoo/stock V16 module.
    if openupgrade.column_exists(env.cr, "stock_picking_type", "backorder_strategy"):
        # Rename column
        openupgrade.rename_columns(
            env.cr,
            {
                "stock_picking_type": [
                    ("backorder_strategy", None),
                ],
            },
        )


def _prefill_stock_move_quantity_done(env):
    """It's going to be an stored field now. Let's try to speed up the field
    computation so it performs better in larga stock_move tables"""
    if not openupgrade.column_exists(env.cr, "stock_move", "quantity_done"):
        openupgrade.add_fields(
            env,
            [
                (
                    "quantity_done",
                    "stock.move",
                    "stock_move",
                    "float",
                    False,
                    "stock",
                )
            ],
        )
    # For moves with lines with different units of measure we rather pass them through
    # the ORM in post-migration, although this will deal with the vast majority of
    # moves.
    openupgrade.logged_query(
        env.cr,
        """
        WITH precision_cte AS (
            SELECT digits FROM decimal_precision
            WHERE name = 'Product Unit of Measure' LIMIT 1
        ),
        consistent_moves AS (
            SELECT move_id
            FROM stock_move_line
            GROUP BY move_id
            HAVING COUNT(DISTINCT product_uom_id) = 1 AND SUM(qty_done) <> 0
        ),
        move_quantities AS (
            SELECT sm.id AS move_id,
                -- Round the values to the current decimal precision in case it changed
                -- in the past
                SUM(
                    ROUND(sml.qty_done, (SELECT digits FROM precision_cte))
                ) AS total_quantity_done
            FROM stock_move sm
            JOIN stock_move_line sml ON sm.id = sml.move_id
            WHERE sm.id IN (SELECT move_id FROM consistent_moves)
            GROUP BY sm.id
        )
        UPDATE stock_move
        SET quantity_done = mq.total_quantity_done
        FROM move_quantities mq
        WHERE stock_move.id = mq.move_id;
    """,
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_tables(env.cr, _tables_renames)
    openupgrade.rename_models(env.cr, _models_renames)
    openupgrade.rename_fields(env, _fields_renames)
    openupgrade.rename_xmlids(env.cr, _xmlids_renames)
    _update_stock_quant_storage_category_id(env)
    _update_stock_quant_package_pack_date(env)
    _update_sol_product_category_name(env)
    _compute_stock_location_replenish_location(env)
    _handle_stock_picking_backorder_strategy(env)
    _prefill_stock_move_quantity_done(env)
