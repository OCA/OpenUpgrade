# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_field_renames = [
    ('product.template', 'product_template', 'product_image_ids', 'product_template_image_ids'),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_fields(env, _field_renames)
