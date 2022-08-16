from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE stock_quant sq
        SET accounting_date = si.accounting_date
        FROM stock_inventory si
        JOIN stock_inventory_line sil ON sil.inventory_id = si.id
        JOIN stock_location sl ON sil.location_id = sl.id
        WHERE sq.location_id = sl.id AND sl.usage in ('internal', 'transit')
            AND si.state = 'done' AND sq.product_id = sil.product_id
            AND sil.product_qty = sq.inventory_quantity
            AND ((sil.prod_lot_id IS NULL AND sq.lot_id IS NULL) OR
                sil.prod_lot_id = sq.lot_id)
            AND si.accounting_date IS NOT NULL""",
    )
