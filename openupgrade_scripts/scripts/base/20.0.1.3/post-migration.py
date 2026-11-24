# Copyright 2026 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade

from odoo.addons.base.models.ir_model import selection_xmlid


def ir_model_fields_index(env):
    """
    Fill index field for custom models
    """
    old_index_field = openupgrade.get_legacy_name("index")
    env.cr.execute(
        f"""
        UPDATE
            ir_model_fields
        SET
            index=CASE WHEN {old_index_field} THEN 'btree' ELSE NULL END
        WHERE
            state='manual'
        """
    )


def res_partner_tz(env):
    """
    Selection source has been changed from pytz.all_timezones (v19) to
    zoneinfo.available_timezones() restricted by babel.dates.get_timezone (v20)

    Map removed values to their most sensible candidate
    """
    openupgrade.copy_columns(
        env.cr,
        {
            "res_partner": [
                ("tz", None, None),
            ],
        },
    )
    mapped_values = [
        ("Europe/Kiev", "Europe/Kyiv"),
        ("Portugal", "Europe/Lisbon"),
        ("Poland", "Europe/Warsaw"),
    ]
    openupgrade.map_values(
        env.cr,
        openupgrade.get_legacy_name("tz"),
        "tz",
        table="res_partner",
        mapping=mapped_values,
    )
    openupgrade.rename_xmlids(
        env.cr,
        [
            (
                selection_xmlid("base", "res.partner", "tz", old_value),
                selection_xmlid("base", "res.partner", "tz", new_value),
            )
            for old_value, new_value in mapped_values
        ],
        allow_merge=True,
    )


def res_partner_bank(env):
    """
    Fill new res.partner.bank fields from res.bank, set company_id from partner,
    """
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE
            res_partner_bank
        SET
            bank_bic=res_bank.bic,
            city=res_bank.city,
            country_id=res_bank.country,
            bank_name=res_bank.name,
            state_id=res_bank.state,
            street=res_bank.street,
            street2=res_bank.street2,
            zip=res_bank.zip
        FROM
            res_bank
        WHERE
            bank_id=res_bank.id
        """,
    )


def res_partner(env):
    """
    Fill additional_identifiers from company_registry
    """
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE
            res_partner
        SET
            additional_identifiers=COALESCE(
                additional_identifiers, jsonb_build_object()
            ) || jsonb_build_object('OTHER', company_registry)
        WHERE
            company_registry IS NOT NULL
        """,
    )


def res_groups(env):
    """
    Add all members of group_user to group_user_regular
    """
    openupgrade.logged_query(
        env.cr,
        f"""
        INSERT INTO
            res_groups_users_rel
            (uid, gid)
        SELECT
            uid, {env.ref("base.group_user_regular").id}
        FROM
            res_groups_users_rel
        WHERE
            gid={env.ref("base.group_user").id}
        AND NOT EXISTS (
            SELECT uid FROM res_groups_users_rel res_groups_users_rel2
            WHERE gid={env.ref("base.group_system").id}
            AND uid=res_groups_users_rel.uid
        )
        """,
    )


def res_users_apikeys_scope(env):
    """
    Set scope rpc for apikeys with scope null
    """
    openupgrade.logged_query(
        env.cr, "UPDATE res_users_apikeys SET scope='rpc' WHERE scope IS NULL"
    )


def ir_config_parameter_default_max_email_size(env):
    """
    Preserve custom default_max_email_size or ir.mail_server#max_email_size,
    whichever is lowest. Set new default 20 otherwise
    """
    IrConfigParameter = env["ir.config_parameter"]
    key = "base.default_max_email_size"
    config_param_value = IrConfigParameter.get_float(key, 10)
    env.cr.execute(
        f"""
        SELECT
            MIN(
                CASE
                    WHEN max_email_size > 0 THEN max_email_size
                    ELSE {config_param_value}
                END
            )
        FROM
            ir_mail_server
        WHERE
            active
        """
    )
    least_value = 0
    for row in env.cr.fetchall():
        least_value = row[0]
    if least_value and least_value != 10:
        IrConfigParameter.set_float(key, least_value)
    else:
        IrConfigParameter.set_float(key, 20)


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(
        env,
        "base",
        "20.0.1.3/noupdate_changes.xml",
        xml_transformation_filename="20.0.1.3/noupdate_changes-transformation.xml",
    )
    openupgrade.delete_records_safely_by_xml_id(
        env,
        [],
    )
    res_partner_tz(env)
    ir_model_fields_index(env)
    res_partner_bank(env)
    res_partner(env)
    res_groups(env)
    res_users_apikeys_scope(env)
    ir_config_parameter_default_max_email_size(env)
