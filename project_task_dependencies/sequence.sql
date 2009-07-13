/*
must be executed manualy after module install
because 
a) create or replace trigger is not supported in 8.2
b) drop trigger causes module loading to fail if trigger does not exist
*/

CREATE FUNCTION project_task_sequences() RETURNS VOID  AS
$$
BEGIN
/*
inititalize with steps of 10
*/
update project_task set sequence = 10;
/*
loop unless all dependencies on levels have been updated
*/
     LOOP 
               update project_task t set sequence = (select max(sequence) + 10 
                                        from project_task p, 
                                             project_task_rel r
                                       where r.next_task_id  = t.id
                                         and r.prior_task_id = p.id)
                where id in (select next_task_id from project_task_rel)
                  and sequence != (select max(sequence) + 10 
                                        from project_task p, 
                                             project_task_rel r
                                       where r.next_task_id  = t.id
                                         and r.prior_task_id = p.id) ;

            IF not found THEN
                RETURN;
            END IF;
        
    END LOOP;
END;
$$
LANGUAGE plpgsql;


/* 
select * from project_task_sequences();
*/

/*
Create trigger construct
*/


create or replace function trg_funct_project_task_sequences() RETURNS trigger as 
$$
BEGIN
execute project_task_sequences();
return new;
END;
$$
LANGUAGE plpgsql;

drop trigger trg_project_task_sequences
ON  project_task_rel;

create trigger trg_project_task_sequences
AFTER INSERT OR UPDATE OR DELETE ON  project_task_rel
    FOR EACH ROW EXECUTE PROCEDURE trg_funct_project_task_sequences();
