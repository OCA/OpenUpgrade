# -*- encoding: utf-8 -*-
from turbogears.database import PackageHub
# import some basic SQLObject classes for declaring the data model
# (see http://www.sqlobject.org/SQLObject.html#declaring-the-class)
from sqlobject import SQLObject, SQLObjectNotFound, RelatedJoin
# import some datatypes for table columns from SQLObject
# (see http://www.sqlobject.org/SQLObject.html#column-types for more)
from sqlobject import StringCol, UnicodeCol, IntCol, DateTimeCol

__connection__ = hub = PackageHub('livechat')


# your data model


# class YourDataClass(SQLObject):
#     pass


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

