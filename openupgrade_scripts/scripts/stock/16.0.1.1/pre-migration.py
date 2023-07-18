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
        UPDATE stock_location sl
            SET replenish_location = False
        WHERE sl.usage != 'internal'
        """,
    )

    openupgrade.logged_query(
        env.cr,
        """
        UPDATE stock_location sl
            SET replenish_location = True
        FROM stock_warehouse sw
        WHERE sl.usage = 'internal' AND sl.id = sw.lot_stock_id
        """,
    )

    openupgrade.logged_query(
        env.cr,
        """
        UPDATE stock_location sl
            SET replenish_location = True
        FROM stock_warehouse_orderpoint point
        WHERE sl.id = point.location_id
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


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_models(env.cr, _models_renames)
    openupgrade.rename_tables(env.cr, _tables_renames)
    openupgrade.rename_fields(env, _fields_renames)
    _update_stock_quant_storage_category_id(env)
    _update_stock_quant_package_pack_date(env)
    _update_sol_product_category_name(env)
    _compute_stock_location_replenish_location(env)
