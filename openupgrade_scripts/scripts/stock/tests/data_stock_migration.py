env = locals().get("env")
# return a picking so that we have something to migrate
picking = env.ref("stock.outgoing_shipment_main_warehouse1")
return_wizard = (
    env["stock.return.picking"]
    .with_context(
        active_id=picking.id,
        active_ids=picking.ids,
        active_model=picking._name,
    )
    .create({})
)
return_wizard._onchange_picking_id()
return_wizard._create_returns()

env.cr.commit()
