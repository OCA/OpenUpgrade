
class authorizer:
    read_perms = "elr"
    write_perms = "adfmw"

    def __init__(self):
        self.user_table = {}

    def validate_authentication(self, username, password):
        """Return True if the supplied username and password match the
        stored credentials."""
        return True

    def impersonate_user(self, username, password):
        """Impersonate another user (noop).

        It is always called before accessing the filesystem.
        By default it does nothing.  The subclass overriding this
        method is expected to provide a mechanism to change the
        current user.
        """

    def terminate_impersonation(self):
        """Terminate impersonation (noop).

        It is always called after having accessed the filesystem.
        By default it does nothing.  The subclass overriding this
        method is expected to provide a mechanism to switch back
        to the original user.
        """

    def has_user(self, username):
        """Whether the username exists in the virtual users table."""
        return True

    def has_perm(self, username, perm, path=None):
        """Whether the user has permission over path (an absolute
        pathname of a file or a directory).

        Expected perm argument is one of the following letters:
        "elradfmw".
        """
        return True

    def get_perms(self, username):
        """Return current user permissions."""
        return 'elr'

    def get_home_dir(self, username):
        """Return the user's home directory."""
        return '/'

    def get_msg_login(self, username):
        """Return the user's login message."""
        return 'Welcome on OpenERP document management system.'

    def get_msg_quit(self, username):
        """Return the user's quitting message."""
        return 'Bye.'


