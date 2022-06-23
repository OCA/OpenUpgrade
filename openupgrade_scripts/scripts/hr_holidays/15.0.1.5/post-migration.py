import logging

from openupgradelib import openupgrade

from odoo import api
from odoo.exceptions import ValidationError

from odoo.addons.hr_holidays.models.hr_leave import HolidaysRequest

_logger = logging.getLogger(__name__)


@api.constrains("holiday_allocation_id")
def _check_allocation_id(self):
    """Don't raise ValidationError in _check_allocation_id method."""
    try:
        return HolidaysRequest._check_allocation_id._original_method(self)
    except ValidationError:
        _logger.warning(
            "Could not find an allocation of type %s for the time off with ID %s."
            "\nRequires allocation of this type is now set to 'No Limit'."
            "\nPlease review requires allocation of this type manually "
            "after the migration."
            % (self.holiday_status_id.mapped("display_name"), self.ids)
        )
        self.holiday_status_id.write({"requires_allocation": "no"})


_check_allocation_id._original_method = HolidaysRequest._check_allocation_id
HolidaysRequest._check_allocation_id = _check_allocation_id


def _fill_hr_leave_holiday_allocation_id(env):
    leaves = env["hr.leave"].search(
        [
            ("holiday_status_id.requires_allocation", "=", "yes"),
            ("date_from", "!=", False),
            ("date_to", "!=", False),
        ]
    )
    leaves._compute_from_holiday_status_id()


@openupgrade.migrate()
def migrate(env, version):
    _fill_hr_leave_holiday_allocation_id(env)
    openupgrade.load_data(env.cr, "hr_holidays", "15.0.1.5/noupdate_changes.xml")
