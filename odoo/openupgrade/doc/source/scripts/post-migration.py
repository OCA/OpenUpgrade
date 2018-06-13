#!/usr/bin/python
import psycopg2
import sys
import getopt


def help_message():
    print('''post-migration.py -- uses getopt to recognize options
Options: -h      -- displays this help message
       --db_name= -- the name of the database
       --db_user=  -- user to execute the sql sentences
       --db_password= --password to execute the sql sentences
       --db_host= --host for connection (optional)
       --db_port= --port for connection (optional)''')
    sys.exit(0)


try:
    options, xarguments = getopt.getopt(sys.argv[1:], 'h',
                                        ['db_name=',
                                         'db_user=', 'db_password=', 'db_host=', 'db_port='])
except getopt.error:
    print('Error: You tried to use an unknown option or the argument for an '
          'option that requires it was missing. Try pre-migration.py -h\' '
          'for more information.')
    sys.exit(0)

for a in options[:]:
    if a[0] == '--db_name' and a[1] != '':
        db_name = a[1]
        options.remove(a)
        break
    elif a[0] == '--db_name' and a[1] == '':
        print('--db_name expects an argument')
        sys.exit(0)

for a in options[:]:
    if a[0] == '--db_user' and a[1] != '':
        db_user = a[1]
        options.remove(a)
        break
    elif a[0] == '--db_user' and a[1] == '':
        print('--db_user expects an argument')
        sys.exit(0)

db_password = False
for a in options[:]:
    if a[0] == '--db_password' and a[1] != '':
        db_password = a[1]
        options.remove(a)
        break

db_host = False
for a in options[:]:
    if a[0] == '--db_host' and a[1] != '':
        db_host = a[1]
        options.remove(a)
        break

db_port = False
for a in options[:]:
    if a[0] == '--db_port' and a[1] != '':
        db_port = a[1]
        options.remove(a)
        break


def disable_inherit_unported_modules(conn, cr):
    print("""defuse inheriting views originating from
    not yet ported modules""")
    cr.execute("""
        UPDATE ir_ui_view
        SET arch_db='<data/>'
        WHERE id in (
            SELECT iuv.id
            FROM ir_ui_view as iuv
            INNER JOIN ir_model_data as imd
            ON iuv.id = imd.res_id
            INNER JOIN ir_module_module as imm
            ON imd.module = imm.name
            WHERE imm.state <> 'installed'
            AND imd.model = 'ir.ui.view')
    """)
    conn.commit()


def set_not_ported_modules_to_installed(conn, cr):
    print("""set not yet ported modules to installed
    (otherwise, updating a module to work on becomes tricky)""")

    cr.execute("""
        UPDATE ir_module_module
        SET state='installed'
        WHERE state IN ('to install', 'to upgrade')
    """)
    conn.commit()


def main():
    # Define our connection string
    conn_string = """dbname=%s user=%s
    password=%s host=%s port=%s""" % (db_name, db_user, db_password, db_host, db_port)

    # print the connection string we will use to connect
    print("Connecting to database\n    ->%s", conn_string)

    # get a connection, if a connect cannot be made an exception
    # will be raised here
    conn = psycopg2.connect(conn_string)

    # conn.cursor will return a cursor object, you can use this cursor
    # to perform queries
    cr = conn.cursor()
    print("Connected!\n")

    disable_inherit_unported_modules(conn, cr)
    set_not_ported_modules_to_installed(conn, cr)


if __name__ == "__main__":
    main()
