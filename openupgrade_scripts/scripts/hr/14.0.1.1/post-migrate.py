# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def fill_hr_employee_company_id(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE hr_employee he
        SET company_id = COALESCE(hd.company_id, ru.company_id)
        FROM hr_employee he2
        JOIN res_users ru ON ru.id = COALESCE(he2.create_uid, 1)
        LEFT JOIN hr_department hd ON hd.id = he2.department_id
        WHERE he.id = he2.id AND he.company_id is NULL
        """,
    )


def update_new_private_admin_partner(env):
    private_partner = env.ref("hr.res_partner_admin_private_address")
    public_partner = env.ref("hr.employee_admin").address_home_id
    private_partner.update(
        {
            "name": public_partner.name,
            "company_id": public_partner.company_id,
            "email": public_partner.email,
            "image_1920": public_partner.image_1920,
        }
    )


@openupgrade.migrate()
def migrate(env, version):
    fill_hr_employee_company_id(env)
    update_new_private_admin_partner(env)
    openupgrade.load_data(env.cr, "hr", "14.0.1.1/noupdate_changes.xml")
    openupgrade.delete_record_translations(
        env.cr, "hr", ["mail_template_data_unknown_employee_email_address"]
    )
    openupgrade.delete_records_safely_by_xml_id(
        env, ["hr.mail_template_data_unknown_employee_email_address"]
    )
