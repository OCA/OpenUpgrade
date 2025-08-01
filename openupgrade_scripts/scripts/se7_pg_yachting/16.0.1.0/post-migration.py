from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.update_module_names(
        env.cr,
        [("se7_pg_adaptacion_proyectos", "se7_pg_yachting")],
    )
    
    openupgrade.logged_query(
        env.cr,
        """
        update account_move_line
        set boat_project_id = (select project_id from account_invoice_line where id = old_invoice_line_id);

        update account_move_line
        set boat_area_id = (select yacht_area from account_invoice_line where id = old_invoice_line_id);

        update account_move_line
        set billable_to_customer = (select billable_to_customer
                                    from account_invoice_line
                                    where id = old_invoice_line_id);



        update account_move_line
        set description_for_customs = (select description_for_customs
                                       from account_invoice_line
                                       where id = old_invoice_line_id);

        update account_move_line
        set quantity_to_invoice = (select quantity_to_invoice from account_invoice_line where id = old_invoice_line_id);

        update account_move_line
        set sale_price_unit = (select sale_price_unit from account_invoice_line where id = old_invoice_line_id);

        update account_move_line
        set commission = (select commission from account_invoice_line where id = old_invoice_line_id);



        update account_move_line
        set commission_already_paid = (select commission_already_paid
                                       from account_invoice_line
                                       where id = old_invoice_line_id);



        update account_move_line
        set commission_move_line_id = (select id
                                       from account_move_line

                                       where old_invoice_line_id = (select commission_line_id
                                                                    from account_invoice_line
                                                                    where id = old_invoice_line_id));



        update account_move
        set boat_project_id = (select project_id from account_invoice where id = old_invoice_id);



        insert into in_out_account_move_line_rel

            (select sl.id as sale_id, pl.id as purchase_id

             from invoice_sale_purchase_line_rel ot

                      join account_move_line sl on ot.sale_line_id = sl.old_invoice_line_id

                      join account_move_line pl on ot.purchase_line_id = pl.old_invoice_line_id);
        """)



