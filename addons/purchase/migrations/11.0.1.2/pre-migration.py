# -*- coding: utf-8 -*-
# Copyright 2017 bloopark systems (<http://bloopark.de>)
# Copyright 2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.delete_record_translations(
        env.cr, 'purchase', ['email_template_edi_purchase'],
    )
    from odoo.addons.purchase.models.purchase import PurchaseOrder
    PurchaseOrder._openupgrade_recompute_fields_blacklist = [
        'picking_count',
        'picking_ids',
        'invoice_count',
        'invoice_ids',
    ]
