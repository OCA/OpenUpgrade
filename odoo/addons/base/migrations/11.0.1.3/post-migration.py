# -*- coding: utf-8 -*-
# © 2017 bloopark systems (<http://bloopark.de>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def map_ir_actions_server_fields(cr):
    """Map field menu_ir_values_id with the help of field model_id to field
    binding_model_id. Use value 'action' for field binding_type. Delete
    ir.values record at the end."""
    cr.execute("""
        SELECT id, model_id, %(menu_ir_values_id)s FROM ir_act_server
        WHERE %(menu_ir_values_id)s IS NOT NULL;
    """ % {
        'menu_ir_values_id': openupgrade.get_legacy_name('menu_ir_values_id')
    })
    for r in cr.fetchall():
        query = ("UPDATE ir_act_server SET binding_model_id = %s "
                 "AND binding_type = 'action' WHERE id = %s;"
                 "DELETE FROM ir_values WHERE id = %s;")
        openupgrade.logged_query(cr, query, (r[1], r[0], r[2]))


@openupgrade.migrate(use_env=False)
def migrate(cr, version):
    map_ir_actions_server_fields(cr)
    openupgrade.load_data(
        cr, 'base', 'migrations/11.0.1.3/noupdate_changes.xml',
    )
