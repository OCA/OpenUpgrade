from odoo.addons import stock


def pre_init_hook(cr):
    # <OpenUpgrade:REMOVE>
    # don't uninstall data as this breaks the analysis
    # Origin of this code is https://github.com/odoo/odoo/issues/22243
    # env = api.Environment(cr, SUPERUSER_ID, {})
    # env['ir.model.data'].search([
    #     ('model', 'like', '%stock%'),
    #     ('module', '=', 'stock')
    # ]).unlink()
    pass
    # </OpenUpgrade>


stock.pre_init_hook = pre_init_hook
