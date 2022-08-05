from openupgradelib import openupgrade


def convert_pos_order_pickings(env):
    openupgrade.m2o_to_x2m(
        env.cr, env["pos.order"], "pos_order", "picking_ids", "picking_id"
    )


def fill_sesion_on_picking_by_pos_order(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE stock_picking sp
        SET pos_session_id =  po.session_id
        FROM pos_order po
        WHERE po.id = sp.pos_order_id
            AND sp.pos_session_id IS NULL""",
    )


def set_point_of_sale_update_stock_quantities_to_real(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE res_company
        SET point_of_sale_update_stock_quantities = 'real';
        """,
    )


def transfer_new_session_state(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE pos_session ps
        SET state =
            CASE
               WHEN pc.cash_control AND NOT COALESCE(ps.rescue, FALSE)
               THEN 'opening_control'
               ELSE 'opened'
            END
        FROM pos_config pc
        WHERE pc.id = ps.config_id AND ps.state = 'new_session';
        """,
    )


def activate_pos_config_manage_orders(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE pos_config
        SET manage_orders = TRUE""",
    )


@openupgrade.migrate()
def migrate(env, version):
    convert_pos_order_pickings(env)
    fill_sesion_on_picking_by_pos_order(env)
    set_point_of_sale_update_stock_quantities_to_real(env)
    transfer_new_session_state(env)
    activate_pos_config_manage_orders(env)
    openupgrade.load_data(env.cr, "point_of_sale", "14.0.1.0.1/noupdate_changes.xml")
