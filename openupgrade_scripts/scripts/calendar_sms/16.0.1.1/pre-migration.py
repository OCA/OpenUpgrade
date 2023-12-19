from openupgradelib import openupgrade

_xmlids_delete = ["calendar_sms.ir_rule_sms_template_system"]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.delete_records_safely_by_xml_id(env, _xmlids_delete)
