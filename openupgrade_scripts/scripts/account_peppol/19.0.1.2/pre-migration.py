from openupgradelib import openupgrade

_renamed_models = [("account_peppol.service.wizard", "peppol.config.wizard")]
_renamed_tables = [("account_peppol_service_wizard", "peppol_config_wizard")]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_models(env.cr, _renamed_models)
    openupgrade.rename_tables(env.cr, _renamed_tables)
