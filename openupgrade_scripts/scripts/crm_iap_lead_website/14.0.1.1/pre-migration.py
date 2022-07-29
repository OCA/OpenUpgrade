from openupgradelib import openupgrade


def m2m_columns_and_tables_renamed(env):
    openupgrade.rename_columns(
        env.cr,
        {"crm_lead_tag_crm_reveal_rule_rel": [("crm_lead_tag_id", "crm_tag_id")]},
    )

    openupgrade.rename_tables(
        env.cr,
        [("crm_lead_tag_crm_reveal_rule_rel", "crm_reveal_rule_crm_tag_rel")],
    )


@openupgrade.migrate()
def migrate(env, version):
    m2m_columns_and_tables_renamed(env)
