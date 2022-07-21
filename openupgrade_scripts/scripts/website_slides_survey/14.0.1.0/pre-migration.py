# Copyright 2022 ForgeFlow S.L.  <https://www.forgeflow.com>
from openupgradelib import openupgrade

_fields_rename = [
    (
        "slide.slide.partner",
        "slide_slide_partner",
        "survey_quizz_passed",
        "survey_scoring_success",
    )
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_fields(env, _fields_rename)
