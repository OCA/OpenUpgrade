# Copyright 2019 Eficent <http://www.eficent.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def fix_bad_pol_uom_data(env):
    """when computing product_uom_qty in _compute_product_uom_qty(),
    we need to avoid the UserError in _compute_quantity()"""
    env.cr.execute(
        """ALTER TABLE purchase_order_line
        ADD COLUMN product_uom_qty DOUBLE PRECISION""",
    )
    openupgrade.logged_query(
        env.cr, """
        UPDATE purchase_order_line upd_pol
        SET product_uom = pt.uom_id, product_uom_qty = pol.product_qty
        FROM purchase_order_line pol
        JOIN product_product pp ON pol.product_id = pp.id
        JOIN product_template pt ON pp.product_tmpl_id = pt.id
        JOIN uom_uom uom1 ON pol.product_uom = uom1.id
        JOIN uom_uom uom2 ON pt.uom_id = uom2.id
        WHERE uom1.category_id != uom2.category_id AND upd_pol.id = pol.id"""
    )


@openupgrade.migrate()
def migrate(env, version):
    fix_bad_pol_uom_data(env)
