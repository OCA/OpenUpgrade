from openupgradelib import openupgrade

@openupgrade.migrate(no_version=True)
def migrate(env, version):

    model_rename = [
        ('product.uom', 'uom.uom'),
        ('product.uom.category', 'uom.category')
    ]

    table_rename = [
        ('product_uom', 'uom_uom'),
        ('product_uom_categ', 'uom_category')
    ]

    xmlids_rename = [
        ('product.group_uom', 'uom.group_uom'),
        ('product.product_uom_categ_unit', 'uom.product_uom_categ_unit'),
        ('product.product_uom_categ_kgm', 'uom.product_uom_categ_kgm'),
        ('product.uom_categ_wtime', 'uom.uom_categ_wtime'),
        ('product.uom_categ_length', 'uom.uom_categ_length'),
        ('product.product_uom_unit', 'uom.product_uom_unit'),
        ('product.product_uom_dozen', 'uom.product_uom_dozen'),
        ('product.product_uom_kgm', 'uom.product_uom_kgm'),
        ('product.product_uom_hour', 'uom.product_uom_hour'),
        ('product.product_uom_day', 'uom.product_uom_day'),
        ('product.product_uom_ton', 'uom.product_uom_ton'),
        ('product.product_uom_meter', 'uom.product_uom_meter'),
        ('product.product_uom_km', 'uom.product_uom_km'),
        ('product.product_uom_litre', 'uom.product_uom_litre'),
        ('product.product_uom_lb', 'uom.product_uom_lb'),
        ('product.product_uom_oz', 'uom.product_uom_oz'),
        ('product.product_uom_cm', 'uom.product_uom_cm'),
        ('product.product_uom_inch', 'uom.product_uom_inch'),
        ('product.product_uom_foot', 'uom.product_uom_foot'),
        ('product.product_uom_mile', 'uom.product_uom_mile'),
        ('product.product_uom_floz', 'uom.product_uom_floz'),
        ('product.product_uom_gal', 'uom.product_uom_gal'),
    ]



    openupgrade.rename_models(env.cr, model_rename)
    openupgrade.rename_tables(env.cr, table_rename)
    openupgrade.rename_xmlids(env.cr, xmlids_rename)
