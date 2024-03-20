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
        with so_delivery_status as (
            select
                sale_id as id,
                case
                    when
                        count(state) filter (
                            where state = 'cancel'
                        ) = count(state)
                        then null
                    when
                        count(state) filter (
                            where state not in ('done', 'cancel')
                        ) = 0
                        then 'full'
                    when
                        count(state) filter (where state = 'done') > 0
                        then 'partial'
                    else 'pending'
                end as delivery_status
            from stock_picking
            group by 1
            order by 1
        )
        update sale_order as so
        set delivery_status = so_delivery_status.delivery_status
        from so_delivery_status
        where so_delivery_status.id = so.id;
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    compute_sale_order_delivery_status(env)
