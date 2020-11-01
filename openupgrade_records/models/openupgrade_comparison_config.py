# Copyright 2011-2015 Therp BV <https://therp.nl>
# Copyright 2016 Opener B.V. <https://opener.am>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import fields, models
from odoo.exceptions import UserError
from odoo.tools.translate import _

from .. import apriori


class OpenupgradeComparisonConfig(models.Model):
    _name = "openupgrade.comparison.config"
    _description = "OpenUpgrade Comparison Configuration"

    name = fields.Char()
    server = fields.Char(required=True, default="localhost")
    port = fields.Integer(required=True, default=8069)
    database = fields.Char(required=True)
    username = fields.Char(required=True, default="admin")
    password = fields.Char(required=True, default="admin")
    last_log = fields.Text()

    def get_connection(self):
        self.ensure_one()
        import odoorpc

        remote = odoorpc.ODOO(self.server, port=self.port)
        remote.login(self.database, self.username, self.password)
        return remote

    def test_connection(self):
        self.ensure_one()
        try:
            connection = self.get_connection()
            user_model = connection.env["res.users"]
            ids = user_model.search([("login", "=", "admin")])
            user_info = user_model.read([ids[0]], ["name"])[0]
        except Exception as e:
            raise UserError(_("Connection failed.\n\nDETAIL: %s") % e)
        raise UserError(_("%s is connected.") % user_info["name"])

    def analyze(self):
        """ Run the analysis wizard """
        self.ensure_one()
        wizard = self.env["openupgrade.analysis.wizard"].create(
            {"server_config": self.id}
        )
        return {
            "name": wizard._description,
            "view_mode": "form",
            "res_model": wizard._name,
            "type": "ir.actions.act_window",
            "target": "new",
            "res_id": wizard.id,
            "nodestroy": True,
        }

    def install_modules(self):
        """ Install same modules as in source DB """
        self.ensure_one()
        connection = self.get_connection()
        remote_module_obj = connection.env["ir.module.module"]
        remote_module_ids = remote_module_obj.search([("state", "=", "installed")])

        modules = []
        for module_id in remote_module_ids:
            mod = remote_module_obj.read([module_id], ["name"])[0]
            mod_name = mod["name"]
            mod_name = apriori.renamed_modules.get(mod_name, mod_name)
            modules.append(mod_name)
        _logger = logging.getLogger(__name__)
        _logger.debug("remote modules %s", modules)
        local_modules = self.env["ir.module.module"].search(
            [("name", "in", modules), ("state", "=", "uninstalled")]
        )
        _logger.debug("local modules %s", ",".join(local_modules.mapped("name")))
        if local_modules:
            local_modules.write({"state": "to install"})
        return {}
