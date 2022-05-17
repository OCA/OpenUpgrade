# Copyright 2020 Odoo Community Association (OCA)
# Copyright 2020 Opener B.V. <stefan@opener.am>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

from openupgradelib import openupgrade

from odoo import tools

_logger = logging.getLogger(__name__)

try:
    from odoo.addons.openupgrade_scripts.apriori import merged_modules, renamed_modules
except ImportError:
    renamed_modules = {}
    merged_modules = {}
    _logger.warning(
        "You are using openupgrade_framework without having"
        " openupgrade_scripts module available."
        " The upgrade process will not work properly."
    )

rename_xmlids_l10n_ec = [
    ("l10n_ec.state_ec_1", "base.state_ec_01"),
    ("l10n_ec.state_ec_2", "base.state_ec_02"),
    ("l10n_ec.state_ec_3", "base.state_ec_03"),
    ("l10n_ec.state_ec_4", "base.state_ec_04"),
    ("l10n_ec.state_ec_5", "base.state_ec_05"),
    ("l10n_ec.state_ec_6", "base.state_ec_06"),
    ("l10n_ec.state_ec_7", "base.state_ec_07"),
    ("l10n_ec.state_ec_8", "base.state_ec_08"),
    ("l10n_ec.state_ec_9", "base.state_ec_09"),
    ("l10n_ec.state_ec_10", "base.state_ec_10"),
    ("l10n_ec.state_ec_11", "base.state_ec_11"),
    ("l10n_ec.state_ec_12", "base.state_ec_12"),
    ("l10n_ec.state_ec_13", "base.state_ec_13"),
    ("l10n_ec.state_ec_14", "base.state_ec_14"),
    ("l10n_ec.state_ec_15", "base.state_ec_15"),
    ("l10n_ec.state_ec_16", "base.state_ec_16"),
    ("l10n_ec.state_ec_17", "base.state_ec_17"),
    ("l10n_ec.state_ec_18", "base.state_ec_18"),
    ("l10n_ec.state_ec_19", "base.state_ec_19"),
    ("l10n_ec.state_ec_20", "base.state_ec_20"),
    ("l10n_ec.state_ec_21", "base.state_ec_21"),
    ("l10n_ec.state_ec_22", "base.state_ec_22"),
    ("l10n_ec.state_ec_23", "base.state_ec_23"),
    ("l10n_ec.state_ec_24", "base.state_ec_24"),
]

rename_xmlids_mail = [
    ("mail.icp_mail_catchall_alias", "base.icp_mail_catchall_alias"),
    ("mail.icp_mail_bounce_alias", "base.icp_mail_bounce_alias"),
]


@openupgrade.migrate(use_env=False)
def migrate(cr, version):
    """
    Don't request an env for the base pre-migration as flushing the env in
    odoo/modules/registry.py will break on the 'base' module not yet having
    been instantiated.
    """
    if "openupgrade_framework" not in tools.config["server_wide_modules"]:
        logging.error(
            "openupgrade_framework is not preloaded. You are highly "
            "recommended to run the Odoo with --load=openupgrade_framework "
            "when migrating your database."
        )

    openupgrade.rename_xmlids(cr, rename_xmlids_l10n_ec)
    openupgrade.rename_xmlids(cr, rename_xmlids_mail)

    openupgrade.update_module_names(cr, renamed_modules.items())
    openupgrade.update_module_names(cr, merged_modules.items(), merge_modules=True)

    openupgrade.convert_field_to_html(
        cr, "res_company", "report_footer", "report_footer"
    )
    openupgrade.convert_field_to_html(
        cr, "res_company", "report_header", "report_header"
    )
    openupgrade.convert_field_to_html(cr, "res_partner", "comment", "comment")
