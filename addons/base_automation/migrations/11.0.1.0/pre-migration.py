# Copyright 2017 Camptocamp
# Copyright 2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

DEFAULT_PYTHON_CODE = """# Available variables:
#  - env: Odoo Environment on which the action is triggered
#  - model: Odoo Model of the record on which the action is triggered; is a void recordset
#  - record: record on which the action is triggered; may be be void
#  - records: recordset of all records on which the action is triggered in multi-mode; may be void
#  - time, datetime, dateutil, timezone: useful Python libraries
#  - log: log(message, level='info'): logging function to record debug information in ir.logging table
#  - Warning: Warning Exception to use with raise
# To return an action, assign: action = {...}\n\n\n\n"""

model_renames_base_action_rule = [
    ('base.action.rule', 'base.automation')
]

table_renames_base_action_rule = [
    ('base_action_rule', 'base_automation')
]

xmlid_renames_base_action_rule = [
    ('base_automation.ir_cron_data_bar_check',
     'base_automation.ir_cron_data_base_automation_check')
]


def migrate_base_action_rule(cr):
    """ base.action.rule renamed base.automation
    Models, table and xmlid renaming
    """
    if openupgrade.is_module_installed(cr, 'base_action_rule'):
        openupgrade.rename_models(cr, model_renames_base_action_rule)
        openupgrade.rename_tables(cr, table_renames_base_action_rule)
        openupgrade.rename_xmlids(cr, xmlid_renames_base_action_rule)


def create_ir_actions_server(env):
    """ base.automation

    fill delegate field action_server_id by creating the related
    ir.actions.server most of the field values will go in ir.actions.server.

    These fields don't have a replacement:

    * act_user_id: This is for forcing to write in the record the "user_id"
      field with that value. Very specific.
    """
    cr = env.cr
    default_vals = {
        'code': DEFAULT_PYTHON_CODE,
        'state': 'object_write',
        'type': 'ir.actions.server',
        'usage': 'base_automation',
    }
    cr.execute("""
        SELECT id, create_uid, create_date, write_uid, write_date
          name, sequence, model_id, kind, filter_id, filter_pre_id
        FROM base_automation
        WHERE action_server_id IS NULL
    """)
    rows = cr.fetchall()
    for row in rows:
        act = dict(row)
        vals = default_vals.copy()
        vals.update({
            'create_uid': act['create_uid'],
            'create_date': act['create_date'],
            'write_uid': act['write_uid'],
            'write_date': act['write_date'],
            'name': act['name'],
            'model_id': act['model_id'],
            'sequence': act['sequence'],
            'trigger': act['kind'],
        })
        for old_field, new_field in [
            ('filter_id', 'filter_domain'),
            ('filter_pre_id', 'filter_pre_domain'),
        ]:
            if act.get(old_field):
                f = env['ir.filters'].browse(act[old_field])
                vals[new_field] = f.domain
        cr.execute("""
            INSERT INTO ir_act_server
              (create_uid, create_date, write_uid, write_date,
               code, state, type, usage,
               name, model_id, sequence, trigger)
            VALUES (
              %(create_uid)s, %(create_date)s, %(write_uid)s, %(write_date)s,
              %(code)s, %(state)s, %(type)s, %(usage)s,
              %(name)s, %(model_id)s, %(sequence)s, %(trigger)s
            )
            RETURNING id
        """, vals)
        srv_act_id = cr.fetchone()[0]
        cr.execute(
            "UPDATE base_automation SET action_server_id = %s WHERE id = %s",
            (srv_act_id, act['id']))


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    migrate_base_action_rule(env.cr)
    create_ir_actions_server(env)
