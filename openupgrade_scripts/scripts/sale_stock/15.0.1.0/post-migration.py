from openupgradelib import openupgrade


def date_to_datetime_fields(env):
    openupgrade.date_to_datetime_tz(
        env.cr,
        "sale_order",
        "create_uid",
        openupgrade.get_legacy_name("effective_date"),
        "effective_date",
    )


@openupgrade.migrate()
def migrate(env, version):
    date_to_datetime_fields(env)
