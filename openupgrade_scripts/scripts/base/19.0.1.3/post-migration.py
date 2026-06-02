# Copyright 2025 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade

from odoo.fields import Command


def _ir_actions_act_window_target(env):
    """
    selection value 'inline' was removed, map to 'current'
    """
    openupgrade.logged_query(
        env.cr,
        "UPDATE ir_act_window SET target='current' WHERE target='inline'",
    )


def _ir_actions_server_child_ids(env):
    """
    Field was changed from m2m to o2m - set parent_id from m2m table,
    duplicate child actions that had multiple parents
    """
    env.cr.execute(
        """
        SELECT action_id, array_agg(server_id)
        FROM rel_server_actions GROUP BY action_id
        """
    )
    for action_id, parent_ids in env.cr.fetchall():
        action = env["ir.actions.server"].browse(action_id)
        parents = env["ir.actions.server"].browse(parent_ids)
        action.parent_id = parents[0]
        for parent in parents[1:]:
            action.copy({"name": action.name, "parent_id": parent.id})


def _ir_actions_server_html_value(env):
    """
    For evaluation_type 'value' and update_field_id.ttype == 'html',
    new field html_value is used
    """
    for action in env["ir.actions.server"].search(
        [
            ("state", "=", "object_write"),
            ("evaluation_type", "=", "value"),
            ("update_field_id.ttype", "=", "html"),
        ]
    ):
        action.write({"html_value": action.value})


def _ir_filters_user_ids(env):
    """
    m2o user_id has been transformed to m2m user_ids
    """
    openupgrade.m2o_to_x2m(
        env.cr, env["ir.filters"], env["ir.filters"]._table, "user_ids", "user_id"
    )


def _res_lang(env):
    """
    Char fields date_format, grouping and time_format have been dumbed down to
    selection fields. Keep their original value in a legacy column, and map existing
    values not in the selection to the default value
    """
    ResLang = env["res.lang"]
    for field_name in ("date_format", "time_format", "grouping"):
        field = ResLang._fields[field_name]
        openupgrade.copy_columns(env.cr, {"res_lang": [(field_name, None, None)]})
        openupgrade.logged_query(
            env.cr,
            f"UPDATE res_lang SET {field_name}=%(default)s "
            f"WHERE {field_name} NOT IN %(selection)s",
            {
                "default": field.default(ResLang),
                "selection": tuple(
                    value for value, _string in field._description_selection(env)
                ),
            },
        )


def _init_default_user_group(env):
    """
    Assign all groups of default_user to implied_ids of default_user_group
    """
    default_user = env.ref("base.default_user", raise_if_not_found=False)
    if not default_user:
        return
    env.ref("base.default_user_group").write(
        {
            "implied_ids": [Command.set(default_user.group_ids.ids)],
        }
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(
        env,
        "base",
        "19.0.1.3/noupdate_changes.xml",
        xml_transformation_filename="19.0.1.3/noupdate_changes-transformation.xml",
    )
    _init_default_user_group(env)
    openupgrade.delete_records_safely_by_xml_id(
        env,
        ["base.ir_filters_delete_own_rule", "base.default_user"],
    )
    _ir_actions_act_window_target(env)
    _ir_actions_server_child_ids(env)
    _ir_actions_server_html_value(env)
    _ir_filters_user_ids(env)
    _res_lang(env)
