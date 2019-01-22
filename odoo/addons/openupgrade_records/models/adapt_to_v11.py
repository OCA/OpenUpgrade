# coding: utf-8
# Copyright 2019 Eficent <http://www.eficent.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import math
from odoo import models
from odoo.exceptions import AccessDenied
from odoo.http import request


class Users(models.Model):
    _inherit = "res.users"

    def _check_credentials(self, password):
        cr = self.env.cr
        cr.execute(
            "SELECT latest_version FROM ir_module_module WHERE name=%s",
            ('base', )
        )
        base_version = cr.fetchone()
        if base_version:
            local_version = '.'.join(base_version[0].split('.')[:2])
            cr.execute(
                "SELECT id FROM ir_module_module WHERE name=%s "
                "AND state = 'installed'",
                ('auth_crypt',)
            )
            auth_crypt = cr.fetchone()
            if local_version == '11.0' and auth_crypt:
                assert password
                self.env.cr.execute(
                    "SELECT password_crypt FROM res_users WHERE id=%s",
                    [self.env.user.id]
                )
                [hashed] = self.env.cr.fetchone()
                valid, replacement = self._crypt_context() \
                    .verify_and_update(password, hashed)
                if replacement is not None:
                    self._set_encrypted_password(self.env.user.id, replacement)
                if not valid:
                    raise AccessDenied()
                return
        return super(Users, self)._check_credentials(password)


class Http(models.AbstractModel):
    _inherit = 'ir.http'

    def get_currencies(self):
        cr = self.env.cr
        cr.execute(
            "SELECT latest_version FROM ir_module_module WHERE name=%s",
            ('base', )
        )
        base_version = cr.fetchone()
        if base_version:
            local_version = '.'.join(base_version[0].split('.')[:2])
            cr.execute(
                "SELECT id FROM ir_module_module WHERE name=%s "
                "AND state = 'installed'",
                ('web',)
            )
            web = cr.fetchone()
            if local_version == '11.0' and web:
                currency_model = request.env['res.currency']
                currencies = currency_model.with_context(
                    prefetch_fields=False).search([]).read(
                    ['symbol', 'position', 'rounding'])
                for c in currencies:
                    if 0 < c['rounding'] < 1:
                        c['decimal_places'] = int(
                            math.ceil(math.log10(1 / c['rounding'])))
                    else:
                        c['decimal_places'] = 0
                return {
                    c['id']: {
                        'symbol': c['symbol'],
                        'position': c['position'],
                        'digits': [69, c['decimal_places']]
                    } for c in currencies}
        return super(Http, self).get_currencies()
