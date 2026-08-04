# Copyright 2026 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade, openupgrade_tools

copy_columns = {
    "hr_candidate_skill": [
        ("candidate_id", None, None),
        ("create_date", "valid_from", "date"),
    ],
}

renamed_fields = [
    ("hr.applicant.skill", "hr_applicant_skill", "candidate_id", "applicant_id")
]

renamed_models = [
    ("hr.candidate.skill", "hr.applicant.skill"),
]

renamed_tables = [
    ("hr_candidate_skill", "hr_applicant_skill"),
]


def hr_applicant_skill(env):
    """
    Set hr.applicant.skill#applicant_id (renamed candidate_id) from hr_applicant
    """
    openupgrade.lift_constraints(env.cr, "hr_applicant_skill", "applicant_id")
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE hr_applicant_skill
        SET applicant_id=hr_applicant.id
        FROM hr_applicant
        WHERE hr_applicant.candidate_id=hr_applicant_skill.applicant_id
        """,
    )


def hr_applicant_skill_ids(env):
    """
    Pre-create and fill hr.applicant#skill_ids
    """
    openupgrade.logged_query(
        env.cr,
        """
        CREATE TABLE hr_applicant_hr_skill_rel (
            hr_applicant_id INTEGER NOT NULL,
            hr_skill_id INTEGER NOT NULL,
            PRIMARY KEY(hr_applicant_id, hr_skill_id)
        );
        COMMENT ON TABLE hr_applicant_hr_skill_rel IS
            'RELATION BETWEEN hr_applicant AND hr_skill';
        CREATE INDEX ON hr_applicant_hr_skill_rel
            (hr_skill_id, hr_applicant_id);
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO hr_applicant_hr_skill_rel (hr_applicant_id, hr_skill_id)
        SELECT applicant_id, skill_id FROM hr_applicant_skill
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.copy_columns(env.cr, copy_columns)
    openupgrade.rename_models(env.cr, renamed_models)
    if openupgrade_tools.table_exists(env.cr, "hr_applicant_skill"):
        # if the database has been migrated from v17, this table can exist already
        renamed_tables[0:0] = [("hr_applicant_skill", None)]
    openupgrade.rename_tables(env.cr, renamed_tables)
    openupgrade.rename_fields(env, renamed_fields)
    hr_applicant_skill(env)
    hr_applicant_skill_ids(env)
