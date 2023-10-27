from openupgradelib import openupgrade


def try_delete_noupdate_records(env):
    openupgrade.delete_records_safely_by_xml_id(
        env,
        [
            "crm.email_template_opportunity_mail",
        ],
    )


def fix_crm_team_use_leads(env):
    """Since v15 there are mechanisims to toggle this crm.team flag depending on the
    groups and reset some defaults [0]. There's also a mechanisim to automatically set
    as lead the crm.lead created from the website form when the assigned team has
    the flag use_leads on [1] making that the user wouldn't be able to reach those leads
    as the menu isn't available. As we could have inconsistent states from the previous
    installation we try to settle the states correctly.
    [0] odoo/odoo/blob/15.0/addons/website_crm/models/crm_lead.py#L55
    [1] odoo/odoo/tree/15.0/addons/crm/models/res_config_settings.py#L136-L141
    """
    use_leads = env.ref("crm.group_use_lead") in env.ref("base.group_user").implied_ids
    # We use leads, no problem in this case. The mechanisims in v15 will set things
    # correctly in case the admins change the settings.
    if use_leads:
        return
    # If we don't use leads, these teams aren't set correctly
    lead_teams = env["crm.team"].search([("use_leads", "=", True)])
    lead_teams.use_leads = False
    # Re-calculate the alias settings to avoid remanents of wrong behavior
    for team in lead_teams:
        team.alias_id.write(team._alias_get_creation_values())


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env.cr, "crm", "15.0.1.6/noupdate_changes.xml")
    try_delete_noupdate_records(env)
    openupgrade.logged_query(
        env.cr,
        """DELETE FROM ir_model_data
        WHERE module = 'crm' AND name = 'mail_alias_lead_info'""",
    )
