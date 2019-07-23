# Copyright 2019 Eficent <http://www.eficent.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def fill_purchase_requisition_currency_id(cr):
    """Assure the correct currency for each requisition"""
    openupgrade.logged_query(
        cr, """
        UPDATE purchase_requisition pr
        SET currency_id = po.currency_id
        FROM purchase_order po
        WHERE po.requisition_id = pr.id""",
    )


def map_purchase_requisition_state_ongoing(cr):
    openupgrade.logged_query(
        cr, """
        UPDATE purchase_requisition pr
        SET state = 'ongoing'
        FROM purchase_requisition_type prt
        WHERE pr.state = 'in_progress' AND pr.type_id = prt.id
            AND prt.quantity_copy = 'none' AND pr.vendor_id IS NOT NULL""",
    )


@openupgrade.migrate()
def migrate(env, version):
    fill_purchase_requisition_currency_id(env.cr)
    map_purchase_requisition_state_ongoing(env.cr)
    openupgrade.load_data(
        env.cr, 'purchase_requisition',
        'migrations/12.0.0.1/noupdate_changes.xml')
