To be done:
-----------

* Test to not create several times the same file / directory
  -> May be put a sql_constraints uniq on several files
  -> test through remove or put

* Change so that if several directories point to the same linked ressource,
  it opens the same files. Root of ressources are those where parent_id=False
  and res_id=RESSOURCE_ID.

  Sales Order/SO001/Test
  Sales By PArtner/AsusTek/SO001/Test

  -> Not sure about that, to be verified. How to manage: template dirs ?

* Retest everything
