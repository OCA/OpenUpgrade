# Copyright Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from odoo import api
from odoo.tools import mute_logger

from odoo.addons.base.models.ir_ui_view import NameManager, View

_logger = logging.getLogger(__name__)


@api.constrains("arch_db")
def _check_xml(self):
    """Mute warnings about views which are common during migration"""
    with mute_logger("odoo.addons.base.models.ir_ui_view"):
        return View._check_xml._original_method(self)


def _check(self, view):
    """Because we captured the exception in _raise_view_error and archived that view,
    so info is None, but it is called to info.get('select') in NameManager.check,
    which will raise an exception AttributeError,
    so we need to override to not raise an exception
    """
    try:
        return NameManager.check._original_method(self, view)
    except AttributeError as e:
        if e.args[0] == "'NoneType' object has no attribute 'get'":
            pass
        else:
            raise


def _raise_view_error(
    self, message, node=None, *, from_exception=None, from_traceback=None
):
    """Don't raise or log exceptions in view validation unless explicitely
    requested
    """
    raise_exception = self.env.context.get("raise_view_error")
    to_mute = "odoo.addons.base.models.ir_ui_view" if raise_exception else "not_muted"
    with mute_logger(to_mute):
        try:
            return View._raise_view_error._original_method(
                self,
                message,
                node=node,
                from_exception=from_exception,
                from_traceback=from_traceback,
            )
        except ValueError as e:
            _logger.warning(
                "Can't render custom view %s for model %s. "
                "Assuming you are migrating between major versions of Odoo. "
                "Please review the view contents manually after the migration.\n"
                "Error: %s",
                self.xml_id,
                self.model,
                e,
            )


_check_xml._original_method = View._check_xml
View._check_xml = _check_xml
_check._original_method = View._check
View._check = _check
_raise_view_error._original_method = View._raise_view_error
View._raise_view_error = _raise_view_error
