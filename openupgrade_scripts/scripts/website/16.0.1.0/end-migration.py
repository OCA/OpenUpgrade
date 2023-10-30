from openupgradelib import openupgrade
from openupgradelib.openupgrade_160 import convert_string_bootstrap_4to5
from psycopg2.extras import Json


def boostrap_5_migration(env):
    """Convert customized website views to Bootstrap 5."""
    backup_column = openupgrade.get_legacy_name("arch_db_bs4")
    openupgrade.logged_query(
        env.cr, f"ALTER TABLE ir_ui_view ADD COLUMN {backup_column} TEXT"
    )
    # Find views to convert
    env.cr.execute(
        """
        SELECT iuv.id, iuv.arch_db
        FROM ir_ui_view iuv
        WHERE iuv.type = 'qweb'
        """
    )
    for id_, arch_db_ in env.cr.fetchall():
        if not arch_db_:
            continue
        new_arch = {
            lang: convert_string_bootstrap_4to5(arch_db)
            for lang, arch_db in arch_db_.items()
        }
        if new_arch != arch_db_:
            env.cr.execute(
                f"UPDATE ir_ui_view SET {backup_column} = arch_db WHERE id=%s",
                (id_,),
            )
            query = "UPDATE ir_ui_view SET arch_db = %s WHERE id = %s"
            env.cr.execute(env.cr.mogrify(query, [Json(new_arch), id_]).decode())


@openupgrade.migrate()
def migrate(env, version):
    boostrap_5_migration(env)
