from openerp.openupgrade import openupgrade
from openerp import pooler, SUPERUSER_ID

def load_data(cr):
    openupgrade.load_data(cr, 'product', 'migrations/8.0.1.1/modified_data.xml', mode='init')

def move_fields(cr, pool):
    execute = openupgrade.logged_query
    queries = ["UPDATE product_supplierinfo "
               "SET product_tmpl_id=(SELECT product_tmpl_id "
               "          FROM product_product "
               "          WHERE product_product.id=product_supplierinfo.%s) " \
               % openupgrade.get_legacy_name('product_id'),
               #
               "UPDATE product_template as pt " 
               "SET color=(SELECT pp1.%s "
               "      FROM product_product as pp1 "
               "      WHERE pp1.product_tmpl_id=pt.id ORDER BY pp1.id LIMIT 1), "
               "    image=(SELECT pp2.image_variant "
               "      FROM product_product as pp2 "
               "      WHERE pp2.product_tmpl_id=pt.id ORDER BY pp2.id LIMIT 1)" 
               "    packaging=(SELECT pp3.%s "
               "      FROM product_product as pp3 "
               "      WHERE pp3.product_tmpl_id=pt.id ORDER BY pp3.id LIMIT 1)" \
               % (openupgrade.get_legacy_name('color'),
                  openupgrade.get_legacy_name('packaging'),
                  )
               #
               
               ]
    for sql in queries:
        execute(cr, sql)

def copy_fields(cr, pool):
    product_tmpl= pool['product.template']
    product_obj= pool['product.product']
    # copy the active field from product to template
    ctx = {'active_test': False}
    tmpl_ids = product_tmpl.search(cr, SUPERUSER_ID, [], context=ctx)
    for template in product_tmpl.browse(cr, SUPERUSER_ID, tmpl_ids, context=ctx):
        template.write({'active': any(variant.active
                                      for variant in template.product_variant_ids)
                        })

def migrate_packaging(cr, pool):
    """create 1 product UL for each different product packaging dimension
    and link it to the packagings
    """
    packaging_obj = pool['product.packaging']
    ul_obj = pool['product.ul']
    packaging_ids = packaging_obj.search(cr, SUPERUSER_ID, [])
    for packaging in packaging_obj.browse(cr, SUPERUSER_ID, packaging_ids):
        ul = packaging.ul
        ul.write({'height': height,
                  'width': width,
                  'length': length,
                  'weight_ul': weight,
                  })
        
@openupgrade.migrate()
def migrate(cr, version):
    pool = pooler.get_pool(cr.dbname)
    move_fields(cr, pool)
    copy_fields(cr, pool)
    migrate_packaging(cr, pool)
    load_data(cr)
    
