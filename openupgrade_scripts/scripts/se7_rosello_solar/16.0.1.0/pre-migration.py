from openupgradelib import openupgrade

_fields_renames = [
    (
        "crm.lead",
        "crm_lead",
        "bidders",
        "bidder_ids",
    )
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_fields(env, _fields_renames)
