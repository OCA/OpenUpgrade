from openupgradelib import openupgrade

_xmlid_renames = [
    (
        "hr_contract.access_hr_contract_type_manager",
        "hr.access_hr_contract_type_manager",
    ),
]


def _hr_employee_fast_fill_work_contact_info(env):
    """
    First we create some column then
    if employee has user_id then set work_contact_id = user.partner_id
    then update mobile_phone, work_email from work_contact_id.mobile
    and work_contact_id.email for it
    """
    if not openupgrade.column_exists(env.cr, "hr_employee", "work_contact_id"):
        openupgrade.add_fields(
            env,
            [
                (
                    "work_contact_id",
                    "hr.employee",
                    "hr_employee",
                    "many2one",
                    False,
                    "hr",
                )
            ],
        )
    if not openupgrade.column_exists(env.cr, "hr_employee", "mobile_phone"):
        openupgrade.add_fields(
            env,
            [
                (
                    "mobile_phone",
                    "hr.employee",
                    "hr_employee",
                    "char",
                    False,
                    "hr",
                ),
            ],
        )
    if not openupgrade.column_exists(env.cr, "hr_employee", "work_email"):
        openupgrade.add_fields(
            env,
            [
                (
                    "work_email",
                    "hr.employee",
                    "hr_employee",
                    "char",
                    False,
                    "hr",
                ),
            ],
        )
    # Start filling for work_contact_id
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE hr_employee he
           SET work_contact_id = ru.partner_id
        FROM res_users ru
        WHERE ru.id = he.user_id AND he.user_id IS NOT NULL
        """,
    )
    # Start filling for mobile_phone
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE hr_employee he
           SET mobile_phone = rp.mobile
        FROM res_partner rp
        WHERE rp.id = he.work_contact_id AND he.work_contact_id IS NOT NULL
        """,
    )
    # Start filling for work_email
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE hr_employee he
           SET work_email = rp.email
        FROM res_partner rp
        WHERE rp.id = he.work_contact_id AND he.work_contact_id IS NOT NULL
        """,
    )


def _hr_plan_fast_fill_company_id(env):
    if not openupgrade.column_exists(env.cr, "hr_plan", "company_id"):
        openupgrade.add_fields(
            env,
            [
                (
                    "company_id",
                    "hr.plan",
                    "hr_plan",
                    "many2one",
                    False,
                    "hr",
                )
            ],
        )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE hr_plan hp
           SET company_id = ru.company_id
        FROM res_users ru
        WHERE ru.id = hp.create_uid
        """,
    )


def _hr_plan_activity_type_fast_fill_company_id(env):
    if not openupgrade.column_exists(env.cr, "hr_plan_activity_type", "company_id"):
        openupgrade.add_fields(
            env,
            [
                (
                    "company_id",
                    "hr.plan.activity.type",
                    "hr_plan_activity_type",
                    "many2one",
                    False,
                    "hr",
                )
            ],
        )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE hr_plan_activity_type hpat
           SET company_id = ru.company_id
        FROM res_users ru
        WHERE ru.id = hpat.create_uid
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_xmlids(env.cr, _xmlid_renames)
    _hr_employee_fast_fill_work_contact_info(env)
    _hr_plan_fast_fill_company_id(env)
    _hr_plan_activity_type_fast_fill_company_id(env)
