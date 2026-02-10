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
    """On v17, there's no more private res.partner records, and the base migration
    has copied private partners to table ou_res_partner_private, so we transfer the
    information to the dedicated employee fields from the copy containing private
    data if it exists, and from res.partner otherwise
    """
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE hr_employee he
        SET lang = rp.lang,
            private_city = COALESCE(he.private_city, rpp.city, rp.city),
            private_country_id = COALESCE(
                he.private_country_id, rpp.country_id, rp.country_id
            ),
            private_email = COALESCE(he.private_email, rpp.email, rp.email),
            private_phone = COALESCE(
                he.private_phone, rpp.phone, rpp.mobile, rp.phone, rp.mobile
            ),
            private_state_id = COALESCE(he.private_state_id, rpp.state_id, rp.state_id),
            private_street = COALESCE(he.private_street, rpp.street, rp.street),
            private_street2 = COALESCE(he.private_street2, rpp.street2, rp.street2),
            private_zip = COALESCE(he.private_zip, rpp.zip, rp.zip)
        FROM res_partner rp
        LEFT JOIN ou_res_partner_private rpp
        ON rp.id=rpp.id
        WHERE he.address_home_id = rp.id""",
    )


@openupgrade.migrate()
def migrate(env, version):
    _transfer_employee_private_data(env)
    openupgrade.load_data(env, "hr", "17.0.1.1/noupdate_changes.xml")
    openupgrade.delete_records_safely_by_xml_id(env, _deleted_xml_records)
