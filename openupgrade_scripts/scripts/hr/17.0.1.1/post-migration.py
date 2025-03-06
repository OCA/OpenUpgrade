# Copyright 2024 Viindoo Technology Joint Stock Company (Viindoo)
# Copyright 2025 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

_deleted_xml_records = [
    "hr.dep_sales",
    "hr.hr_plan_activity_type_company_rule",
    "hr.hr_plan_company_rule",
    "hr.res_partner_admin_private_address",
]


def _transfer_employee_private_data(env):
    """On v17, there's no more private res.partner records, so we should transfer the
    information to the dedicated employee fields, and then anonymize the remaining data
    in the res.partner record.
    """
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE hr_employee he
        SET lang = rp.lang,
            private_city = rp.city,
            private_country_id = rp.country_id,
            private_email = rp.email,
            private_phone = rp.phone,
            private_state_id = rp.state_id,
            private_street = rp.street,
            private_street2 = rp.street2,
            private_zip = rp.zip
        FROM res_partner rp
        WHERE he.address_home_id = rp.id""",
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE res_partner rp
        SET city = '***',
            country_id = NULL,
            email = '***',
            phone = '***',
            state_id = NULL,
            street = '***',
            street2 = '***',
            zip = '***'
        FROM hr_employee he
        WHERE he.address_home_id = rp.id""",
    )


@openupgrade.migrate()
def migrate(env, version):
    _transfer_employee_private_data(env)
    openupgrade.load_data(env, "hr", "17.0.1.1/noupdate_changes.xml")
    openupgrade.delete_records_safely_by_xml_id(env, _deleted_xml_records)
