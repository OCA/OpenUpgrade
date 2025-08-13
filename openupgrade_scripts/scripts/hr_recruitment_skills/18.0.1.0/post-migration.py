# Copyright 2025 Tecnativa - Carlos Lopez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def _fill_hr_candidate_skill(env):
    # Create candidate skill records from applicant skill
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO hr_candidate_skill (
            candidate_id, skill_id, skill_level_id, skill_type_id,
            create_date, write_date, create_uid, write_uid
        )
        SELECT DISTINCT ON (candidate_id, skill_id)
            candidate_id,
            skill_id,
            skill_level_id,
            skill_type_id,
            create_date,
            write_date,
            create_uid,
            write_uid
        FROM (
            SELECT ha.candidate_id,
                has.skill_id,
                has.skill_level_id,
                has.skill_type_id,
                has.create_date,
                has.write_date,
                has.create_uid,
                has.write_uid,
                hsl.level_progress
            FROM hr_applicant_skill AS has
            JOIN hr_applicant AS ha ON ha.id = has.applicant_id
            JOIN hr_skill_level hsl ON hsl.id = has.skill_level_id
        ) tmp
        ORDER BY candidate_id, skill_id, level_progress DESC;
        """,
    )
    # fill many2many field skill_ids
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO hr_candidate_hr_skill_rel (
            hr_candidate_id, hr_skill_id
        )
        SELECT DISTINCT candidate_id, skill_id
        FROM hr_candidate_skill
        ON CONFLICT DO NOTHING
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env, "hr_recruitment_skills", "18.0.1.0/noupdate_changes.xml")
    _fill_hr_candidate_skill(env)
