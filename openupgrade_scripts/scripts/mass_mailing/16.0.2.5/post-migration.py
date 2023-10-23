# Copyright 2023 Viindoo - locdang8
# Copyright 2023 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

_delete_xmlids = [
    "mass_mailing.s_blockquote_cover_default_image",
    "mass_mailing.s_company_team_image_1",
    "mass_mailing.s_company_team_image_2",
    "mass_mailing.s_company_team_image_3",
    "mass_mailing.s_company_team_image_4",
    "mass_mailing.s_product_list_default_image_4",
    "mass_mailing.s_product_list_default_image_5",
    "mass_mailing.s_product_list_default_image_6",
    "mass_mailing.s_reference_default_image_6",
    "mass_mailing.s_reference_demo_image_1",
    "mass_mailing.s_reference_demo_image_2",
    "mass_mailing.s_reference_demo_image_3",
    "mass_mailing.s_reference_demo_image_4",
    "mass_mailing.s_reference_demo_image_5",
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env.cr, "mass_mailing", "16.0.2.5/noupdate_changes.xml")
    openupgrade.delete_records_safely_by_xml_id(env, _delete_xmlids)
