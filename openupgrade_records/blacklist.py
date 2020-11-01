BLACKLIST_MODULES = [
    # the hw_* modules are not affected by a migration as they don't
    # contain any ORM functionality, but they do start up threads that
    # delay the process and spit out annoying log messages continously.
    "hw_drivers",
    "hw_escpos",
    "hw_posbox_homepage",
    # Modules that seems bugged
    "l10n_bo",
    # Doesn't have sense to analyse this module that contains patches
    "openupgrade_framework",
]
