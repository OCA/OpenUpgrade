from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.m2o_to_x2m(
        env.cr,
        env["event.question"],
        "event_question",
        "event_ids",
        "event_id",
    )
    openupgrade.m2o_to_x2m(
        env.cr,
        env["event.question"],
        "event_question",
        "event_type_ids",
        "event_type_id",
    )
    openupgrade.load_data(env, "event", "19.0.1.9/noupdate_changes_work.xml")
