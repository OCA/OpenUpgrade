from openupgradelib import openupgrade


def _move_data_from_product_packaging_to_stock_package_type(env):
    openupgrade.logged_query(
        env.cr,
        """ALTER TABLE stock_package_type
        ADD COLUMN IF NOT EXISTS old_product_packaging_id INTEGER""",
    )
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO stock_package_type(old_product_packaging_id,
            name, sequence, height, width,
            shipper_package_code, package_carrier_type,
            packaging_length, max_weight, barcode, company_id,
            create_uid, create_date, write_uid, write_date)
        SELECT id,
            name, sequence, height, width,
            shipper_package_code, package_carrier_type,
            packaging_length, max_weight, barcode, company_id,
            create_uid, create_date, write_uid, write_date
        FROM product_packaging
        WHERE product_id IS NULL
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE stock_quant_package sqp
        SET package_type_id = spt.id
        FROM stock_package_type spt
        WHERE spt.old_product_packaging_id = sqp.packaging_id
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    _move_data_from_product_packaging_to_stock_package_type(env)
