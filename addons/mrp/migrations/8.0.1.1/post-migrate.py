from openerp.openupgrade import openupgrade
from openerp import pooler


def move_fields(cr, pool):
    execute = openupgrade.logged_query
    queries = [
        """
        UPDATE product_template
        SET produce_delay = (
            SELECT pt.%s
            FROM product_template pt
            WHERE pt.id = product_product.product_tmpl_id)
        """ % openupgrade.get_legacy_name('produce_delay'),
    ]
    for sql in queries:
        execute(cr, sql)


@openupgrade.migrate()
def migrate(cr, version):
    pool = pooler.get_pool(cr.dbname)
    move_fields(cr, pool)
