from openupgradelib import openupgrade

_fields_renames = [
    (
        "res.company",
        "res_company",
        "a3_codigo_empresa",
        "a3_company_code",
    ),
    (
        "account.account",
        "account_account",
        "code_a3",
        "a3_code",
    ),
    (
        "account.move",
        "account_move",
        "exported",
        "a3_exported",
    ),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_fields(env, _fields_renames)
