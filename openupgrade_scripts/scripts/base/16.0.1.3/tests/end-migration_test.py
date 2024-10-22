# Copyright 2023 Odoo Community Association (OCA)
# Copyright 2023 Guillaume Masson <guillaume.masson@meta-it.fr>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


@openupgrade.migrate(no_version=True)
def migrate(env, version):
    params = env["ir.config_parameter"].sudo()
    params.set_param("openupgrade.test_end_migration", "Executed")
