from openupgradelib import openupgrade

_fields_renames = [
    (
        "account.move",
        "account_move",
        "fecha_vencimiento_pagare",
        "promissory_note_date_due",
    )
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_fields(env, _fields_renames)
