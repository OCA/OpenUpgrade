# Copyright 2018 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def update_move_dest_id(env):
    openupgrade.logged_query(
        env.cr, """
        UPDATE purchase_requisition_line prl
        SET move_dest_id = po.move_dest_id
        FROM procurement_order po, purchase_requisition pr
        WHERE prl.requisition_id = pr.id
        AND pr.procurement_id = po.id """
    )


@openupgrade.migrate()
def migrate(env, version):
    update_move_dest_id(env)
