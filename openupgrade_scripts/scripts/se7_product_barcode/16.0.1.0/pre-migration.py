from openupgradelib import openupgrade

_fields_renames = [
    (
        "res.company",
        "res_company",
        "internalbarcodeprefix",
        "internal_barcode_prefix",
    ),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_fields(env, _fields_renames)
