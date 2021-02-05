# Copyright 2017 Tecnativa - Pedro M. Baeza
# Copyright 2020 ForgeFlow <http://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade
from openupgradelib.openupgrade_merge_records import merge_records


def merge_config_settings(env):
    env.cr.execute("""
        SELECT id, model
        FROM ir_model
        WHERE model LIKE '%.config.settings' AND transient
            AND model != 'res.config.settings'""")
    list_models = {x[0]: x[1] for x in env.cr.fetchall()}
    if list_models:
        env.cr.execute("""
            SELECT id FROM ir_model
            WHERE model = 'res.config.settings'""")
        setts_id = env.cr.fetchone()[0]
        for model_id, model_name in list_models.items():
            _update_referenced_data(
                env, [(model_id, setts_id)], model_name, 'res.config.settings')


def _update_referenced_data(env, ids_map, old_model, new_model):
    # helper to check for custom modules:
    # select f.id, f.model, f.name, f.ttype, f.relation, sc.table_name
    # from ir_model_fields f
    # join ir_model m ON f.relation = m.model
    # join information_schema.columns sc ON (
    #     sc.column_name = f.name AND sc.table_name=replace(f.model, '.', '_'))
    # where f.relation = 'ir.model' and not m.transient order by f.model;

    rename_all = [
        # ('calendar_event', 'res_model', 'res_model_id'),
        ('ir_act_server', 'model_name', 'model_id'),
        ('ir_model_fields', 'model', 'model_id'),
        # ('ir_model_fields_anonymization', 'model_name', 'model_id'),
        # ('mail_template', 'model', 'model_id'),
        # ('mail_mass_mailing', 'mailing_model_name', 'mailing_model_id'),
        # ('rating_rating', 'res_model', 'res_model_id'),
        # ('rating_rating', 'parent_res_model', 'parent_res_model_id'),
    ]
    rename_model_id = [
        # ('fetchmail_server', 'object_id'),
        # ('gamification_goal_definition', 'model_id'),
        # ('google_drive_config', 'model_id'),
        ('ir_act_server', 'crud_model_id'),
        # ('ir_actions', 'binding_model_id'),
        ('ir_model_access', 'model_id'),
        ('ir_model_constraint', 'model'),
        ('ir_model_relation', 'model'),
        ('ir_rule', 'model_id'),
        # ('mail_activity_type', 'res_model_id'),
        # ('mail_alias', 'alias_model_id'),
        # ('mail_alias', 'alias_parent_model_id'),
        # ('mail_template', 'sub_object'),
        # ('payment_transaction', 'callback_model_id'),
    ]
    rename_model_name = [
        ('ir_filters', 'model_id'),
        # ('ir_ui_view', 'model'),
    ]
    # the commented ones = improbable to appear *.config.settings model
    for (old_id, new_id) in ids_map:
        for rename in rename_all:
            openupgrade.logged_query(
                env.cr, """
                UPDATE {table}
                SET {field1} = '{new_value1}', {field2} = {new_value2}
                WHERE {field1} = '{old_value1}' AND {field2} = {old_value2}
                """.format(
                    table=rename[0], field1=rename[1], field2=rename[2],
                    old_value1=old_model, new_value1=new_model,
                    old_value2=old_id, new_value2=new_id,
                )
            )
        for rename in rename_model_id:
            openupgrade.logged_query(
                env.cr, """
                UPDATE {table}
                SET {field} = {new_value}
                WHERE {field} = {old_value}
                """.format(
                    table=rename[0], field=rename[1],
                    old_value=old_id, new_value=new_id,
                )
            )
        for rename in rename_model_name:
            openupgrade.logged_query(
                env.cr, """
                UPDATE {table}
                SET {field} = '{new_value}'
                WHERE {field} = '{old_value}'
                """.format(
                    table=rename[0], field=rename[1],
                    old_value=old_model, new_value=new_model,
                )
            )


@openupgrade.migrate()
def migrate(env, version):
    merge_config_settings(env)
    openupgrade.disable_invalid_filters(env)
