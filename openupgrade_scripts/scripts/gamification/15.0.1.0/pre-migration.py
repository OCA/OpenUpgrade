from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.set_xml_ids_noupdate_value(
        env, "gamification", ["mail_template_data_new_rank_reached"], True
    )
    openupgrade.convert_field_to_html(
        env.cr, "gamification_badge", "description", "description"
    )
