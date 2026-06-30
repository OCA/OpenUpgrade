# Copyright 2026 Tecnativa - Carlos Lopez
# Copyright 2026 Tecnativa - Eduardo Ezerouali
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from openupgradelib import openupgrade


def _empty_lang_ids(env):
    openupgrade.logged_query(
        env.cr,
        "DELETE FROM res_lang_survey_survey_rel",
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env, "survey", "19.0.3.7/noupdate_changes.xml")
    _empty_lang_ids(env)
