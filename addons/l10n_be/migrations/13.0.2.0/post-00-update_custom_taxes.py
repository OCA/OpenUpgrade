from openupgradelib import openupgrade
import logging

_logger = logging.getLogger(__name__)


# This is tables of correspondance between old tags and the new tax tags
# based on the tax tag used in the account.tax.template
base_invoice_tag_xmlids = [
    ("tax_tag_00", "+00"),
    ("tax_tag_01", "+01"),
    ("tax_tag_02", "+02"),
    ("tax_tag_03", "+03"),
    ("tax_tag_44", "+44"),
    ("tax_tag_45", "+45"),
    ("tax_tag_46L", "+46L"),
    ("tax_tag_46T", "+46T"),
    ("tax_tag_47", "+47"),
    ("tax_tag_81", "+81"),
    ("tax_tag_82", "+82"),
    ("tax_tag_83", "+83"),
    ("tax_tag_86", "+86"),
    ("tax_tag_87", "+87"),
    ("tax_tag_88", "+88"),
    ("tax_tag_81_not_deductible", "+81"),
    ("tax_tag_82_not_deductible", "+82"),
    ("tax_tag_83_not_deductible", "+83"),
]

tax_invoice_tag_xmlids = [
    ("tax_tag_54", "+54"),
    ("tax_tag_55", "-55"),
    ("tax_tag_56", "-56"),
    ("tax_tag_57", "-57"),
    ("tax_tag_59", "+59"),
    ("tax_tag_82", "+82"),
    ("tax_tag_82_not_deductible", "+82"),
]

base_refund_tag_xmlids = [
    ("tax_tag_48s44", "+48s44"),
    ("tax_tag_48s46L", "+48s46L"),
    ("tax_tag_48s46T", "+48s46T"),
    ("tax_tag_49", "+49"),
    ("tax_tag_81", "-81"),
    ("tax_tag_82", "-82"),
    ("tax_tag_83", "-83"),
    ("tax_tag_84", "+84"),
    ("tax_tag_85", "+85"),
    ("tax_tag_86", "-86"),
    ("tax_tag_87", "-87"),
    ("tax_tag_88", "-88"),
    ("tax_tag_81_not_deductible", "-81"),
    ("tax_tag_82_not_deductible", "-82"),
    ("tax_tag_83_not_deductible", "-83"),
    ("tax_tag_85_not_deductible", "+85"),
]

tax_refund_tag_xmlids = [
    ("tax_tag_63", "+63"),
    ("tax_tag_64", "+64"),
    ("tax_tag_82", "-82"),
    ("tax_tag_82_not_deductible", "-82"),
]

tax_unclassified_tag_xmlids = [
    "tax_tag_61",
    "tax_tag_62",
]


def update_custom_account_tax(env):
    """This function tries to update custom account.tax"""
    # get old tags and extract their code names
    correspondance = {
        ("invoice", "base"): [
            (env.ref("l10n_be." + xmlid), new_name)
            for xmlid, new_name in base_invoice_tag_xmlids
        ],
        ("invoice", "tax"): [
            (env.ref("l10n_be." + xmlid), new_name)
            for xmlid, new_name in tax_invoice_tag_xmlids
        ],
        ("refund", "base"): [
            (env.ref("l10n_be." + xmlid), new_name)
            for xmlid, new_name in base_refund_tag_xmlids
        ],
        ("refund", "tax"): [
            (env.ref("l10n_be." + xmlid), new_name)
            for xmlid, new_name in tax_refund_tag_xmlids
        ],
    }

    def get_parent_tax_tags(account_tax):
        """Return old tags that were linked on the parent tax if any"""
        parent_tax_id = (
            env["account.tax"]
            .with_context(active_test=False)
            .search([("children_tax_ids", "in", account_tax.id)], limit=1)
        )
        if not parent_tax_id:
            return None
        env.cr.execute(
            """SELECT account_account_tag_id
            FROM account_tax_account_tag
            WHERE account_tax_id = %s
            """,
            (parent_tax_id.id,),
        )
        parent_tax_tags = [int(res[0]) for res in env.cr.fetchall()]
        parent_tax_tag_ids = (
            env["account.account.tag"]
            .with_context(active_test=False)
            .search([("id", "in", parent_tax_tags)])
        )
        return parent_tax_tag_ids

    def get_new_tag_names(tag_ids, old_tags):
        """Return list of code and old_tags for tag_ids that exists in
        old_tags
        """
        keep_tags = []
        for tag in tag_ids:
            for old_tag, new_name in old_tags:
                if tag == old_tag:
                    keep_tags.append(new_name)
        return keep_tags

    def repartition_lines_iter(account_tax):
        """Special loop over repartition lines in an account.tax"""
        for repartition in account_tax.invoice_repartition_line_ids:
            yield ("invoice", repartition)
        for repartition in account_tax.refund_repartition_line_ids:
            yield ("refund", repartition)

    custom_account_tax_ids = (
        env["account.tax"]
        .with_context(active_test=False)
        .search([])
    )
    for account_tax in custom_account_tax_ids:
        parent_tax_tag_ids = get_parent_tax_tags(account_tax)
        for reptype, repartition in repartition_lines_iter(account_tax):
            key = (reptype, repartition.repartition_type)
            # keep right tags
            if (
                repartition.repartition_type == "base"
                and parent_tax_tag_ids is not None
            ):
                keep_tags = get_new_tag_names(
                    parent_tax_tag_ids, correspondance[key]
                )
            else:
                keep_tags = get_new_tag_names(
                    repartition.tag_ids, correspondance[key]
                )
            # fix special cases
            # tag "82" can not be set on tax lines if other tags are
            # assigned to these tax lines
            if (
                repartition.repartition_type == "tax"
                and len(keep_tags) > 1
            ):
                if "+82" in keep_tags:
                    keep_tags.remove("+82")
                if "-82" in keep_tags:
                    keep_tags.remove("-82")
            # convert tags
            new_tags = env["account.account.tag"]
            for new_name in keep_tags:
                new_tag = env["account.account.tag"].search(
                    [("name", "=", new_name)], limit=1,
                )
                new_tags |= new_tag
            repartition.tag_ids = new_tags


@openupgrade.migrate()
def migrate(env, version):
    update_custom_account_tax(env)
