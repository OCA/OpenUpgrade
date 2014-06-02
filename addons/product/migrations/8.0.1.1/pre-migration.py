from openerp.openupgrade import openupgrade

column_renames = {
    # Using magic None value to trigger call to get_legacy_name()
    'product_supplierinfo': [
        ('product_id', None),
        ],
    'product_product': [
        ('color', None),
        ('image', 'image_variant'),
        ],
    'product_template': [
        ('produce_delay', None), # need to handle in mrp migration
        ],
    'product_packaging': [
        ('height', None),
        ('length', None),
        ('weight_ul', None),
        ('width', None),
        ]
        }


@openupgrade.migrate()
def migrate(cr, version):
    openupgrade.rename_columns(cr, column_renames)
