# Copyright 2024 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_xmlids_renames = [
    ("survey.survey_form", "survey.survey_survey_view_form"),
    ("survey.survey_kanban", "survey.survey_survey_view_kanban"),
    ("survey.survey_tree", "survey.survey_survey_view_tree"),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_xmlids(env.cr, _xmlids_renames)
