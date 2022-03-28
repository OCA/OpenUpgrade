# Copyright 2019 Eficent <http://www.eficent.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def switch_mrp_xml_id_noupdate(cr):
    """Some references records have an associated XML-ID, that was
    updated in v11 through a method and maintain as XML noupdate=0 data, so
    they weren't removed on updates, but now on v12, that XML-IDs are
    noupdate=1, and no XML data in provided, so on regular update process, they
    are tried to be removed. We switch them to noupdate=1 for avoiding this
    problem.
    """
    openupgrade.logged_query(
        cr, """
        UPDATE ir_model_data
        SET noupdate = True
        WHERE module = 'mrp'
        AND name IN %s""", ((
            'picking_type_manufacturing',
        ), ),
    )


def precompute_mrp_production__product_uom_qty(env):
    """Precompute the product_uom_qty field of mrp.production."""
    openupgrade.add_fields(
        env, [
            (
                "product_uom_qty",
                "mrp.production",
                "mrp_production",
                "float",
                False,
                "mrp",
            ),
        ]
    )
    openupgrade.logged_query(
        env.cr,
        """UPDATE mrp_production mp
        SET product_uom_qty = product_qty
        FROM product_product pp
        JOIN product_template pt ON pp.product_tmpl_id = pt.id
        WHERE pp.id = mp.product_id
            AND mp.product_uom_id = pt.uom_id
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """UPDATE mrp_production mp
        SET product_uom_qty = round(product_qty / uu2.factor * uu.factor, 4)
        FROM product_product pp, uom_uom uu2, product_template pt, uom_uom uu
        WHERE pp.id = mp.product_id
            AND pp.product_tmpl_id = pt.id
            AND pt.uom_id = uu.id
            AND mp.product_uom_id = uu2.id
            AND mp.product_uom_id != pt.uom_id
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    switch_mrp_xml_id_noupdate(env.cr)
    precompute_mrp_production__product_uom_qty(env)
