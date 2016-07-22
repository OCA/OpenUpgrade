# -*- coding: utf-8 -*-
# © 2016 Eficent Business and IT Consulting Services S.L.
# © 2016 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


column_spec = {
    'product_template': [
        ('purchase_requisition', None, None),
    ],
}


@openupgrade.migrate()
def migrate(cr, version):
    openupgrade.copy_columns(cr, column_spec)
