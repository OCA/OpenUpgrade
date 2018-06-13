#!/usr/bin/python
import psycopg2
import sys
import getopt


def help_message():
    print('''pre-migration.py -- uses getopt to recognize options
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


def pre_install_modules(conn, cr):
    for module in ["database_cleanup"]:
        cr.execute("""
            SELECT id
            FROM ir_module_module
            WHERE name='%s'""" % module)
        if cr.fetchall():
            continue
        cr.execute("""
            INSERT INTO ir_module_module (name, state)
            VALUES ('%s', 'to install')
        """ % module)


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

    pre_install_modules(conn, cr)


if __name__ == "__main__":
    main()
