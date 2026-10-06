# Copyright 2026 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from collections import namedtuple

from openupgradelib import openupgrade


def ir_access(env):  # noqa: C901
    """
    Create ir.access records for manually created ir.model.access and ir.rule records

    This needs evaluating all pre-migration access rules in order to not create too wide
    permissions for ir.model.access records with accompanying ir.rules and not too
    narrow ones for ir.model.access records without for some group(s)
    """
    IrModel = env["ir.model"]
    ResGroups = env["res.groups"]
    AccessTuple = namedtuple("AccessTuple", ("group", "model", "operation"))
    accesstuple2domains = {}
    accesstuples_all = set()
    accesstuples_manual = set()
    EMPTY_DOMAIN = object()

    operation_field_mapping = {
        "c": "perm_create",
        "r": "perm_read",
        "u": "perm_write",
        "d": "perm_unlink",
    }

    def custom_record(column, model):
        return f"""
        {column} NOT IN (
            SELECT res_id
            FROM ir_model_data
            WHERE model='{model}'
            AND module NOT IN (
                '__export__', '__custom__'
            )
        )
        """

    env.cr.execute(
        f"""
        SELECT
            perm_create, perm_read, perm_write, perm_unlink, model_id, group_id,
            NOT {custom_record("id", "ir.model.access")} AS has_xmlid
        FROM
            ir_model_access
        WHERE
            active
        """
    )
    for row in env.cr.dictfetchall():
        for operation, field_name in operation_field_mapping.items():
            if not row[field_name]:
                continue
            group = ResGroups.browse(row["group_id"])
            model = IrModel.browse(row["model_id"])
            accesstuple = AccessTuple(group, model, operation)
            accesstuples_all.add(accesstuple)
            if not row["has_xmlid"]:
                accesstuples_manual.add(accesstuple)
            for implied_by_group in group.all_implied_by_ids or [group]:
                key = AccessTuple(implied_by_group, model, operation)
                accesstuple2domains[key] = {EMPTY_DOMAIN}

    env.cr.execute(
        f"""
        SELECT
            perm_create, perm_read, perm_write, perm_unlink, domain_force, model_id,
            group_id
        FROM
            ir_rule
        LEFT JOIN
            rule_group_rel
        ON
            rule_group_rel.rule_group_id=ir_rule.id
        WHERE
            ir_rule.active
        AND (
            perm_create OR
            perm_read OR
            perm_write OR
            perm_unlink
        )
        AND
            {custom_record("ir_rule.id", "ir.rule")}
        """
    )

    for row in env.cr.dictfetchall():
        for operation, field_name in operation_field_mapping.items():
            if not row[field_name]:
                continue
            key = AccessTuple(
                ResGroups.browse(row["group_id"]),
                IrModel.browse(row["model_id"]),
                operation,
            )
            if key not in accesstuple2domains:
                global_key = (ResGroups,) + key[1:]
                if global_key in accesstuples_all:
                    accesstuple2domains[key] = set()
                elif not key.group:
                    if any(
                        accesstuple.model == key.model
                        and accesstuple.operation == key.operation
                        for accesstuple in accesstuples_all
                    ):
                        accesstuple2domains[key] = set()
                    else:
                        continue
                else:
                    continue
            accesstuple2domains[key].add(row["domain_force"])
            if EMPTY_DOMAIN in accesstuple2domains[key]:
                accesstuple2domains[key].remove(EMPTY_DOMAIN)

    for key in list(accesstuple2domains.keys()):
        if (
            accesstuple2domains[key] == {EMPTY_DOMAIN}
            and key not in accesstuples_manual
        ):
            accesstuple2domains.pop(key)
            continue

        for group in key.group.all_implied_ids - key.group:
            group_key = (group,) + key[1:]
            if group_key not in accesstuple2domains:
                continue
            for domain in accesstuple2domains[group_key]:
                if domain in accesstuple2domains[key]:
                    accesstuple2domains[key].remove(domain)

        if (
            accesstuple2domains[key] == {EMPTY_DOMAIN}
            and key not in accesstuples_manual
        ):
            accesstuple2domains.pop(key)

    DomainTuple = namedtuple("DomainTuple", ["group", "model", "domain"])
    domaintuple2operation = {}

    for accesstuple, domains in accesstuple2domains.items():
        for domain in domains:
            key = DomainTuple(accesstuple.group, accesstuple.model, domain)
            existing_operation = domaintuple2operation.get(key, "")
            domaintuple2operation[key] = "".join(
                o
                for o in operation_field_mapping
                if o == accesstuple.operation or o in existing_operation
            )

    IrAccess = env["ir.access"]
    # turn off validation as most models won't be available yet
    _validate_fields = IrAccess.__class__._validate_fields
    IrAccess.__class__._validate_fields = lambda *args: None
    IrAccess.create(
        [
            {
                "name": "Migrated from v19",
                "operation": operation,
                "group_id": domaintuple.group.id,
                "model_id": domaintuple.model.id,
                "domain": domaintuple.domain
                if domaintuple.domain != EMPTY_DOMAIN
                else None,
            }
            for domaintuple, operation in domaintuple2operation.items()
        ]
    )
    IrAccess.__class__._validate_fields = _validate_fields


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
        FROM
            ir_model
        WHERE
            ir_model_fields.model_id=ir_model.id
        AND
            ir_model.state='manual'
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
    ir_access(env)
    res_partner_tz(env)
    ir_model_fields_index(env)
    res_partner_bank(env)
    res_country(env)
    res_partner(env)
    res_groups(env)
