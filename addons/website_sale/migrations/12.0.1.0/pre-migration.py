# Copyright 2019 Eficent <http://www.eficent.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_field_renames = [
    ('product.template', 'product_template',
     'website_published', 'is_published'),
]

_column_renames = {
    'res_partner': [('last_website_so_id', None)],
}


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_fields(env, _field_renames)
    openupgrade.rename_columns(env.cr, _column_renames)
