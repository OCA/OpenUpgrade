# coding: utf-8
import logging

from openupgradelib import openupgrade, openupgrade_90

_logger = logging.getLogger(__name__)

account_type_map = [
    ('l10n_nl.user_type_tax', 'account.data_account_type_current_liabilities'),
    ('l10n_nl.user_type_equity', 'account.data_account_type_equity'),
]


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    """ Migrate old l10n_nl specific account types to standard account types.
    Users may want to set the type of recoverable VAT accounts to an asset
    type manually. """
    openupgrade_90.replace_account_types(env, account_type_map)
