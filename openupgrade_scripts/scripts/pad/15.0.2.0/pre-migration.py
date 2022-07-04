import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, version):
    """If all company have only one pad_server, this method will create configparam
    If all company have more than one pad_server, user need to enter pad_server in settings
    """
    env.cr.execute(
        """
        SELECT DISTINCT pad_server, pad_key FROM res_company
        WHERE pad_server IS NOT NULL AND pad_server IS NOT NULL
        """
    )
    pad_configs = env.cr.dictfetchall()
    if len(pad_configs) == 1:
        env["ir.config_parameter"].create(
            [
                {
                    "key": "pad.pad_server",
                    "value": pad_configs[0]["pad_server"],
                },
                {
                    "key": "pad.pad_key",
                    "value": pad_configs[0]["pad_key"],
                },
            ]
        )
    else:
        _logger.warning(
            "Pad: The system has multiple pad servers. \
                Odoo 15.0 supports only 1. No pad settings have been changed. \
                    This may require manual configuration after migration."
        )
