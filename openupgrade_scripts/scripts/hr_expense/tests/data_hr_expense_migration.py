env = locals().get("env")
env.ref("hr_expense.team_building_sheet").action_submit_sheet()
env.ref("hr_expense.office_furniture_sheet").action_submit_sheet()
env.ref("hr_expense.office_furniture_sheet").action_approve_expense_sheets()
env.ref("hr_expense.lunch_demo_customer_bill_expense").product_id = env.ref(
    "hr_expense.expense_product_gift"
)
env.ref("hr_expense.customer_meeting_sheet").action_submit_sheet()
env.ref("hr_expense.customer_meeting_sheet").action_approve_expense_sheets()
env.ref("hr_expense.customer_meeting_sheet").action_sheet_move_post()
action = env.ref("hr_expense.customer_meeting_sheet").action_register_payment()
wizard = env[action["res_model"]].with_context(**action["context"]).create({})
wizard.action_create_payments()
env.cr.commit()
