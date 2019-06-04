# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_xmlids(env.cr, [
            ('base.res_partner_title_dra', 'l10n_do.res_partner_title_dra'),
            ('base.res_partner_title_ing', 'l10n_do.res_partner_title_ing'),
            ('base.res_partner_title_lic', 'l10n_do.res_partner_title_lic'),
            ('base.res_partner_title_licda', 'l10n_do.res_partner_title_licda'),
            ('base.res_partner_title_mba', 'l10n_do.res_partner_title_mba'),
            ('base.res_partner_title_msc', 'l10n_do.res_partner_title_msc')
    ])
