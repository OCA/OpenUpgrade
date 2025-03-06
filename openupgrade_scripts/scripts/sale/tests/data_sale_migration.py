env = locals().get("env")
# set sale order to done to be sure we migrate
# the done state correctly
env.ref("sale.sale_order_18").action_done()
env.cr.commit()
