# Copyright 2024 Viindoo Technology Joint Stock Company (Viindoo)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def _ir_act_server_update_name_if_base_automation(env):
    act_servers = (
        env["ir.actions.server"]
        .with_context(active_test=False)
        .search([("base_automation_id", "!=", False)])
    )
    if act_servers:
        act_servers._compute_name()


def _base_automation_update_trigger_fields_ids_if_null(env):
    """
    Need to update the trigger_fields_ids if Null for 'on_create_or_write'
    or else we will get weird error
    Also this is base on hint from
    https://github.com/odoo/odoo/pull/114352#issuecomment-1836948745
    """
    base_automations = (
        env["base.automation"]
        .with_context(active_test=False)
        .search(
            [
                ("trigger", "=", "on_create"),
                ("trigger_field_ids", "=", False),
            ]
        )
    )
    if base_automations:
        create_date_fields = env["ir.model.fields"].search(
            [
                ("model_id", "in", tuple(base_automations.model_id.ids)),
                ("name", "=", "create_date"),
            ]
        )
        for automation in base_automations:
            create_date_field = create_date_fields.filtered(
                lambda field, automation=automation: field.model_id
                == automation.model_id
            )[:1]
            if create_date_field:
                automation.trigger_field_ids = [(4, create_date_field.id)]


def _ir_ui_view_remove_inherit_id_from_automation_form(env):
    """
    Somehow this inherit_id from ir.actions.server of 'view_base_automation_form'
    won't disappear so we need to remove it from here
    """
    view = env.ref(
        "base_automation.view_base_automation_form", raise_if_not_found=False
    )
    if view and view.inherit_id:
        view.inherit_id = False


def _base_automation_update_deprecate_trigger(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE base_automation
            SET trigger = 'on_create_or_write'
        WHERE trigger IN ('on_create', 'on_write')
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env, "base_automation", "17.0.1.0/noupdate_changes.xml")
    _ir_act_server_update_name_if_base_automation(env)
    _base_automation_update_trigger_fields_ids_if_null(env)
    # Need to update deprecated trigger after add trigger field for 'on_create' trigger
    _base_automation_update_deprecate_trigger(env)
    _ir_ui_view_remove_inherit_id_from_automation_form(env)
