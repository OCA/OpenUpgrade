from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.copy_columns(
        env.cr,
        {"rating_rating": [("rating_text", None, None)]},
    )
    # Disappeared constraint
    openupgrade.delete_sql_constraint_safely(
        env, "rating", "rating_rating", "rating_range"
    )
