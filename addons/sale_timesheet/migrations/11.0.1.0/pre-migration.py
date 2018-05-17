# Copyright 2018 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

COLUMN_COPIES = {
    'product_template': [
        ('service_type', None, None),
    ],
}


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.copy_columns(env.cr, COLUMN_COPIES)
    try:
        with env.cr.savepoint():
            env.ref('sale_timesheet.duplicate_field_xmlid').unlink()
    except Exception:
        pass
