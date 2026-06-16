env = locals().get("env")

# create task type with exclusively inactive projects
task_type = env["project.task.type"].create(
    {
        "name": "Task type",
    }
)
project = env["project.project"].create(
    {
        "name": "Inactive project",
        "active": False,
        "type_ids": [(6, 0, task_type.ids)],
    }
)


env.cr.commit()
