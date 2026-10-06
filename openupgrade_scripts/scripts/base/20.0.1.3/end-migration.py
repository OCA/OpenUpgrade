# Copyright 2026 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from collections import namedtuple

from markupsafe import Markup
from openupgradelib import openupgrade


class SetOfDomainWithOrigin(dict):
    """
    Store domains for some permission/restriction with the ir.model.access id that
    enables the operation
    """

    def __init__(self, origin):
        self.origin = origin

    def add(self, domain, origin):
        if domain in self:
            self[domain].add(origin)
        else:
            self[domain] = {origin}


AccessTuple = namedtuple("AccessTuple", ("group", "model", "operation"))


def _ir_access_get_v19_permissions(env):
    """
    Return custom permission domains per operation as seen in v19.

    Only consider custom records, not changed module records as we don't know their
    original value at this point.
    """
    IrModel = env["ir.model"]
    ResGroups = env["res.groups"]
    accesstuple2domains = {}
    accesstuples_manual = set()

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
                '__export__', '__custom__', 'studio_customization'
            )
        )
        """

    env.cr.execute(
        f"""
        SELECT
            name, perm_create, perm_read, perm_write, perm_unlink, model_id, group_id,
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
            if not row["has_xmlid"]:
                accesstuples_manual.add(accesstuple)
            for implied_by_group in group.all_implied_by_ids or [group]:
                key = AccessTuple(implied_by_group, model, operation)
                accesstuple2domains[key] = SetOfDomainWithOrigin(row["name"])

    env.cr.execute(
        f"""
        SELECT
            COALESCE(name, 'ir.rule,'||id) name, perm_create, perm_read, perm_write,
            perm_unlink, domain_force, model_id, group_id
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
            # in general, don't consider domains for operations that aren't allowed
            if key not in accesstuple2domains:
                global_key = (ResGroups,) + key[1:]
                if global_key in accesstuple2domains:
                    # but if there's a blanket permission, consider the domain
                    accesstuple2domains[key] = SetOfDomainWithOrigin(
                        accesstuple2domains[global_key].origin
                    )
                elif not key.group:
                    for accesstuple, domains in accesstuple2domains.items():
                        if (
                            accesstuple.model == key.model
                            and accesstuple.operation == key.operation
                        ):
                            # also consider domains of restrictions if there are
                            # permissions for it
                            accesstuple2domains[key] = SetOfDomainWithOrigin(
                                domains.origin
                            )
                            break
                    else:
                        continue
                else:
                    continue
            accesstuple2domains[key].add(row["domain_force"], row["name"])

    return accesstuples_manual, accesstuple2domains


def _ir_access_postprocess_accesstuple2domains(
    env, accesstuples_manual, accesstuple2domains
):
    """
    Reduce accesstuple2domains to keep minimal group/domain assignments per operation,
    and remove global permissions that haven't been manually added by the user
    """
    v19_keys = set(accesstuple2domains)
    for key in list(accesstuple2domains.keys()):
        if not accesstuple2domains[key] and key not in accesstuples_manual:
            accesstuple2domains.pop(key)
            continue

        # as _ir_access_get_v19_permissions has expanded all groups, move domains up
        # the group inheritance tree to get the minimal set of permissions to add
        for group in key.group.all_implied_ids - key.group:
            group_key = (group,) + key[1:]
            if group_key not in accesstuple2domains:
                continue
            for domain in accesstuple2domains[group_key]:
                accesstuple2domains[key].pop(domain, False)

        if not accesstuple2domains[key]:
            # keep empty (=allow all) permissions only if they were added manually
            if key in accesstuples_manual:
                # set group_everyone for former ir.model.access records without group
                # if no other v19 access or rule applies to this model and operation
                if not key.group and not any(
                    model_key
                    for model_key in v19_keys
                    if model_key.model == key.model
                    and model_key.operation == key.operation
                    and model_key != key
                ):
                    group_everyone = env.ref("base.group_everyone")
                    accesstuple2domains[AccessTuple(*((group_everyone,) + key[1:]))] = (
                        accesstuple2domains.pop(key)
                    )
            else:
                accesstuple2domains.pop(key)


def ir_access(env):
    """
    Create ir.access records for manually created ir.model.access and ir.rule records

    This needs evaluating all pre-migration access rules in order to not create too wide
    permissions for ir.model.access records with accompanying ir.rules and not too
    narrow ones for ir.model.access records without for some group(s).

    Do not consider interactions between v19 provisioned rules and custom rules, as the
    goal here is to just migrate the custom v19 rules, not to restore the exact
    permissions existing in v19.
    """
    accesstuples_manual, accesstuple2domains = _ir_access_get_v19_permissions(env)
    _ir_access_postprocess_accesstuple2domains(
        env, accesstuples_manual, accesstuple2domains
    )

    DomainTuple = namedtuple("DomainTuple", ["group", "model", "domain"])
    domaintuple2operation = {}

    for accesstuple, domains in accesstuple2domains.items():
        for domain in domains or [None]:
            key = DomainTuple(accesstuple.group, accesstuple.model, domain)
            existing_operation = domaintuple2operation.get(key, "")
            domaintuple2operation[key] = "".join(
                o
                for o in "crud"
                if o == accesstuple.operation or o in existing_operation
            )

    IrAccess = env["ir.access"]

    custom_access_active = IrAccess.browse()
    custom_access_inactive = IrAccess.browse()

    for domaintuple, operation in domaintuple2operation.items():
        origins = set()
        for operation_char in operation:
            accesstuple = (domaintuple.group, domaintuple.model, operation_char)
            origins.add(accesstuple2domains[accesstuple].origin)
            origins |= accesstuple2domains[accesstuple].get(domaintuple.domain, set())
        vals = {
            "name": f"Migrated from v19 ({', '.join(origins)})",
            "operation": operation,
            "group_id": domaintuple.group.id,
            "model_id": domaintuple.model.id,
            "domain": domaintuple.domain,
        }

        try:
            with env.cr.savepoint():
                custom_access_active += IrAccess.create(vals)
        except Exception as e:  # noqa: BLE001
            openupgrade.message(
                env.cr,
                "base",
                None,
                None,
                "Creating inactive rule for %s[%s]: %s because it fails with %s",
                domaintuple.model.model,
                operation,
                domaintuple.domain,
                e,
            )
            custom_access_inactive += IrAccess.create(dict(vals, active=False, note=e))

    admin_channel = "discuss.channel" in env and env.ref(
        "mail.channel_admin", raise_if_not_found=False
    )

    if (custom_access_active or custom_access_inactive) and admin_channel:
        model_list = ""
        for access_model in (custom_access_active + custom_access_inactive).model_id:
            model_list += (
                f'<li><a href="/odoo/ir.model/{access_model.id}">'
                f"{access_model.name}</a></li>"
            )
        inactive_access_list = ""
        for access in custom_access_inactive:
            inactive_access_list += (
                f'<li><a href="/odoo/ir.access/{access.id}">{access.name}</a></li>'
            )
        admin_channel.message_post(
            body=Markup(
                """
            <div class="alert alert-warning">Custom record rules and model access</div>
            <p>You have customized your model access rules.
            Note the v19 approach does not map exactly to v20, so you need to
            review and test carefully that the migrated access records for the
            following models do what you expect.</p>
            <p>Be especially cautious with group based restrictions, those will
            most likely not work the way they used to.</p>
            <p>Also ir.model.access records without a group work as restrictions in v20.
            If you really want to grant everyone some access, you'll have to set group
            <em>Everyone</em> there. The migration only did this for models that do not
            have access restrictions set in v19.</p>
            """
                + (
                    f"""
                <p>Models with custom access:</p>
                <ul>{model_list}</ul>
                """
                    if model_list
                    else ""
                )
                + (
                    f"""
                <p>Some migrated custom access records could not be activated, those
                have been created as inactive. Review the exception in the notes field
                and fix them accordingly before activating:
                </p>
                <ul>{inactive_access_list}</ul>
                """
                    if inactive_access_list
                    else ""
                )
            ),
            message_type="comment",
        )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.disable_invalid_filters(env)
    ir_access(env)
