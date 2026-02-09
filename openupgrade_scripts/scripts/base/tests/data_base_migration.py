env = locals().get("env")
# server action with multiple children
parent_action1 = env["ir.actions.server"].create(
    {
        "name": "test server action 1",
        "state": "multi",
        "model_id": env.ref("base.model_ir_module_module").id,
        "child_ids": [
            (
                0,
                0,
                {
                    "name": "child action 1",
                    "model_id": env.ref("base.model_ir_module_module").id,
                },
            ),
            (
                0,
                0,
                {
                    "name": "child action 2",
                    "model_id": env.ref("base.model_ir_module_module").id,
                },
            ),
        ],
    }
)
parent_action1.copy(
    {
        "name": "test server action 2",
        "child_ids": [
            (6, 0, parent_action1.child_ids.ids),
            (
                0,
                0,
                {
                    "name": "child action 3",
                    "model_id": env.ref("base.model_ir_module_module").id,
                },
            ),
        ],
    }
)
env.cr.commit()
