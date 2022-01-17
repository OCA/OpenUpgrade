from openupgradelib import openupgrade


def convert_field_m2o_to_o2m(env):
    openupgrade.m2o_to_x2m(
        env.cr, env["pos.order"], "pos_order", "picking_ids", "picking_id"
    )


def fill_sesion_on_picking_by_pos_order(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE stock_picking
        SET pos_session_id = (SELECT session_id
                                FROM pos_order
                                WHERE pos_order.id = stock_picking.pos_order_id
                                LIMIT 1)
        WHERE pos_session_id IS NULL AND pos_order_id IS NOT NULL;
        """,
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
        SET state = CASE
                        WHEN pc.cash_control=True AND
                        COALESCE(ps.rescue,False)=False THEN 'opening_control'
                        ELSE 'opened'
                    END
        FROM pos_config pc
        WHERE pc.id = ps.config_id AND ps.state = 'new_session';
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    convert_field_m2o_to_o2m(env)
    fill_sesion_on_picking_by_pos_order(env)
    set_point_of_sale_update_stock_quantities_to_real(env)
    transfer_new_session_state(env)
    openupgrade.load_data(env.cr, "point_of_sale", "14.0.1.0.1/noupdate_changes.xml")
