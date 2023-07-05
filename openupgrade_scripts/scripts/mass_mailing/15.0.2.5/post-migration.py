from lxml.etree import tostring
from lxml.html import fromstring
from openupgradelib import openupgrade

from odoo.osv import expression


def _migrate_mailing_body(env, domain=None):
    """Make previous mailings work with the editor. We just have to rewrap them as
    the editor expect them to be. A simple f string isn't enough as some mailings
    could have a parent node that we need to replace and some other might not. This
    way we ensure both scenarios. If there's no parent node lxml injects one."""
    domain = domain or []
    domain = expression.AND(
        [["|", ("body_html", "!=", False), ("body_html", "!=", "")], domain]
    )
    mailings = env["mailing.mailing"].with_context(active_test=False).search(domain)
    for mailing in mailings:
        try:
            html_tree = fromstring(str(mailing.body_html))
        except Exception:
            # Avoid content errors
            continue
        wrapper = fromstring(
            """
<div class="o_layout oe_unremovable oe_unmovable bg-200 o_empty_theme" data-name="Mailing">
    <div class="container o_mail_wrapper o_mail_regular oe_unremovable">
        <div class="row">
            <div
                class="col o_mail_no_options o_mail_wrapper_td bg-white oe_structure o_editable"
                contenteditable="true"
            >
            </div>
        </div>
    </div>
</div>
            """
        )
        new_parent_node, *_ = wrapper.xpath("//div[@contenteditable='true']")
        for children in html_tree:
            new_parent_node.append(children)
        mailing.body_arch = tostring(wrapper, pretty_print=True, encoding="utf-8")


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env.cr, "mass_mailing", "15.0.2.5/noupdate_changes.xml")
    openupgrade.delete_record_translations(
        env.cr,
        "mass_mailing",
        ["ir_cron_mass_mailing_queue"],
    )
    _migrate_mailing_body(env)
