# Copyright 2026 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


def stock_move_reference_ids(env):
    """
    Fill stock.move#reference_ids from obsolete group_id
    """
    env.cr.execute(
        """
        INSERT INTO stock_reference_move_rel
        (move_id, reference_id)
        SELECT id, group_id FROM stock_move
        WHERE group_id IS NOT NULL
        """
    )


def stock_move_packaging_uom_id(env):
    """
    Use stock.move#product_packaging_id to fill stock.move#packaging_uom_id
    """
    env.cr.execute(
        """
        UPDATE stock_move
        SET packaging_uom_id=product_uom.uom_id
        FROM
        product_uom
        WHERE product_packaging_id=product_uom.id
        """
    )


def stock_picking_package_history_ids(env):
    """
    Use stock.package_level#picking_id to fill stock.picking#package_history_ids
    """
    env.cr.execute(
        """
        INSERT INTO stock_package_history_stock_picking_rel
        (stock_picking_id, stock_package_history_id)
        SELECT picking_id, id
        FROM stock_package_history
        WHERE picking_id IS NOT NULL
        """
    )


def stock_package_type_package_use(env):
    """
    Set stock.package.type#package_use to 'reusable' if all previous stock.quant.package
    records using this type had package_use = 'reusable'
    """
    env.cr.execute(
        """
        UPDATE stock_package_type
        SET package_use='reusable'
        WHERE id IN (
            SELECT package_type_id
            FROM stock_package
            GROUP BY package_type_id
            HAVING array_agg(distinct package_use) <@ '{"reusable"}'
        )
        """
    )


def uom_uom_package_type_id(env):
    """
    Set uom.uom#package_type_id from previous product.packaging#packaging_type
    """
    env.cr.execute(
        """
        UPDATE uom_uom
        SET package_type_id=product_uom.package_type_id
        FROM product_uom
        WHERE product_uom.uom_id=uom_uom.id
        AND product_uom.package_type_id IS NOT NULL
        """
    )


def stock_packaging_type_route_ids(env):
    """
    Set stock.packaging.type#route_ids from previous product.packaging#route_ids
    """
    env.cr.execute(
        """
        INSERT INTO stock_package_type_stock_route_rel
        (stock_package_type_id, stock_route_id)
        SELECT DISTINCT
        product_uom.package_type_id, stock_route_packaging.route_id
        FROM
        stock_route_packaging
        JOIN product_uom
        ON stock_route_packaging.packaging_id=product_uom.id
        """
    )


def stock_package_history_package_name(env):
    """
    Set stock.package.history#package_name from package_id#name
    """
    env.cr.execute(
        """
        UPDATE stock_package_history
        SET package_name=stock_package.name
        FROM stock_package
        WHERE
        stock_package_history.package_id=stock_package.id
        AND package_name IS NULL
        """
    )


_deleted_xmlids = [
    "stock.stock_location_locations_virtual",
    "stock.stock_location_locations_partner",
    "stock.stock_location_locations",
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env, "stock", "19.0.1.1/noupdate_changes.xml")
    openupgrade.delete_record_translations(
        env.cr,
        "stock",
        [
            "mail_template_data_delivery_confirmation",
        ],
        ["body_html"],
    )
    stock_move_reference_ids(env)
    stock_move_packaging_uom_id(env)
    stock_picking_package_history_ids(env)
    stock_package_type_package_use(env)
    uom_uom_package_type_id(env)
    stock_packaging_type_route_ids(env)
    stock_package_history_package_name(env)
    openupgrade.delete_records_safely_by_xml_id(env, _deleted_xmlids)
