from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.m2o_to_x2m(env.cr, env["crm.stage"], "crm_stage", "team_ids", "team_id")
    openupgrade.load_data(env, "crm", "19.0.1.9/noupdate_changes.xml")
