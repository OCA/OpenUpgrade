from odoo import api
from odoo.addons.point_of_sale.models.pos_config import PosConfig

if True:

    @api.model
    def post_install_pos_localisation(self, companies=False):
        # <OpenUpgrade:REMOVE>
        # don't try to setup_defaults, because it will fail
        # when executing the generation of records, in the openupgrade_records
        # module.
        # self = self.sudo()
        # if not companies:
        #     companies = self.env['res.company'].search([])
        # for company in companies.filtered('chart_template_id'):
        #     pos_configs = self.search([('company_id', '=', company.id)])
        #     pos_configs.setup_defaults(company)
        pass
        # </OpenUpgrade>

PosConfig.post_install_pos_localisation = post_install_pos_localisation
