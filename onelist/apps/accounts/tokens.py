import sys
import hmac
import hashlib
from datetime import date
from flask import current_app, g
from onelist.apps.accounts.models import UserModel

class PasswordResetTokenGenerator(object):

    def make_token(self, user):
        """Returns a token that can be used once to do a password reset for the
        given user.
        """
        return self._make_token_with_timestamp(user, self._num_days(date.today()))


    def constant_time_compare(self, val1, val2):
        """Returns True if the two strings are equal, False otherwise.

        The time taken is independent of the number of characters that match.
        """
        if len(val1) != len(val2):
            return False
        result = 0
        for x, y in zip(val1, val2):
            result |= ord(x) ^ ord(y)
        return result == 0


    def check_token(self, token):
        """
        Check that a password reset token is correct for a given user.
        """
        # Parse the token
        try:
            user_id_base36, timestamp_base36, code = token.split('-')
        except ValueError:
            return False

        # Extract and get the user
        try:
            user_id = self.base36_to_int(user_id_base36)
            user = g.User.get(id=user_id)
        except ValueError:
            return False

        # Extract the timestamp
        try:
            ts = self.base36_to_int(timestamp_base36)
        except ValueError:
            return False

        # Check that the timestamp/uid has not been tampered with
        if not self.constant_time_compare(self._make_token_with_timestamp(user, ts), token):
            return False

        # Check the timestamp is within limit
        if (self._num_days(date.today()) - ts) > current_app.config['PASSWORD_RESET_DAYS']:
            return False

        return user


    def salted_hmac(self, key_salt, value, secret=None):
        """
        Returns the HMAC-SHA1 of 'value', using a key generated from key_salt and a
        secret (which defaults to settings.SECRET_KEY).

        A different key_salt should be passed in for every application of HMAC.
        """
        # if secret is None:
        #     secret = settings.SECRET_KEY
        # secret = 'OTCOOLqPN6tWyIvVT40hUuslz7UXgwg5cW664RcR0YuEmGu6ip1Pm68PtzeAnFw'

        # We need to generate a derived key from our base key.  We can do this by
        # passing the key_salt and our base key through a pseudo-random function and
        # SHA1 works nicely.
        key = hashlib.sha1(key_salt + current_app.config['SECRET_KEY']).digest()

        # If len(key_salt + secret) > sha_constructor().block_size, the above
        # line is redundant and could be replaced by key = key_salt + secret, since
        # the hmac module does the same thing for keys longer than the block size.
        # However, we need to ensure that we *always* do this.

        return hmac.new(key, msg=value, digestmod=hashlib.sha1)


    def _make_token_with_timestamp(self, user, timestamp):
        # timestamp is number of days since 2001-1-1.  Converted to
        # base 36, this gives us a 3 digit string until about 2121
        ts_b36 = self.int_to_base36(timestamp)

        # By hashing on the internal state of the user and using state
        # that is sure to change (the password salt will change as soon as
        # the password is set), we produce a hash that will be
        # invalid as soon as it is used.
        # We limit the hash to 20 chars to keep URL short
        key_salt = "onelist.apps.accounts.tokens.PasswordResetTokenGenerator"
        value = unicode(user.id) + user.password + unicode(timestamp)
        hash = self.salted_hmac(key_salt, value).hexdigest()[::2]
        return "%s-%s-%s" % (self.int_to_base36(user.id), ts_b36, hash)


    def _num_days(self, dt):
        return (dt - date(2001,1,1)).days


    def int_to_base36(self, i):
        """Converts an integer to a base36 string
        """
        digits = "0123456789abcdefghijklmnopqrstuvwxyz"
        factor = 0
        # Find starting factor
        while True:
            factor += 1
            if i < 36 ** factor:
                factor -= 1
                break
        base36 = []
        # Construct base36 representation
        while factor >= 0:
            j = 36 ** factor
            base36.append(digits[i / j])
            i = i % j
            factor -= 1
        return ''.join(base36)


    def base36_to_int(self, s):
        """Converts a base 36 string to an ``int``. Raises ``ValueError` if the
        input won't fit into an int.
        """
        # To prevent overconsumption of server resources, reject any
        # base36 string that is long than 13 base36 digits (13 digits
        # is sufficient to base36-encode any 64-bit integer)
        if len(s) > 13:
            raise ValueError("Base36 input too large")
        value = int(s, 36)
        # ... then do a final check that the value will fit into an int.
        if value > sys.maxint:
            raise ValueError("Base36 input too large")
        return value


token_generator = PasswordResetTokenGenerator()