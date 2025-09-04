# Copyright 2024,2025 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def fill_purchase_order_group_from_tenders(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE purchase_order_group
        ADD COLUMN IF NOT EXISTS old_purchase_requisition_id INTEGER
        """,
    )
    # Create a group if there is more than one PO per requisition
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO purchase_order_group
        (old_purchase_requisition_id, create_date, create_uid, write_date, write_uid)
        SELECT
            t.requisition_id, pr.create_date, pr.create_uid, pr.write_date, pr.write_uid
        FROM (
            SELECT *, row_number()
            over (partition BY requisition_id ORDER BY id) AS rnum
            FROM purchase_order
        ) t
        JOIN purchase_requisition pr ON pr.id = t.requisition_id
        WHERE t.rnum = 2;
        """,
    )
    # Assign it to the purchase orders
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE purchase_order po
        SET purchase_group_id = pog.id
        FROM purchase_order_group pog
        WHERE po.requisition_id = pog.old_purchase_requisition_id
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    fill_purchase_order_group_from_tenders(env)
    openupgrade.delete_records_safely_by_xml_id(
        env,
        ["purchase_requisition.seq_purchase_tender", "purchase_requisition.type_multi"],
    )
