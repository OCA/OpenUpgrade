# -*- coding: utf-8 -*-
# © 2017 bloopark systems (<http://bloopark.de>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # Update email template purchase.email_template_edi_purchase
    tmpl_id = env.ref('purchase.email_template_edi_purchase').id
    env.cr.execute("""
        DELETE FROM ir_translation
        WHERE module = 'purchase'
        AND name = 'email.template,body_html'
        AND res_id = %s;
    """, (tmpl_id,))

    openupgrade.load_data(
        env.cr, 'purchase', 'migrations/11.0.1.2/noupdate_changes.xml',
    )

    # Update new field created_purchase_line_id at stock.move
    env.cr.execute("""
        UPDATE stock_move sm
        SET created_purchase_line_id = po.purchase_line_id
        FROM procurement_order po
        WHERE sm.procurement_id = po.id;
    """)

    # Update new field orderpoint_id at purchase.order.line
    env.cr.execute("""
        UPDATE purchase_order_line pol
        SET orderpoint_id = po.orderpoint_id
        FROM procurement_order po
        WHERE pol.id = po.purchase_line_id
    """)
