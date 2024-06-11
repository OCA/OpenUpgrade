import logging

from openupgradelib import openupgrade
from openupgradelib.openupgrade_160 import (
    _convert_field_bootstrap_4to5_sql,
    convert_field_bootstrap_4to5,
)

logger = logging.getLogger(__name__)


def convert_custom_qweb_templates_bootstrap_4to5(env):
    """Convert customized website views to Bootstrap 5."""
    backup_column = openupgrade.get_legacy_name("arch_db_bs4")
    openupgrade.logged_query(
        env.cr, f"ALTER TABLE ir_ui_view ADD COLUMN {backup_column} TEXT"
    )
    openupgrade.logged_query(
        env.cr,
        f"""
        UPDATE ir_ui_view SET {backup_column} = arch_db
        WHERE type = 'qweb' AND website_id IS NOT NULL
        """,
    )
    # Find views to convert
    env.cr.execute(
        "SELECT id FROM ir_ui_view WHERE type = 'qweb' AND website_id IS NOT NULL"
    )
    view_ids = [x for x, *_ in env.cr.fetchall()]
    _convert_field_bootstrap_4to5_sql(env.cr, "ir_ui_view", "arch_db", ids=view_ids)


def convert_field_html_string_bootstrap_4to5(env):
    """Convert html field which might contain old bootstrap syntax"""
    # These models won't use bootstrap in their html fields
    model_exclusions = [
        "mail.activity",
        "mail.message",
        "mail.wizard.invite",
        "web_editor.converter.test",
        "mail.mail",
        "mail.template",
        "res.users",
        "mail.channel",
        "mailing.mailing",
        "account.invoice.send",
        "mail.alias",
    ]
    # We could want to refine a certain field logic to discard a good bunch of records
    field_special_domain = {
        "account.move": {
            "narration": [
                ("move_type", "in", ["out_invoice", "out_refund", "out_receipt"])
            ]
        },
    }
    fields = env["ir.model.fields"].search(
        [
            ("ttype", "=", "html"),
            ("store", "=", True),
            ("model", "not in", model_exclusions),
        ]
    )
    for field in fields:
        model = field.model_id.model
        # The method convert_field_bootstrap_4to5 takes care of empty fields considering
        domain = field_special_domain.get(model, {}).get(field.name, [])
        logger.info(f"Converting from BS4 to BS5 field {field.name} in model {model}")
        if env.get(model, False) is not False and env[model]._auto:
            if openupgrade.table_exists(env.cr, env[model]._table):
                if field.name in env[model]._fields and openupgrade.column_exists(
                    env.cr, env[model]._table, field.name
                ):
                    convert_field_bootstrap_4to5(env, model, field.name, domain=domain)


def rename_t_group_website_restricted_editor(env):
    """Locate group directives in custom views with the former `group_website_publisher`
    group which is now renamed to `group_website_restricted_editor`. For example, the
    website_partner.partner_detail template"""
    views = env["ir.ui.view"].search(
        [
            (
                "arch_db",
                "ilike",
                "website.group_website_publisher",
            ),
            ("website_id", "!=", False),
        ]
    )
    for view in views:
        view.arch_db = view.arch_db.replace(
            "website.group_website_publisher", "website.group_website_restricted_editor"
        )


@openupgrade.migrate()
def migrate(env, version):
    convert_custom_qweb_templates_bootstrap_4to5(env)
    convert_field_html_string_bootstrap_4to5(env)
    rename_t_group_website_restricted_editor(env)
