# Copyright 2023 Coop IT Easy SC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def compute_sale_order_delivery_status(env):
    openupgrade.add_fields(
        env,
        [
            (
                "delivery_status",
                "sale.order",
                False,
                "selection",
                False,
                "sale_stock",
            )
        ],
    )
    openupgrade.logged_query(
        env.cr,
        """
        with so_delivery_status_sub as (
            select
                sale_id as id,
                case
                    when
                        count(*) filter (
                            where state = 'cancel'
                        ) = count(*)
                        then NULL
                    when
                        count(*) filter (
                            where state not in ('done', 'cancel')
                        ) = 0
                        then 'full'
                    when
                        count(*) filter (where state = 'done') > 0
                        then 'partial'
                    else 'pending'
                end as delivery_status
            from stock_picking
            group by 1
            order by 1
        ), so_delivery_status as (
            select
                sol.order_id as id,
                case
                    when
                        sub.delivery_status = 'partial' and count(*) filter (
                            where COALESCE(sol.qty_delivered,0) != 0
                        ) > 0
                        then 'started'
                    when sub.delivery_status IS NOT NULL
                        then sub.delivery_status
                    else NULL
                end as delivery_status
            from sale_order_line sol
            join so_delivery_status_sub sub ON sub.id = sol.order_id
            group by 1, sub.delivery_status
            order by 1
        )
        update sale_order as so
        set delivery_status = so_delivery_status.delivery_status
        from so_delivery_status
        where so_delivery_status.id = so.id AND so_delivery_status.delivery_status IS NOT NULL;
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    compute_sale_order_delivery_status(env)
