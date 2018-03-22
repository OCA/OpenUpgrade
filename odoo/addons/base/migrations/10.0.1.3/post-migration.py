# coding: utf-8
# © 2017-2018 Opener BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def handle_im_odoo_support_views(env):
    """ im_odoo_support is a deprecated module, merged into im_livechat.
    If the latter module is not installed, a broken version of
    im_odoo_support.assets_backend is left in the database which breaks the
    web client after the migration. """
    module = env['ir.module.module'].search([('name', '=', 'im_livechat')])
    if module and module.state not in ('to upgrade', 'installed'):
        view = env.ref('im_livechat.assets_backend', False)
        if view and not env['ir.ui.view'].search([
                ('inherit_id', '=', view.id)]):
            view.unlink()


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    handle_im_odoo_support_views(env)
    openupgrade.load_data(
        env.cr, 'base', 'migrations/10.0.1.3/noupdate_changes.xml'
    )
