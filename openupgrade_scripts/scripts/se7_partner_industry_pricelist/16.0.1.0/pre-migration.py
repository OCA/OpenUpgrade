from openupgradelib import openupgrade

_fields_renames = [
    (
        "res.partner.industry",
        "res_partner_industry",
        "pricelist",
        "pricelist_id",
    ),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_fields(env, _fields_renames)
