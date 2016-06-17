# -*- coding: utf-8 -*-
# © 2016 Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade, openupgrade_80
from openerp import api, pooler, SUPERUSER_ID


def _copy_purchase_order_line_quantity_as_bid(cr):
    openupgrade.logged_query(
        cr, """
        UPDATE purchase_order_line
        SET quantity_bid=product_qty
        WHERE
            id IN (
                SELECT pol.id
                FROM purchase_order po, purchase_order_line pol
                WHERE
                    pol.order_id = po.id AND
                    po.requisition_id IS NOT NULL
            )""")


def _create_workflows_for_requisitions(cr):
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        requisitions = env['purchase.requisition'].search(
            [('state', 'in', ['draft', 'in_progress'])])
        model = 'purchase.requisition'
        workflow = env.ref(
            'purchase_requisition.purchase_requisition_workflow')
        activities = {
            'draft': env.ref('purchase_requisition.act_draft'),
            'in_progress': env.ref('purchase_requisition.act_sent'),
        }
        for requisition in requisitions:
            # Instantiate the workflow
            cr.execute("""
                INSERT INTO wkf_instance
                (res_type, res_id, uid, wkf_id, state)
                VALUES (%s, %s, %s, %s, 'active')
                RETURNING id
                """, (model, requisition.id, SUPERUSER_ID, workflow.id))
            instance_id = cr.fetchone()[0]
            # Put the workflow instance in its correct activity
            cr.execute("SELECT nextval('wkf_workitem_id_seq')")
            id_new = cr.fetchone()[0]
            cr.execute("""
                insert into wkf_workitem
                (id, act_id, inst_id, state)
                VALUES (%s, %s, %s, 'active')
                """, (id_new, activities[requisition.state].id, instance_id))


def _fill_procurement_id_from_requisition(cr):
    """Fills the counterpart of the requisition from the procurement order."""
    openupgrade.logged_query(
        cr, """
        UPDATE purchase_requisition pr
        SET procurement_id=po.id
        FROM procurement_order po
        WHERE po.requisition_id = pr.id
        """)


@openupgrade.migrate()
def migrate(cr, version):
    pool = pooler.get_pool(cr.dbname)
    openupgrade_80.set_message_last_post(
        cr, SUPERUSER_ID, pool, ['purchase.requisition'])
    openupgrade.move_field_m2o(
        cr, pool, 'product.product',
        openupgrade.get_legacy_name('purchase_requisition'), 'product_tmpl_id',
        'product.template', 'purchase_requisition')
    _copy_purchase_order_line_quantity_as_bid(cr)
    openupgrade.set_defaults(
        cr, pool, {
            'purchase.requisition': [
                ('picking_type_id', None),
            ],
        })
    _create_workflows_for_requisitions(cr)
    _fill_procurement_id_from_requisition(cr)
    openupgrade.load_data(
        cr, 'purchase_requisition', 'migrations/8.0.0.1/noupdate_changes.xml')
