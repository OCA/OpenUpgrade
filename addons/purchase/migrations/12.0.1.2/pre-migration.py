# Copyright 2019 Eficent <http://www.eficent.com>
# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

xmlid_renames = [
    ('purchase.route_warehouse0_buy', 'purchase_stock.route_warehouse0_buy'),
]


def precompute_pol_product_uom_qty(env):
    """when computing product_uom_qty in _compute_product_uom_qty(),
    we need to avoid the UserError in _compute_quantity()"""
    openupgrade.add_fields(
        env, [
            ('product_uom_qty', 'purchase.order.line', 'purchase_order_line',
             'float', 'double precision', 'purchase'),
        ],
    )
    # On first place, assign the same value when UoM has not changed
    openupgrade.logged_query(
        env.cr, """
        UPDATE purchase_order_line
        SET product_uom_qty = product_qty""",
    )
    # Then, only auto-switch UoM of lines when they are in draft
    openupgrade.logged_query(
        env.cr, """
        UPDATE purchase_order_line upd_pol
        SET product_uom = pt.uom_id
        FROM purchase_order_line pol
        JOIN product_product pp ON pol.product_id = pp.id
        JOIN product_template pt ON pp.product_tmpl_id = pt.id
        JOIN uom_uom uu ON pol.product_uom = uu.id
        JOIN uom_uom uu2 ON pt.uom_id = uu2.id
        WHERE uu.category_id != uu2.category_id
            AND pol.state = 'draft'
            AND upd_pol.id = pol.id""",
    )
    # Lastly, perform conversion when different UoMs, ignoring incompatible
    # UoM categories
    openupgrade.logged_query(
        env.cr, """
        UPDATE purchase_order_line upd_pol
        SET product_uom_qty = pol.product_qty / uu.factor * uu2.factor
        FROM purchase_order_line pol
        JOIN product_product pp ON pol.product_id = pp.id
        JOIN product_template pt ON pp.product_tmpl_id = pt.id
        JOIN uom_uom uu on uu.id = pol.product_uom
        JOIN uom_uom uu2 on uu2.id = pt.uom_id
        WHERE upd_pol.id = pol.id
            AND pol.product_uom != pt.uom_id""",
    )


def fill_purchase_order_user_id(cr):
    if not openupgrade.column_exists(cr, 'purchase_order', 'user_id'):
        # Done here because user_id is filled automatically when upgrading
        cr.execute(
            """
            ALTER TABLE purchase_order ADD COLUMN user_id integer;
            """)
    openupgrade.logged_query(
        cr, """
        UPDATE purchase_order
        SET user_id = create_uid
        WHERE user_id IS NULL""",
    )


@openupgrade.migrate()
def migrate(env, version):
    fill_purchase_order_user_id(env.cr)
    precompute_pol_product_uom_qty(env)
    openupgrade.rename_xmlids(env.cr, xmlid_renames)
