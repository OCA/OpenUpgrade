# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

unlink_by_xmlid = [
    'web_editor.FieldTextHtml',
    'web_editor.assets_editor',
    'web_editor.js_tests_assets',
    'web_editor.layout',
    'web_editor.webclient_bootstrap',
]


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    openupgrade.delete_records_safely_by_xml_id(env, unlink_by_xmlid)
