# Copyright 2024 Viindoo Technology Joint Stock Company (Viindoo)
# Copyright Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from odoo import api
from odoo.exceptions import ValidationError
from odoo.modules.module import get_resource_from_path
from odoo.tools import mute_logger

from odoo.addons.base.models.ir_ui_view import IrUiView

_logger = logging.getLogger(__name__)


@api.constrains("arch_db")
def _check_xml(self):
    """Don't raise or log exceptions in view validation unless explicitely
    requested. Mute warnings about views which are common during migration."""
    with mute_logger("odoo.addons.base.models.ir_ui_view"):
        try:
            return IrUiView._check_xml._original_method(self)
        except ValidationError as e:
            _logger.warning(
                "Can't render custom view %s for model %s. "
                "Assuming you are migrating between major versions of Odoo. "
                "Please review the view contents manually after the migration.\n"
                "Error: %s",
                self.xml_id,
                self.model,
                e,
            )


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
            return IrUiView._raise_view_error._original_method(
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


def _check_field_paths(self, node, field_paths, model_name, use):
    """Ignore UnboundLocalError when we squelched the raise about missing fields"""
    try:
        return IrUiView._check_field_paths._original_method(
            self, node, field_paths, model_name, use
        )
    except UnboundLocalError:  # pylint: disable=except-pass
        pass


def _inverse_arch(self):
    """
    Remove install_filename from context if it's from openupgrade_scripts.
    Without this, arch_fs will point to openupgrade_scripts' file which most likely
    won't exist when the migrated database is deployed, which breaks resetting views
    """
    if "install_filename" in self.env.context:
        path_info = get_resource_from_path(self.env.context["install_filename"])
        if path_info and path_info[0] == "openupgrade_scripts":
            self = self.with_context(  # pylint: disable=context-overridden
                {k: v for k, v in self.env.context.items() if k != "install_filename"}
            )
    return _inverse_arch._original_method(self)


_check_xml._original_method = IrUiView._check_xml
IrUiView._check_xml = _check_xml
_raise_view_error._original_method = IrUiView._raise_view_error
IrUiView._raise_view_error = _raise_view_error
_check_field_paths._original_method = IrUiView._check_field_paths
IrUiView._check_field_paths = _check_field_paths
_inverse_arch._original_method = IrUiView._inverse_arch
IrUiView._inverse_arch = _inverse_arch
