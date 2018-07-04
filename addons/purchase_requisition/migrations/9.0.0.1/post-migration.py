# -*- coding: utf-8 -*-
# © 2015 Eficent Business and IT Consulting Services S.L. -
# Jordi Ballester Alomar
# © 2015 Serpent Consulting Services Pvt. Ltd. - Sudhir Arya
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from psycopg2.extensions import AsIs
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(cr, version):
    # Mapping new values for purchase_requisition
    column = openupgrade.get_legacy_name('purchase_requisition')
    openupgrade.logged_query(
        cr, """UPDATE product_template SET purchase_requisition = 'rfq'
        WHERE %s IS NOT TRUE""", (AsIs(column),))
    openupgrade.logged_query(
        cr, """UPDATE product_template SET purchase_requisition = 'tenders'
        WHERE %s""",  (AsIs(column),))
