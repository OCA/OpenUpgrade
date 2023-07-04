from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.delete_records_safely_by_xml_id(
        env, ["analytic.analytic_tag_comp_rule", "analytic.analytic_group_comp_rule"]
    )
