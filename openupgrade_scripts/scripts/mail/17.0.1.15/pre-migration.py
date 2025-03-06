# Copyright 2024 Viindoo Technology Joint Stock Company (Viindoo)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade

_models_renames = [
    ("mail.channel", "discuss.channel"),
    ("mail.channel.member", "discuss.channel.member"),
    ("mail.channel.rtc.session", "discuss.channel.rtc.session"),
]
_tables_renames = [
    ("mail_channel", "discuss_channel"),
    ("mail_channel_member", "discuss_channel_member"),
    ("mail_channel_rtc_session", "discuss_channel_rtc_session"),
    ("mail_channel_res_groups_rel", "discuss_channel_res_groups_rel"),
]
_fields_renames = [
    (
        "mail.tracking.value",
        "mail_tracking_value",
        "field",
        "field_id",
    ),
]
_columns_renames = {
    "discuss_channel_res_groups_rel": [
        ("mail_channel_id", "discuss_channel_id"),
    ],
}
_columns_copies = {
    "mail_template": [
        ("report_template", None, None),
    ],
}


def _mail_alias_fill_multiple_values(env):
    """
    We will fill value for alias_full_name in post because alias_domain has not been
    present yet
    """
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE mail_alias
        ADD COLUMN IF NOT EXISTS alias_full_name VARCHAR,
        ADD COLUMN IF NOT EXISTS alias_incoming_local BOOLEAN,
        ADD COLUMN IF NOT EXISTS alias_status VARCHAR;
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE mail_alias
        SET
        alias_incoming_local = True,
        alias_status = 'valid'
        """,
    )


def _mail_tracking_value_update_monetary_tracking_values(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE mail_tracking_value
            SET old_value_float = old_value_monetary,
                new_value_float = new_value_monetary
        WHERE old_value_monetary IS NOT NULL
            OR new_value_monetary IS NOT NULL;
        """,
    )


def _mail_gateway_allowed(env):
    """Set some dummy value so that the not null constraint can be created"""
    env.cr.execute(
        """
        UPDATE mail_gateway_allowed SET email='admin@example.com'
        WHERE email IS NULL
        """
    )


def _company_update_email_colors(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE res_company
        ADD COLUMN IF NOT EXISTS email_primary_color VARCHAR,
        ADD COLUMN IF NOT EXISTS email_secondary_color VARCHAR;
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE res_company
        SET email_primary_color = CASE
            WHEN primary_color IS NOT NULL then primary_color
            ELSE '#000000'
        END,
            email_secondary_color = CASE
            WHEN secondary_color IS NOT NULL then secondary_color
            ELSE '#875A7B'
        END
        """,
    )


def _mail_activity_plan(env):
    """If the OCA mail_activity_plan module is installed, we convert the existing data
    to adapt them to the standard.
    """
    if not openupgrade.table_exists(env.cr, "mail_activity_plan"):
        return
    _mail_activity_plan_fields_renames = [
        (
            "mail.activity.plan",
            "mail_activity_plan",
            "model",
            "res_model",
        ),
        (
            "mail.activity.plan",
            "mail_activity_plan",
            "model_id",
            "res_model_id",
        ),
    ]
    openupgrade.rename_fields(env, _mail_activity_plan_fields_renames)
    openupgrade.remove_tables_fks(
        env.cr,
        [
            "mail_activity_plan_activity_type",
            "mail_activity_plan_mail_activity_plan_activity_type_rel",
        ],
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_models(env.cr, _models_renames)
    openupgrade.rename_tables(env.cr, _tables_renames)
    openupgrade.rename_fields(env, _fields_renames)
    openupgrade.rename_columns(env.cr, _columns_renames)
    openupgrade.copy_columns(env.cr, _columns_copies)
    _mail_alias_fill_multiple_values(env)
    _mail_tracking_value_update_monetary_tracking_values(env)
    _company_update_email_colors(env)
    _mail_gateway_allowed(env)
    _mail_activity_plan(env)
    # create column to avoid model mail.alias is loaded before model res.company
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE res_company
        ADD COLUMN IF NOT EXISTS alias_domain_id INTEGER;
        """,
    )
