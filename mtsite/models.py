class User(UserMixin):

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def get_totp_uri(self):
        return 'otpauth://totp/MT-2FA:{0}?secret={1}&issuer=MT-2FA'.format(self.username, self.otp_secret)

    def verify_totp(self, token):
        return onetimepass.valid_totp(token, self.otp_secret)

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return self.authenticated

    def is_active(self):
        return self.active

    def get_id(self):
        return self.id


