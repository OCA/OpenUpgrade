# Copyright 2020 Odoo Community Association (OCA)
# Copyright 2020 Opener B.V. <stefan@opener.am>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def install_unmet_dependencies(env):
    """When changing the dependency of module which is not installed on the target version,
    this method to install the missing modules to avoid error unmet_dependencies
    """
    installed_modules = env['ir.module.module'].search([('state','=','installed')])
    installed_modules.update_list()
    modules_to_install = installed_modules.upstream_dependencies(
        exclude_states=('uninstallable', 'installed', 'to upgrade', 'to remove', 'to install'),
        )

    openupgrade.logged_query(
        env.cr,
        """
        UPDATE ir_module_module
        SET state='to install'
        WHERE id in (%s)"""
        % (", ".join([str(m_id) for m_id in modules_to_install.ids]),)
    )


@openupgrade.migrate()
def migrate(env, version):
    install_unmet_dependencies(env)
    # Load noupdate changes
    openupgrade.load_data(env.cr, "base", "14.0.1.3/noupdate_changes.xml")
