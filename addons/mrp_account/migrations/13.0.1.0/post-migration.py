# Copyright 2020 Andrii Skrypka
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def set_mrp_workorder_product_uom_id(cr):
    openupgrade.logged_query(
        cr, """
        UPDATE mrp_workorder w
        SET    product_uom_id = pt.uom_id
        FROM   product_product pp
        JOIN   product_template pt ON pp.product_tmpl_id = pt.id
        WHERE  w.product_id = pp.id
        AND    w.product_uom_id IS NULL;
        """
    )


@openupgrade.migrate()
def migrate(env, version):
    set_mrp_workorder_product_uom_id(env.cr)
