Development FAQ
+++++++++++++++

How are new dependencies treated by the OpenERP migration manager?
   New dependencies (like the *edi* module is a new dependency of the
   *account* module) will be marked for installation on the first upgrade
   run. The upgrade of the original module will halt at that point due to
   the 'missing dependency'. This means that you will have to run the 
   upgrade step again (and again...) until all dependencies have been
   resolved. It also means that at least your *pre-scripts* need to be
   tolerant to being run twice on the same database.
