from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.logged_query(
        env.cr,
        """
        WITH subquery as (
            SELECT op.name as origin, p.id as pid
            FROM stock_warehouse_orderpoint AS op
            LEFT JOIN procurement_group AS p ON op.group_id = p.id
        )
        UPDATE purchase_requisition as requisition
        SET procurement_group_id = subquery.pid
        FROM subquery
        WHERE requisition.origin = subquery.origin;
        """,
    )
