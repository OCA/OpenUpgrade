import logging

from openupgradelib import openupgrade

from odoo import tools

from odoo.addons.openupgrade_scripts.apriori import merged_modules, renamed_modules

_logger = logging.getLogger(__name__)


@openupgrade.migrate(use_env=False)
def migrate(cr, version):
    """
    Don't request an env for the base pre-migration as flushing the env in
    odoo/modules/registry.py will break on the 'base' module not yet having
    been instantiated.
    """
    if "openupgrade_framework" not in tools.config["server_wide_modules"]:
        _logger.error(
            "openupgrade_framework is not preloaded. You are highly "
            "recommended to run the Odoo with --load=openupgrade_framework "
            "when migrating your database."
        )
    openupgrade.update_module_names(cr, renamed_modules.items())
    openupgrade.update_module_names(cr, merged_modules.items(), merge_modules=True)
