from openupgradelib import openupgrade


def remove_obsolete_sale_order_kanban_view(env):
    """
    Remove the outdated kanban view entry for 'action_quotations' (Odoo 17)
    to prevent duplicate key constraint violation during migration to Odoo 18.
    """
    openupgrade.logged_query(
        env.cr,
        """
        SELECT v.id
        FROM ir_act_window_view v
        JOIN ir_model_data d ON d.res_id = v.id
        AND d.model = 'ir.actions.act_window.view'
        WHERE d.module = 'sale'
          AND d.name = 'sale_order_action_view_quotation_kanban'
        """,
    )
    result = env.cr.fetchone()

    if result:
        view_id = result[0]
        openupgrade.logged_query(
            env.cr, "DELETE FROM ir_act_window_view WHERE id = %s", (view_id,)
        )
        openupgrade.logged_query(
            env.cr,
            """
            DELETE FROM ir_model_data
            WHERE model = 'ir.actions.act_window.view'
              AND module = 'sale'
              AND name = 'sale_order_action_view_quotation_kanban'
            """,
        )


_xmlids_renames = [
    (
        "product.group_discount_per_so_line",
        "sale.group_discount_per_so_line",
    ),
]


@openupgrade.migrate()
def migrate(env, version):
    remove_obsolete_sale_order_kanban_view(env)
    openupgrade.rename_xmlids(env.cr, _xmlids_renames)
