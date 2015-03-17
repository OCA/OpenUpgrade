Development FAQ
+++++++++++++++

How are new dependencies treated by the Odoo migration manager?
   New dependencies (like the *edi* module is a new dependency of the
   *account* module) will be detected by the upgrade process.  The
   Odoo server code is slightly modified to loop over this part
   of the process to install new dependencies and then return to
   upgrading the modules that depend on them, until no more modules
   are processed.

Are migration scripts fired when installing new modules?
   Yes.  That includes any new dependencies that the new version of any
   module might declare.  You might want to check for a non true value
   of the *version* argument, or (better) make your script robust to
   running against a database that it does not apply to, in anticipation
   of any unknown unknowns.  Also another argument for not running the
   OpenUpgrade server in production, even though we both know that you
   would never ever do so anyway.
