# Copyright 2024 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def fill_purchase_order_group_from_tenders(env):
    tender_type = env.ref("purchase_requisition.type_multi")
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE purchase_order_group
        ADD COLUMN IF NOT EXISTS old_purchase_requisition_id INTEGER
        """,
    )
    openupgrade.logged_query(
        env.cr,
        f"""
        INSERT INTO purchase_order_group (old_purchase_requisition_id,
            create_date, create_uid, write_date, write_uid)
        SELECT DISTINCT ON (pr.id) pr.id,
            pr.create_date, pr.create_uid, pr.write_date, pr.write_uid
        FROM purchase_requisition pr
        JOIN purchase_order po1 ON po1.requisition_id = pr.id
        JOIN purchase_order po2 ON po2.requisition_id = pr.id AND po1.id != po2.id
        -- only create group if there is more than one purchase
        WHERE pr.type_id = {tender_type.id}
        RETURNING old_purchase_requisition_id
        """,
    )
    tender_requisition_ids = [x[0] for x in env.cr.fetchall()]
    if tender_requisition_ids:
        openupgrade.logged_query(
            env.cr,
            """
            UPDATE purchase_order po
            SET purchase_group_id = pog.id
            FROM purchase_order_group pog
            WHERE po.requisition_id = pog.old_purchase_requisition_id
            """,
        )
    openupgrade.logged_query(
        env.cr,
        f"""
            SELECT pr.id
            FROM purchase_requisition pr
            WHERE pr.type_id = {tender_type.id}
            """,
    )
    obsolete_requisition_ids = [x[0] for x in env.cr.fetchall()]
    if obsolete_requisition_ids:
        openupgrade.logged_query(
            env.cr,
            f"""
            UPDATE purchase_order po
            SET requisition_id = NULL
            FROM purchase_requisition pr
            WHERE po.requisition_id = pr.id AND pr.type_id = {tender_type.id}
            """,
        )
        openupgrade.logged_query(
            env.cr,
            """
            UPDATE purchase_requisition pr
            SET state = 'draft'
            WHERE pr.state not in ('draft', 'cancel')
            """,
        )
        env["purchase.requisition"].browse(obsolete_requisition_ids).unlink()


@openupgrade.migrate()
def migrate(env, version):
    fill_purchase_order_group_from_tenders(env)
    openupgrade.delete_records_safely_by_xml_id(
        env,
        ["purchase_requisition.seq_purchase_tender", "purchase_requisition.type_multi"],
    )
