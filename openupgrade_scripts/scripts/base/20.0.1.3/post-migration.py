# Copyright 2026 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


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
    openupgrade.map_values(
        env.cr,
        openupgrade.get_legacy_name("tz"),
        "tz",
        table="res_partner",
        mapping=[
            ("Europe/Kiev", "Europe/Kyiv"),
            ("Portugal", "Europe/Lisbon"),
            ("Poland", "Europe/Warsaw"),
        ],
    )


def res_partner_bank(env):
    """
    Fill new res.partner.bank from res.bank, set company_id from partner
    """
    env.cr.execute(
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
        """
    )


def res_country(env):
    """
    Set zip_applicability=optional where it was not required
    """
    env.cr.execute(
        """
        UPDATE
            res_country
        SET
            zip_applicability='optional'
        WHERE
            NOT zip_required
        """
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


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(
        env,
        "base",
        "20.0.1.3/noupdate_changes.xml",
    )
    openupgrade.delete_records_safely_by_xml_id(
        env,
        [],
    )
    res_partner_tz(env)
    ir_model_fields_index(env)
    res_partner_bank(env)
    res_country(env)
    res_partner(env)
    res_groups(env)
