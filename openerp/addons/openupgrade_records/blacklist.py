BLACKLIST_MODULES = [
    # l10n_be cannot be reinstalled as the module's yaml data installs
    # the chart of accounts at installation time, and the other modules
    # depend on this module and the chart installation itself.
    'l10n_be',
    'l10n_be_intrastat',
    'l10n_be_hr_payroll_account',
    # the hw_* modules are not affected by a migration as they don't
    # contain any ORM functionality, but they do start up threads that
    # delay the process and spit out annoying log messages continously.
    'hw_escpos',
    'hw_proxy',
    'hw_scale',
    'hw_scanner',
]
