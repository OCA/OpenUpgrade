from openupgradelib import openupgrade, openupgrade_130
import logging

_logger = logging.getLogger(__name__)


def convert_old_tax_tags_into_new_report_line_tags(env):
    """ The normal migration script of module account tries to link the
        old account.account.tag's to account.tax.repartition.line's.
        However, account.account.tag's are revamped in 13.0, they come
        in positive (debit) and negative (credit) flavors. Luckily,
        account.tax.report.line's are added from XML, which happen to
        use the same and similar names as the old - and new
        account.account.tag's. So we use that name as the link between
        them.
    """
    def expect_tag_not_used(env, tag_id, tag_name):
        lines = env['account.tax.repartition.line'].search([
            ('tag_ids', '=', tag_id),
        ])
        if lines:
            _logger.error('Tag is still used and could not be converted: %s'
                          % tag_name)
            return False
        return True

    def find_tag_by_name(env, name, negate, country_id):
        if negate is None:
            negate_comparison = 'IS NULL'
        elif negate:
            negate_comparison = '= TRUE'
        else:
            negate_comparison = '= FALSE'

        # The check against country_id is left out on purpose because
        # it is not uncommon for tags to not have this field set
        # correctly.
        env.cr.execute("""
            SELECT id FROM account_account_tag
            WHERE
                tax_negate {} AND
                name = %s AND
                applicability = 'taxes'
        """.format(negate_comparison), (name,))

        # Return whether or not a tag
        result = env.cr.fetchone()
        return result[0] if result else None

    def get_tag_from_report_line(env, report_line_id, negate):
        env.cr.execute("""
            SELECT account_account_tag_id
            FROM account_tax_report_line_tags_rel WHERE
                account_tax_report_line_id = %s AND
                account_account_tag_id IN (
                    SELECT id FROM account_account_tag WHERE
                        tax_negate = %s AND
                        applicability = 'taxes'
                )
        """, (report_line_id, negate))
        return env.cr.fetchone()[0]

    report_lines = env['account.tax.report.line'].search([])
    for report_line in report_lines:
        old_tag_id = find_tag_by_name(
            env,
            report_line.name,
            None,
            report_line.country_id.id)

        # If the report line has not tag_name field, check to see if
        # this would be a problem because an old tag would still need to
        # be converted.
        if not report_line.tag_name:
            if not old_tag_id:
                _logger.info("Report line has no tag_name, but is ok because "
                             "the old tag doesn't exist: %s", report_line.name)
                continue
            else:
                if not expect_tag_not_used(env, old_tag_id, report_line.name):
                    _logger.info("Report line has no tag_name, but is ok "
                                 "because the old tag was not used anyway: %s",
                                 report_line.name)
        else:
            new_debit_tag_id = get_tag_from_report_line(
                env,
                report_line.id,
                True)
            new_credit_tag_id = get_tag_from_report_line(
                env,
                report_line.id,
                False)

            if not old_tag_id:
                expect_tag_not_used(env, old_tag_id, report_line.name)
            else:
                # If there is no new tag to be matched, check to see if
                # that would be a problem because the old tag still exists
                if not new_debit_tag_id and not new_credit_tag_id:
                    if not expect_tag_not_used(env, old_tag_id,
                                               report_line.name):
                        _logger.warning("Old tag not used, skipping: %s",
                                        report_line.name)

                # If new tags do exist, convert them
                else:
                    openupgrade_130.convert_old_style_tax_tag_to_new(
                        env,
                        report_line,
                        old_tag_id,
                        new_debit_tag_id,
                        new_credit_tag_id
                    )


def disable_troublesome_tags(env):
    openupgrade.logged_query(env.cr, """
        UPDATE account_account_tag
        SET active = FALSE
        WHERE
            name NOT LIKE '+%' AND
            name NOT LIKE '-%' AND
            applicability = 'taxes'
    """)


TAG_TAX_ID_START = 18
TAG_TAX_ID_END = 40
TAG_ID_END = 42

base_tag_xmlids = [
    'tag_nl_%02d' % x for x in
    set(range(1, TAG_TAX_ID_START)).union(range(TAG_TAX_ID_END, TAG_ID_END))]
tax_tag_xmlids = [
    'tag_nl_%02d' % x for x in
    range(TAG_TAX_ID_START, TAG_TAX_ID_END)]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade_130.unlink_invalid_tax_tags_from_move_lines(
        env,
        base_tag_xmlids,
        tax_tag_xmlids)
    openupgrade_130.unlink_invalid_tax_tags_from_repartition_lines(
        env,
        base_tag_xmlids,
        tax_tag_xmlids)
    convert_old_tax_tags_into_new_report_line_tags(env)
    disable_troublesome_tags(env)
