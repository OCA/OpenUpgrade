from lxml import etree

env = locals().get("env")

# comparison saved by 14.0 in the dashboard action context: the 16.0 client
# does not understand it, see post-migration.py
comparison = {
    "comparisonId": "previous_year",
    "fieldName": "create_date",
    "fieldDescription": "Created on",
    "range": "['&', ['create_date', '>=', '2023-01-01 00:00:00'], "
    "['create_date', '<=', '2023-12-31 23:59:59']]",
    "rangeDescription": "2023",
    "comparisonRange": "['&', ['create_date', '>=', '2022-01-01 00:00:00'], "
    "['create_date', '<=', '2022-12-31 23:59:59']]",
    "comparisonRangeDescription": "2022",
}
action = env.ref("base.action_partner_form")
root = etree.Element("form", string="My Dashboard")
board = etree.SubElement(root, "board", style="1-1")
column = etree.SubElement(board, "column")
etree.SubElement(
    column,
    "action",
    name=str(action.id),
    string="OpenUpgrade Test Dashboard",
    view_mode="graph",
    domain="[('is_company', '=', True)]",
    context=repr(
        {
            "group_by": ["create_date:month"],
            "comparison": comparison,
            "dashboard_merge_domains_contexts": False,
        }
    ),
)
etree.SubElement(
    column,
    "action",
    name=str(action.id),
    string="OpenUpgrade Test Dashboard No Comparison",
    view_mode="graph",
    domain="[]",
    context=repr({"group_by": ["create_date:month"]}),
)
env["ir.ui.view.custom"].create(
    {
        "ref_id": env.ref("board.board_my_dash_view").id,
        "user_id": env.uid,
        "arch": etree.tostring(root, encoding="unicode"),
    }
)
env.cr.commit()
