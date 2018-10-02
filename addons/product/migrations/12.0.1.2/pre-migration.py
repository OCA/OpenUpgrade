from openupgradelib import openupgrade

@openupgrade.migrate()
def migrate(env, version):

    model_rename = [
        ('product.attribute.line', 'product.template.attribute.line'),
        ('product.attribute.price', 'product.template.attribute.value')
    ]
    table_rename = [('product_attribute_line', 'product_template_attribute_line')]

    column_rename = {
        'product_attribute_price': [('value_id', 'product_attribute_value_id')]
    }

    openupgrade.rename_columns(env.cr, column_rename)
    openupgrade.rename_models(env.cr, model_rename)
    openupgrade.rename_tables(env.cr, table_rename)
