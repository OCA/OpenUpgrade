from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.logged_query(
        env.cr,
        """
            UPDATE barcode_rule
            SET type = 'pack_date'
            WHERE type = 'packaging_date'
        """,
    )
