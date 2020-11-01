# flake8: noqa
# pylint: skip-file

import odoo
from odoo.service import security
from odoo.http import SessionExpiredException, request, OpenERPSession

if True:
    def _check_security(self):
        """
        Check the current authentication parameters to know if those are still
        valid. This method should be called at each request. If the
        authentication fails, a :exc:`SessionExpiredException` is raised.
        """
        if not self.db or not self.uid:
            raise SessionExpiredException("Session expired")
        # We create our own environment instead of the request's one.
        # to avoid creating it without the uid since request.uid isn't set yet
        env = odoo.api.Environment(request.cr, self.uid, self.context)
        # here we check if the session is still valid
        if not security.check_session(self, env):
            # <OpenUpgrade:ADD>
            # When asking openupgrade_records to generate records
            # over jsonrpc, a query on res_users in the call above locks this
            # table for the sql operations that are triggered by the
            # reinstallation of the base module
            env.cr.rollback()
            # </OpenUpgrade>
            raise SessionExpiredException("Session expired")


OpenERPSession.check_security = _check_security
