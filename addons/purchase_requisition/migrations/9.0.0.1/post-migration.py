# -*- coding: utf-8 -*-
# © 2016 Eficent Business and IT Consulting Services S.L.
# © 2016 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(cr, version):
    # Mapping new values for purchase_requisition
    openupgrade.map_values(
        cr, openupgrade.get_legacy_name('purchase_requisition'),
        'purchase_requisition', [(True, 'tenders'), (False, 'rfq')],
        table='product_template')
