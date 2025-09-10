from openupgradelib import openupgrade

_models_renames = [
    (
        "ir.database",
        "database.database"
    ),
    (
        "ir.database.module",
        "database.module"
    ),
    (
        "ir.database.user",
        "database.user"
    ),
    (
        "ir.server",
        "database.server"
    )
]
_tables_renames = [

(
        "ir_database",
        "database_database"
    ),
    (
        "ir_database_module",
        "database_module"
    ),
    (
        "ir_database_user",
        "database_user"
    ),
    (
        "ir_server",
        "database_server"
    )


]

_fields_renames = [
    (
        "ir.server",
        "ir_server",
        "ip",
        "host",
    ),
    (
        "ir.server",
        "ir_server",
        "port",
        "secure_port",
    ),
    (
        "ir.server",
        "ir_server",
        "insecure_port",
        "port",
    ),
    (
        "ir.database",
        "ir_database",
        "login_user",
        "database_user_id",
    )
]




@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_fields(env, _fields_renames)
    openupgrade.rename_models(env.cr, _models_renames)
    openupgrade.rename_tables(env.cr, _tables_renames)

