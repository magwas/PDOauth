# pylint: disable=line-too-long
from test.helpers.PDUnitTest import PDUnitTest, test
from test.helpers.UserUtil import UserUtil
from test.helpers.FakeInterFace import FakeInterface, FakeMail, FakeApp
from pdoauth.EmailHandling import EmailHandling
from pdoauth.models.Credential import Credential
from pdoauth.models import User
from smtplib import SMTPException
from pdoauth.ReportedError import ReportedError
from pdoauth.Messages import exceptionSendingEmail

exampleBody = """Dear abc@xyz.uw,
This is a reset email.
Go to https://local.sso.edemokraciagep.org:8888/static/login.html?secret=th1s1sth4s3cret
you have to do it until 11 Dec 2098 12:34:56.

Sincerely,
The Test machine
"""

exampleHtml = """<html><head></head><body>
Dear abc@xyz.uw,<br>
This is a reset email.<br/>
Click <a href="https://local.sso.edemokraciagep.org:8888/static/login.html?secret=th1s1sth4s3cret">Click</a><br/>
you have to do it until 11 Dec 2098 12:34:56.<br/>
<br/>
Sincerely,<br/>
The Test machine
</body></html>
"""

class TestMailer(EmailHandling, FakeInterface):
    app = FakeApp()
    mail = FakeMail()

class FailingMail(FakeMail):
    def send(self,msg):
        raise SMTPException('some smtp error')

class FailingMailer(EmailHandling, FakeInterface):
    app = FakeApp()
    mail = FailingMail()

class EmailTest(PDUnitTest, UserUtil):

    def setUp(self):
        self.mailer = TestMailer()
        self.failingMailer = FailingMailer()
        cred = self.createUserWithCredentials()
        self.user = cred.user

    @test
    def email_is_formatted_correctly(self):
        self.user.email='abc@xyz.uw'
        self.mailer.sendEmail(self.user, 'th1s1sth4s3cret', 4069139696, 'PASSWORD_RESET')
        message = self.mailer.mail.outbox[0]
        self.assertEqual(message.body,exampleBody);
        self.assertEqual(message.html,exampleHtml);
        self.user.rm()

    @test
    def password_reset_email_subject_is_PASSWORD_RESET_EMAIL_SUBJECT(self):
        self.mailer.sendPasswordResetMail(self.user)
        self.assertSubjectIs("password reset")

    @test
    def password_reset_email_body_is_DEREGISTRATION_EMAIL_BODY(self):
        self.mailer.sendPasswordResetMail(self.user)
        self.assertGotAnEmailContaining("This is a reset email")

    @test
    def password_reset_email_body_contains_user(self):
        self.mailer.sendPasswordResetMail(self.user)
        self.assertGotAnEmailContaining(self.user.email)

    @test
    def password_reset_email_body_contains_secret(self):
        self.mailer.sendPasswordResetMail(self.user)
        cred = Credential.getByUser(self.user,"email_for_password_reset")
        self.assertGotAnEmailContaining(cred.secret)

    @test
    def password_verification_email_subject_is_PASSWORD_VERIFICATION_EMAIL_SUBJECT(self):
        self.mailer.sendPasswordVerificationEmail(self.user)
        self.assertSubjectIs("verification")

    @test
    def password_verification_email_body_is_DEREGISTRATION_EMAIL_BODY(self):
        self.mailer.sendPasswordVerificationEmail(self.user)
        self.assertGotAnEmailContaining("This is a verification email")

    @test
    def password_verification_email_body_contains_user(self):
        self.mailer.sendPasswordVerificationEmail(self.user)
        self.assertGotAnEmailContaining(self.user.email)

    @test
    def password_verification_email_body_contains_secret(self):
        self.mailer.sendPasswordVerificationEmail(self.user)
        cred = Credential.getByUser(self.user,"emailcheck")
        self.assertGotAnEmailContaining(cred.secret)

    @test
    def deregistration_email_subject_is_DEREGISTRATION_EMAIL_SUBJECT(self):
        self.mailer.sendDeregisterMail(self.user)
        self.assertSubjectIs("deregistration email")

    @test
    def deregistration_email_body_is_DEREGISTRATION_EMAIL_BODY(self):
        self.mailer.sendDeregisterMail(self.user)
        self.assertGotAnEmailContaining("This is a deregistration email")

    @test
    def deregistration_email_body_contains_user(self):
        self.mailer.sendDeregisterMail(self.user)
        self.assertGotAnEmailContaining(self.user.email)

    @test
    def deregistration_email_body_contains_secret(self):
        self.mailer.sendDeregisterMail(self.user)
        cred = Credential.getByUser(self.user,"deregister")
        self.assertGotAnEmailContaining(cred.secret)

    @test
    def verification_email_smtp_error_throws_ReportedError_and_removes_user(self):
        email = self.user.email
        with self.assertRaises(ReportedError):
            self.failingMailer.sendPasswordVerificationEmail(self.user)
        self.assertEqual(None, User.getByEmail(email))

    @test
    def password_reset_email_smtp_error_throws_ReportedError(self):
        email = self.user.email
        with self.assertRaises(ReportedError):
            self.failingMailer.sendPasswordResetMail(self.user)
        self.assertEqual(email, User.getByEmail(email).email)

    @test
    def deregistration_email_smtp_error_throws_ReportedError(self):
        email = self.user.email
        with self.assertRaises(ReportedError):
            self.failingMailer.sendDeregisterMail(self.user)
        self.assertEqual(email, User.getByEmail(email).email)

    @test
    def ReportedError_contains_localizable_message_and_original_error(self):
        with self.assertRaises(ReportedError) as context:
            self.failingMailer.sendDeregisterMail(self.user)
        
        self.assertEqual(context.exception.descriptor,
            exceptionSendingEmail.format('some smtp error'))  # @UndefinedVariable
        
    def tearDown(self):
        self.mailer.mail.outbox=list()
        user = User.getByEmail('abc@xyz.uw')
        if user:
            user.rm()