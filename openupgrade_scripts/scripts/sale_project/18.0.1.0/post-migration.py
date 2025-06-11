# Copyright 2025 Le Filament (https://le-filament.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade, openupgrade_180


def _convert_company_dependent(env):
    openupgrade_180.convert_company_dependent(
        env,
        "product.template",
        "project_id",
    )
    openupgrade_180.convert_company_dependent(
        env,
        "product.template",
        "project_template_id",
    )


@openupgrade.migrate()
def migrate(env, version):
    _convert_company_dependent(env)
