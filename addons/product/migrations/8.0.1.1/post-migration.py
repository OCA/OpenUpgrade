from openerp.openupgrade import openupgrade
from openerp import pooler, SUPERUSER_ID

def load_data(cr):
    openupgrade.load_data(cr, 'product', 'migrations/8.0.1.1/modified_data.xml', mode='init')

def move_fields(cr, pool):
    execute = openupgrade.logged_query
    queries = [ """
    UPDATE product_supplierinfo
    SET product_tmpl_id=(SELECT product_tmpl_id
                         FROM product_product
                         WHERE product_product.id=product_supplierinfo.%s)
    """ % openupgrade.get_legacy_name('product_id'),
    """
    UPDATE product_template as pt
    SET color=(SELECT pp1.%s 
          FROM product_product as pp1
          WHERE pp1.product_tmpl_id=pt.id ORDER BY pp1.id LIMIT 1),
        image=(SELECT pp2.%s 
          FROM product_product as pp2
          WHERE pp2.product_tmpl_id=pt.id ORDER BY pp2.id LIMIT 1)
    """ % (openupgrade.get_legacy_name('color'),
           openupgrade.get_legacy_name('image')
           ),
                ]
    for sql in queries:
        execute(cr, sql)

@openupgrade.migrate()
def migrate(cr, version):
    pool = pooler.get_pool(cr.dbname)
    move_fields(cr, pool)
    load_data(cr)
    
