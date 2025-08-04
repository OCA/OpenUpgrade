from openupgradelib import openupgrade

columns_copy = {
    "hr_applicant": [
        ("name", None, None),
    ],
}

column_creates = [
    ("hr.applicant", "refuse_date", "datetime"),
]

field_renames = [
    ("hr.applicant", "hr_applicant", "description", "applicant_notes"),
]

xmlid_renames = [
    (
        "hr_recruitment.applicant_hired_template",
        "hr_recruitment.candidate_hired_template",
    ),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.copy_columns(env.cr, columns_copy)
    openupgrade.add_columns(env, column_creates)
    openupgrade.rename_fields(env, field_renames)
    openupgrade.rename_xmlids(env.cr, xmlid_renames)
    openupgrade.rename_xmlids(
        env.cr,
        [
            ("hr_recruitment.refuse_reason_3", "hr_recruitment.refuse_reason_2"),
            ("hr_recruitment.refuse_reason_4", "hr_recruitment.refuse_reason_2"),
        ],
        allow_merge=True,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE hr_applicant
        SET refuse_date = write_date
        WHERE refuse_reason_id IS NOT NULL
        """,
    )
