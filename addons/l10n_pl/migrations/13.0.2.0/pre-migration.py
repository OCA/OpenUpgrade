# Copyright 2022 Macopedia <https://www.macopedia.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

_xml_noupdate_to_zero = (
    'tag_pl_01',
    'tag_pl_02',
    'tag_pl_03',
    'tag_pl_04',
    'tag_pl_05',
    'tag_pl_06',
    'tag_pl_07',
    'tag_pl_08',
    'tag_pl_09',
    'tag_pl_10',
    'tag_pl_11',
    'tag_pl_12',
    'tag_pl_13',
    'tag_pl_14',
    'tag_pl_15',
    'tag_pl_16',
    'tag_pl_17',
    'tag_pl_18',
    'tag_pl_19',
    'tag_pl_20',
    'tag_pl_21',
    'tag_pl_22',
    'tag_pl_23',
    'tag_pl_24',
    'tag_pl_25',
    'tag_pl_26',
    'tag_pl_27',
    'tag_pl_28',
    'tag_pl_29',
    'tag_pl_30',
    'tag_pl_31',
    'tag_pl_32',
    'tag_pl_33',
    'tag_pl_34',
    'tag_pl_35',
    'tag_pl_36',
    'tag_pl_37',
    'tag_pl_38',
    'tag_pl_39',
    'tag_pl_40',
    'tag_pl_41',
    'tag_pl_42',
    'tag_pl_43',
    'tag_pl_44',
    'tag_pl_45',
    'tag_pl_46',
    'tag_pl_47',
    'tag_pl_48',
    'tag_pl_49',
    'tag_pl_50',
    'account_type_nonbalance',
    'account_type_tax',
    'pl_chart_template',
    'CA01',
    'CA02',
    'CA03',
    'CA04',
    'CA05',
    'CA06',
    'CA07',
    'CA08',
    'CA09',
    'CA10',
    'CA11',
    'CA12',
    'CA13',
    'CA14',
    'CA15',
    'CA16'
)


def update_account_account_user_type_id(env):
    """Some relations in account.account model to account.account.types were moved to account.account module"""
    openupgrade.logged_query(
        env.cr, """
        UPDATE account_account
        SET user_type_id = (SELECT id FROM account_account_type WHERE name = 'Off-Balance Sheet')
        WHERE code in (
            '29-010-000',
            '29-020-000',
            '29-030-000'
        );
        """
    )
    openupgrade.logged_query(
        env.cr, """
        UPDATE account_account
        SET user_type_id = (SELECT id FROM account_account_type WHERE name = 'Current Liabilities')
        WHERE code in (
            '22-010-000',
            '22-030-100',
            '22-030-200',
            '22-030-300',
            '22-030-400',
            '22-030-500',
            '22-030-600',
            '22-040-000',
            '22-040-100',
            '22-040-200',
            '22-040-300',
            '22-040-400',
            '22-040-500',
            '87-010-000'
        );
        """
    )
    openupgrade.logged_query(
        env.cr, """
        UPDATE account_account
        SET user_type_id = (SELECT id FROM account_account_type WHERE name = 'Current Assets')
        WHERE code in (
            '22-020-100',
            '22-020-200',
            '22-020-300',
            '22-020-400',
            '22-020-500',
            '22-020-600',
            '87-020-000'
        );
        """
    )


@openupgrade.migrate()
def migrate(env, version):
    update_account_account_user_type_id(env)
    openupgrade.set_xml_ids_noupdate_value(
        env,
        'l10n_pl',
        _xml_noupdate_to_zero,
        False
    )
