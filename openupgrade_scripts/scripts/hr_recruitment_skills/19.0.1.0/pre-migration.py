from openupgradelib import openupgrade

_renamed_models = [
    ("hr.candidate.skill", "hr.applicant.skill"),
]

_renamed_tables = [
    ("hr_candidate_skill", "hr_applicant_skill"),
    ("hr_candidate_hr_skill_rel", "hr_applicant_hr_skill_rel"),
]

_renamed_fields = [
    ("hr.applicant.skill", "hr_applicant_skill", "candidate_id", "applicant_id"),
]

_renamed_columns = {
    "hr_applicant_hr_skill_rel": [("hr_candidate_id", "hr_applicant_id")],
}


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_models(env.cr, _renamed_models)
    openupgrade.rename_tables(env.cr, _renamed_tables)
    openupgrade.rename_fields(env, _renamed_fields)
    openupgrade.rename_columns(env.cr, _renamed_columns)
