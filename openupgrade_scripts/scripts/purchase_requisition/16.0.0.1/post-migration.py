from openupgradelib import openupgrade


def _fill_purchase_order_group(env):
    tender_xml = env.ref("purchase_requisition.type_multi", raise_if_not_found=False)
    if tender_xml:
        requisition_data = env["purchase.requisition"].search_read(
            [
                ("type_id", "=", tender_xml.id),
            ],
            ["purchase_ids"],
        )
        po_group_vals_list = []
        for req in requisition_data:
            if not req.get("purchase_ids"):
                continue
            po_group_vals_list.append({"order_ids": [(6, 0, req["purchase_ids"])]})

        if po_group_vals_list:
            env["purchase.order.group"].create(po_group_vals_list)


@openupgrade.migrate()
def migrate(env, version):
    _fill_purchase_order_group(env)
    openupgrade.delete_records_safely_by_xml_id(
        env,
        ["purchase_requisition.seq_purchase_tender", "purchase_requisition.type_multi"],
    )
