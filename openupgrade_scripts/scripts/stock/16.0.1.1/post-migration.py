from openupgradelib import openupgrade


def _complete_stock_move_quantity_done_with_orm(env):
    """In pre-migration we left out the moves with lines with different units of
    measure to be treated by the ORM"""
    env.cr.execute(
        """
        SELECT
            move_id
        FROM
            stock_move_line
        GROUP BY
            move_id
        HAVING
            COUNT(DISTINCT product_uom_id) > 1 AND
            SUM(qty_done) <> 0
    """
    )
    move_ids = [id for id, *_ in env.cr.fetchall() if id]
    env["stock.move"].browse(move_ids)._quantity_done_compute()


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env.cr, "stock", "16.0.1.1/noupdate_changes.xml")
    _complete_stock_move_quantity_done_with_orm(env)
