# Copyright 2018 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def migrate_l10n_fr_siret_field(env):
    """If l10n_fr_siret is installed in version 10.0, we must rename xmlid"""
    if openupgrade.is_module_installed(env.cr, 'l10n_fr_siret'):
        openupgrade.rename_xmlids(
            env.cr, ('l10n_fr_siret.field_res_partner_siret',
                     'l10n_fr.field_res_partner_siret'))


@openupgrade.migrate()
def migrate(env, version):
    migrate_l10n_fr_siret_field(env)
