from openupgradelib import openupgrade

_field_renames = [
    ("res.users", "res_users", "google_cal_account_id", "google_calendar_account_id"),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_fields(env, _field_renames)
    openupgrade.delete_sql_constraint_safely(
        env, "google_calendar", "res_users", "google_token_uniq"
    )
