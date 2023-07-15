from openupgradelib import openupgrade


def create_sequence(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE event_track_location
        ADD COLUMN IF NOT EXISTS sequence integer
        """,
    )

    openupgrade.logged_query(
        env.cr,
        """
        UPDATE event_track_location
        SET sequence = 10
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    create_sequence(env)
