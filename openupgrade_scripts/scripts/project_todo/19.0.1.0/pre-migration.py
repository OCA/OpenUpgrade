from openupgradelib import openupgrade

deleted_xmlids = [
    "project_todo.project_task_preload_action_todo",
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.delete_records_safely_by_xml_id(env, deleted_xmlids)
