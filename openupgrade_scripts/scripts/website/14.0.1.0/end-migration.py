# Copyright 2023 Tecnativa - Pilar Vargas
from openupgradelib import openupgrade, openupgrade_140


def convert_field_html_string(env):
    exclusions = ["mail.message"]
    fields = env["ir.model.fields"].search(
        [("ttype", "=", "html"), ("store", "=", True)]
    )
    for field in fields:
        model = field.model_id.model
        if model in exclusions:
            continue
        if env.get(model, False) is not False and env[model]._auto:
            if openupgrade.table_exists(env.cr, env[model]._table):
                if field.name in env[model]._fields and openupgrade.column_exists(
                    env.cr, env[model]._table, field.name
                ):
                    openupgrade_140.convert_field_html_string_13to14(
                        env,
                        model,
                        field.name,
                    )


@openupgrade.migrate()
def migrate(env, version):
    convert_field_html_string(env)
