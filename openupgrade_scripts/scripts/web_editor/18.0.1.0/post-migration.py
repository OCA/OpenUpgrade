import logging

from lxml import etree
from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, version):
    views = env["ir.ui.view"].search(
        [("arch_db", "like", "expr=\"//div[@id='snippet_custom']\"")]
    )
    for view in views:
        try:
            t_element = etree.fromstring(view.arch_db).xpath("//t")[0]
            thumbnail_url = t_element.attrib["t-thumbnail"]
            full_snippet_key = t_element.attrib["t-snippet"]
            template_key, snippet_key = view.key.rsplit(".", 1)
            view.write(
                {
                    "arch": f"""
                    <data inherit_id="{template_key}">
                        <xpath expr="//snippets[@id='snippet_custom']" position="inside">
                            <t t-snippet="{full_snippet_key}" t-thumbnail="{thumbnail_url}"/>
                        </xpath>
                    </data>
                """  # noqa: E501
                }
            )
        except Exception as e:
            _logger.error(f"View with id {view.id} cannot be transformed {e}")
