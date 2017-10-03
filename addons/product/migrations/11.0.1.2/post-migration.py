# -*- coding: utf-8 -*-
# © 2017 bloopark systems (<http://bloopark.de>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def map_product_tmpl_id_to_product_id(cr):
    """Set the product_id for the product_tmpl_id in product.packaging"""
    # fetching column names of table product_packaging for 'copy' of
    # additional product_packaging records per product_id later
    cr.execute("""
        SELECT column_name FROM information_schema.columns
        WHERE table_name='product_packaging';""")
    column_names = [r[0] for r in cr.fetchall() if r[0] != 'id' and r[0] !=
                    'product_id']
    # we consider only product_packaging with a related product_template
    cr.execute("""
        SELECT id, product_tmpl_id FROM product_packaging WHERE
        product_tmpl_id IS NOT NULL;""")
    package_rows = cr.fetchall()
    for r in package_rows:
        cr.execute("""
            SELECT id FROM product_product WHERE product_tmpl_id = %s;
        """, (r[1],))
        product_rows = cr.fetchall()
        if product_rows:
            # update existing product_packaging with the first product_id
            cr.execute("""
                UPDATE product_packaging
                SET product_id = %s WHERE id = %s;
            """, (product_rows[0][0], r[0],))
            # 'copy' existing product_packaging for additional
            # product_product records
            for p in product_rows[1:]:
                fields = values = column_names
                cr.execute("""
                   INSERT INTO product_packaging %s
                   SELECT %s
                   FROM product_packaging WHERE id = %%s""" % (
                    ','.join(fields + ['product_id']),
                    ','.join(values + [p[0]])), (r[0],))


@openupgrade.migrate()
def migrate(env, version):
    map_product_tmpl_id_to_product_id(env.cr)
