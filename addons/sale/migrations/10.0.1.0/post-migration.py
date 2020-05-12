# -*- coding: utf-8 -*-
# © 2017 bloopark systems (<http://bloopark.de>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def _fill_sale_order_confirmation_date(cr):
    """This fills the field with a date found for a tracking value
    that changes state. Two strategies are used:

    * If the state of the order is `sale`, last tracking value is selected, as
      it will match with the confirmation step.
    * If the state of the order is `done`, we can't use last, but first one
      is also not the good one if the order has been sent by mail, but we use
      it as the best one.
    """
    openupgrade.logged_query(
        cr, """
        UPDATE sale_order so
        SET confirmation_date = sub.confirmation_date
        FROM (
            SELECT so.id as id,
                CASE
                    WHEN so.state = 'sale' THEN MAX(mtv.create_date)
                    ELSE MIN(mtv.create_date)
                END as confirmation_date
            FROM sale_order so,
                mail_tracking_value mtv,
                mail_message mm
            WHERE mm.res_id = so.id
                AND mm.model = 'sale.order'
                AND mtv.mail_message_id = mm.id
                AND mtv.field = 'state'
                AND so.confirmation_date IS NULL
            GROUP BY so.id
        ) as sub
        WHERE sub.id = so.id""",
    )


@openupgrade.migrate(use_env=False)
def migrate(cr, version):
    # map old / non existing value 'cost' to default value 'order'
    openupgrade.map_values(
        cr,
        openupgrade.get_legacy_name('invoice_policy'), 'invoice_policy',
        [('cost', 'order')],
        table='product_template', write='sql')
    openupgrade.load_data(
        cr, 'sale', 'migrations/10.0.1.0/noupdate_changes.xml',
    )
    _fill_sale_order_confirmation_date(cr)
