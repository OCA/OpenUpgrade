# Copyright 2017 Camptocamp
# Copyright 2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade
from odoo.addons.base.ir.ir_actions import IrActionsServer

model_renames_base_action_rule = [
    ('base.action.rule', 'base.automation')
]

table_renames_base_action_rule = [
    ('base_action_rule', 'base_automation')
]

xmlid_renames_base_action_rule = [
    ('base_automation.ir_cron_crm_action',
     'base_automation.ir_cron_data_base_automation_check')
]


def migrate_base_action_rule(cr):
    """ base.action.rule renamed base.automation
    Models, table and xmlid renaming
    """
    openupgrade.rename_models(cr, model_renames_base_action_rule)
    openupgrade.rename_tables(cr, table_renames_base_action_rule)
    openupgrade.rename_xmlids(cr, xmlid_renames_base_action_rule)


def create_ir_actions_server(env):
    """Fill delegate field action_server_id by creating the related
    ir.actions.server most of the field values will go in ir.actions.server.

    Fill also m2m table for server actions to run.
    """
    openupgrade.add_fields(
        env, [
            ('action_server_id', 'base.automation', 'base_automation',
             'many2one', False, 'base_automation'),
        ],
    )
    default_vals = {
        'code': IrActionsServer.DEFAULT_PYTHON_CODE,
        'state': 'multi',
        'type': 'ir.actions.server',
        'usage': 'base_automation',
        'binding_type': 'action',
    }
    env.cr.execute("""
        SELECT ba.id, ba.create_uid, ba.create_date, ba.write_uid,
            ba.write_date, ba.name, ba.sequence, ba.model_id, ba.kind,
            ba.filter_id, ba.filter_pre_id, im.model
        FROM base_automation AS BA,
            ir_model AS im
        WHERE
            im.id = ba.model_id
    """)
    for act in env.cr.dictfetchall():
        vals = default_vals.copy()
        vals.update({
            'create_uid': act['create_uid'],
            'create_date': act['create_date'],
            'write_uid': act['write_uid'],
            'write_date': act['write_date'],
            'name': act['name'],
            'model_id': act['model_id'],
            'model_name': act['model'],
            'sequence': act['sequence'],
        })
        for old_field, new_field in [
            ('filter_id', 'filter_domain'),
            ('filter_pre_id', 'filter_pre_domain'),
        ]:
            if act.get(old_field):
                f = env['ir.filters'].browse(act[old_field])
                vals[new_field] = f.domain
        openupgrade.logged_query(
            env.cr, """
            INSERT INTO ir_act_server
              (create_uid, create_date, write_uid, write_date, binding_type,
               code, state, type, usage, name, model_id, model_name, sequence)
            VALUES (
              %(create_uid)s, %(create_date)s, %(write_uid)s, %(write_date)s,
              %(binding_type)s, %(code)s, %(state)s, %(type)s, %(usage)s,
              %(name)s, %(model_id)s, %(model_name)s, %(sequence)s
            )
            RETURNING id""", vals,
        )
        srv_act_id = env.cr.fetchone()[0]
        # Transfer server actions to run
        openupgrade.logged_query(
            env.cr, """
            INSERT INTO rel_server_actions
                (server_id, action_id)
            SELECT
                %s, ir_act_server_id
            FROM base_action_rule_ir_act_server_rel
            WHERE base_action_rule_id = %s
            """, (srv_act_id, act['id']),
        )
        # Write in the base.automation record the parent ir.actions.server ID
        # and possible filters
        set_query = "action_server_id = %s"
        params = [srv_act_id]
        for field in ['filter_domain', 'filter_pre_domain']:
            if vals.get(field):
                set_query += ', %s = %%s' % field
                params.append(vals[field])
        params.append(act['id'])
        query = 'UPDATE base_automation SET %s WHERE id = %%s' % set_query
        openupgrade.logged_query(env.cr, query, tuple(params))


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    migrate_base_action_rule(env.cr)
    create_ir_actions_server(env)
