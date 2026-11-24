The odoo_patch folder contains python files in a tree that mimicks the
folder tree of the Odoo project. It contains a number of monkey patches
to improve the migration of an Odoo database between two major versions.

So far, we are able to make everything work without overwriting large
blocks of code, but if larger patches need to be added, please use the
method described below:

To see the patches added, you can use `meld` tools:

`meld PATH_TO_ODOO_FOLDER/odoo/ PATH_TO_OPENUPGRADE_FRAMEWORK_MODULE/odoo_patch`

To make more easy the diff analysis :

- Make sure the python files has the same path as the original one.
- Keep the same indentation as the original file. (using `if True:` if
  required)
- Add the following two lines at the beginning of your file, to avoid
  flake8 / pylint errors

``` python
# flake8: noqa
# pylint: skip-file
```

- When you want to change the code. add the following tags:

For an addition:

``` python
# <OpenUpgrade:ADD>
some code...
# </OpenUpgrade>
```

For a change:

``` python
# <OpenUpgrade:CHANGE>
some code...
# </OpenUpgrade>
```

For a removal:

``` python
# <OpenUpgrade:REMOVE>
# Comment the code, instead of removing it.
# </OpenUpgrade>
```
