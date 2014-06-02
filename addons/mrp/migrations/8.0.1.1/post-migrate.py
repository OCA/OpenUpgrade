from openerp.openupgrade import openupgrade
from openerp import pooler, SUPERUSER_ID

def move_fields(cr, pool):
    execute = openupgrade.logged_query
    queries = [ """
    UPDATE product_product
    SET produce_delay=(SELECT pt.%s
                       FROM product_template
                       WHERE product_template.id=product_product.product_tmpl_id)
    """ % openupgrade.get_legacy_name('produce_delay'),


@openupgrade.migrate()
def migrate(cr, version):
    pool = pooler.get_pool(cr.dbname)
    move_fields(cr, pool)
    
