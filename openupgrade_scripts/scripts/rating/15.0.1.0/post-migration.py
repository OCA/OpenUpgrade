from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.map_values(
        env.cr,
        openupgrade.get_legacy_name("rating_text"),
        "rating_text",
        [
            ("satisfied", "top"),
            ("not satisfied", "ok"),
            ("highly_dissatisfied", "ko"),
            ("no_rating", "none"),
        ],
        table="rating_rating",
    )
