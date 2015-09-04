Run your own analysis
=====================

1. First you need to prepare your Python environment by installing the appropriate release of openupgradelib_.
.. _openupgradelib: https://github.com/OCA/openupgradelib/releases

2. In order to analyse the difference of two codebases you need to specially prepare your different codebases by applying this OpenUpgrade patch onto your Odoo code-base. (Note@ProjectLeader: Please provide patches towards OCA/OCB and standard Odoo for different versions) This will add some folders of the OpenUpgrade tool suite and modify some Odoo core files in order to work smoothly with OpenUpgrade.

3. Then create empty databases, even without demo data: one on top of the new code, the other on top of the old code.

4. Then install the modules you want to take into account on both databases. Also, install the module *openupgrade_records* on both databases.

5. If you have obvious changes in module or model names and you do not want your analyse output to be cluttered, include this mapping in the 'apripri.py'_ 
.. _'apriori.py': https://github.com/OCA/OpenUpgrade/tree/8.0/openerp/addons/openupgrade_records/lib

6. On both instances: from the development menu, select the *Generate Records* option.

7. On the new (target) database, from the OpenUpgrade Development menu, set the server connection to your old (source) database in the "Comparison Config" menu. Test the connection with the appropriate button.

8. Make sure, that the Odoo user has writing rights in the folders of your target database's source code.

9. In the target instance, in the *Comparison Config* form, click on *Perform Analysis*. This will create 'openupgrade_analisis.txt' files in the (newly created) migrations subfolders of each of your installed modules on your target source code. It will also create an 'openupgrade_general_log.txt' in the appropriate 'migrations' subfolder of the 'base' module.

Read on in the docs on how to create migration scrips from those analyse files.

Note that in many of the operations above you may get a client timeout or a concurrent access error even if the operation completes successfully. You should be able to ascertain a successful operation by verifying that all modules involved are in an installed state and the analysis files in the module directories have an appropriate modification time.
