from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.logged_query(
        env.cr,
        """
        DELETE FROM event_stage WHERE id IN (
            SELECT imd.res_id FROM ir_model_data imd
            WHERE imd.model = 'event.stage'
              AND imd.module = 'event'
              AND imd.name = 'event_stage_cancelled'
        )
        """,
    )
