from openupgradelib import openupgrade


def set_type(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE barcode_rule
        SET type = 'pack_date'
        WHERE type = 'packaging_date'
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    set_type(env)
