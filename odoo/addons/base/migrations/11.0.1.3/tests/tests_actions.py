# coding: utf-8
# © 2017 Opener B.V. <https://opener.amsterdam>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from odoo.tests.common import TransactionCase


class TestActions(TransactionCase):
    def test_actions(self):
        """ Check that ir_values have been migrated to action fields """
        action_install = self.env.ref(
            'base.action_server_module_immediate_install')
        self.assertEqual(action_install.binding_type, 'action')
        self.assertEqual(
            action_install.binding_model_id.model, 'ir.module.module')
        self.assertEqual(action_install.usage, 'ir_actions_server')
        action_overview = self.env.ref('base.report_ir_model_overview')
        self.assertEqual(action_overview.binding_type, 'report')
        self.assertEqual(action_overview.binding_model_id.model, 'ir.model')
        self.assertEqual(action_overview.type, 'ir.actions.report')
        action_board = self.env.ref('board.open_board_my_dash_action',
                                    raise_if_not_found=False)
        if action_board:  # is board installed?
            self.assertEqual(action_board.usage, 'menu')

    def test_default(self):
        """ Verify that default values are migrated from ir_values """
        field = self.env.ref('base.field_res_partner_lang')
        default = self.env['ir.default'].search([
            ('field_id', '=', field.id)])
        self.assertEqual(default.json_value, '"en_US"')
