import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


def _m2m_to_o2m_plan_activity_type_ids(env):
    """
    The field 'plan_activity_type_ids' has changed
    from m2m to o2m, so we need to check the rel table (m2m table)
    between them then fill value for 'plan_id' at hr.plan.activity.type
    and after that ORM will do the rest for us
    """
    openupgrade.logged_query(
        env.cr,
        """
        WITH tmp AS(
            SELECT hp.id as hr_plan_id, hpat.id as hr_plan_activity_type_id
              FROM hr_plan hp JOIN hr_plan_hr_plan_activity_type_rel rel
            ON hp.id = rel.hr_plan_id JOIN hr_plan_activity_type hpat
            ON hpat.id = rel.hr_plan_activity_type_id
        )
        UPDATE hr_plan_activity_type hpat
           SET plan_id = tmp.hr_plan_id
        FROM tmp
        WHERE hpat.id = tmp.hr_plan_activity_type_id
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env.cr, "hr", "16.0.1.1/noupdate_changes.xml")
    _m2m_to_o2m_plan_activity_type_ids(env)
