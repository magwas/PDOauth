from pdoauth.models.Credential import Credential
from urllib import urlencode
from test.helpers.todeprecate.UserTesting import UserTesting
from test.helpers.PDUnitTest import PDUnitTest, test

from test.config import Config
testuserIdentifier = "06:11:50:AC:71:A4:CE:43:0F:62:DC:D2:B4:F0:2A:1C:31:4B:AB:E2/CI Test User"
testCredentialRepresentation = '{{"credentialType": "certificate", "identifier": "{0}"}}'.format(testuserIdentifier)

class SSLLoginTest(PDUnitTest, UserTesting):

    def tearDown(self):
        PDUnitTest.tearDown(self)
        self.removeCertUser()

    @test
    def there_is_a_SSL_LOGIN_BASE_URL_config_option_containing_the_base_url_of_the_site_with_the_optional_no_ca_config(self):
        self.assertTrue(Config.SSL_LOGIN_BASE_URL is not None)

    @test
    def there_is_a_BASE_URL_config_option_containing_the_plain_ssl_base_url(self):
        "where no certificate is asked"
        self.assertTrue(Config.BASE_URL is not None)

    @test
    def there_is_a_SSL_LOGOUT_URL_config_option_pointing_to_a_location_which_is_set_up_with_SSLVerifyClient_require_and_SSLVerifyDepth_0_within_SSL_LOGIN_BASE_URL(self):
        self.assertTrue(Config.SSL_LOGIN_BASE_URL in Config.SSL_LOGOUT_URL)
    
    @test
    def there_is_a_START_URL_config_option_which_contains_the_starting_point_useable_for_unregistered_and_or_not_logged_in_user(self):
        self.assertTrue(Config.BASE_URL in Config.START_URL)

    @test
    def you_can_login_using_a_registered_ssl_cert(self):
        resp = self.createUserAndLoginWithCert()
        self.assertEquals(resp.status_code, 200)
        self.assertTrue(testCredentialRepresentation in
            self.getResponseText(resp))

    @test
    def with_cert_login_you_get_actually_logged_in(self):
        resp = self.createUserAndLoginWithCert()
        self.assertEquals(resp.status_code, 200)
        body = self.getResponseText(resp)
        self.assertTrue(testCredentialRepresentation in
            body)
        resp = self.showUserByCurrentUser('me')
        self.assertEqual(200, resp.status_code)

    @test
    def you_cannot_login_using_an_unregistered_ssl_cert_without_email(self):
        identifier, digest, cert = self.getCertAttributes()  # @UnusedVariable
        self.assertReportedError(self.sslLoginWithCert, [cert], 403, ["You have to register first"])

    @test
    def you_cannot_login_without_a_cert(self):
        self.assertReportedError(self.controller.do_ssl_login, [], 403, ["No certificate given"])

    @test
    def empty_certstring_gives_error(self):
        self.assertReportedError(self.sslLoginWithCert, [''], 403, ["No certificate given"])

    @test
    def junk_certstring_gives_error(self):
        self.assertReportedError(self.sslLoginWithCert, ['junk'], 400, ["error in cert", "junk"])

    @test
    def ssl_login_is_cors_enabled(self):
        resp = self.createUserAndLoginWithCert()
        self.assertEquals(resp.status_code, 200)
        self.assertEqual(resp.headers['Access-Control-Allow-Origin'], "*")

    def removeCertUser(self):
        cred = Credential.get('certificate', testuserIdentifier)
        if cred:
            cred.rm()
            cred.user.rm()

    @test
    def you_can_register_and_login_using_an_unregistered_ssl_cert_with_email(self):
        identifier, digest, cert = self.getCertAttributes()  # @UnusedVariable
        params=dict(email="certuser@example.com")
        self.controller._testdata.request_url = Config.BASE_URL+"?"+urlencode(params)
        resp = self.sslLoginWithCert(cert)
        cred = Credential.get("certificate", identifier)
        self.deleteUser(cred.user)
        self.assertEquals(resp.status_code, 200)
        responseText = self.getResponseText(resp)
        self.assertTrue(testCredentialRepresentation in
            responseText)
        self.assertTrue('{"credentialType": "emailcheck", "identifier":' in
            responseText)

    @test
    def when_you_log_in_with_a_cert_login_credential_gets_set(self):
        identifier, digest, cert = self.getCertAttributes()  # @UnusedVariable
        params=dict(email="certuser@example.com")
        self.controller._testdata.request_url = Config.BASE_URL+"?"+urlencode(params)
        resp = self.sslLoginWithCert(cert)
        self.assertEquals(resp.status_code, 200)
        sessionLoginCredential = self.controller.getSession()[self.controller.LOGIN_CREDENTIAL_ATTRIBUTE]
        self.assertEqual(sessionLoginCredential['credentialType'],'certificate')
        self.assertEqual(sessionLoginCredential['identifier'],testuserIdentifier)