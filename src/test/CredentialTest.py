from test.helpers.PDUnitTest import PDUnitTest, test
from test.helpers.FakeInterFace import FakeForm
from Crypto.Hash.SHA256 import SHA256Hash
from pdoauth.models.Credential import Credential
from test.helpers.UserUtil import UserUtil

class CredentialTest(PDUnitTest, UserUtil):

    def setUp(self):
        self.user = self.createUserWithCredentials()
        self.cred=Credential.get('password', self.userCreationUserid)
        PDUnitTest.setUp(self)
        
    @test
    def Credential_representation_is_readable(self):
        secretdigest=SHA256Hash(self.usercreationPassword).hexdigest()
        representation = "Credential(user={0},credentialType=password,identifier={2},secret={1})".format(
            self.userCreationEmail,
            secretdigest,
            self.userCreationUserid)
        self.assertEquals("{0}".format(self.cred),representation)

    @test
    def a_logged_in_user_can_add_credential(self):
        resp = self._createPasswordCredential()
        self.assertEqual(resp.status_code, 200)

    @test
    def when_a_credential_is_added_the_response_contains_user_data_which_contains_her_credentials(self):
        resp = self._createPasswordCredential()
        self.assertEqual(resp.status_code, 200)
        text = self.getResponseText(resp)
        self.assertTrue(self.userCreationUserid in text)

    @test
    def the_credential_is_actually_added(self):
        myUserid = self.createRandomUserId()
        credBefore = Credential.get("password", myUserid)
        self.assertTrue(credBefore is None)
        resp = self._createPasswordCredential(userid=myUserid)
        self.assertEqual(200, resp.status_code)
        credAfter = Credential.get("password", myUserid)
        self.assertTrue(credAfter is not None)

    @test
    def a_credential_can_be_deleted(self):
        myUserid = self.createRandomUserId()
        resp = self._removeACredential(myUserid)
        self.assertEqual(200, resp.status_code)
        self.assertEqual('{"message": "credential removed"}', self.getResponseText(resp))

    def _removeACredential(self, myUserid):
        self.controller.loginInFramework(self.cred)
        user = self.cred.user
        Credential.new(user, "facebook", myUserid, "testsecret")
        data = {"credentialType":"facebook", 
            "identifier":myUserid}
        self.assertTrue(Credential.get("facebook", myUserid))
        resp = self.controller.doRemoveCredential(FakeForm(data))
        return resp

    @test
    def password_is_stored_using_sha256_hash(self):
        resp = self._createPasswordCredential()
        self.assertEqual(resp.status_code, 200)
        cred = Credential.get('password', self.userCreationUserid)
        self.assertEqual(cred.secret, SHA256Hash(self.usercreationPassword).hexdigest())


    def _createPasswordCredential(self, userid=None):
        self.controller.loginInFramework(self.cred)
        self.setupUserCreationData()
        if userid is None:
            userid = self.userCreationUserid
        form = FakeForm(dict(credentialType='password', identifier=userid, secret=self.usercreationPassword))
        resp = self.controller.doAddCredential(form)
        return resp

    @test
    def an_already_existing_credential_cannot_be_addedd(self):
        self.createUserWithCredentials(userid="existinguser")
        self.assertReportedError(self.createUserWithCredentials, ['password', 'existinguser'], 400, 'Already existing credential')
        cred = Credential.get("password", "existinguser")
        cred.rm()

    @test
    def the_credential_used_for_login_cannot_be_cleared(self):
        credential = self.createUserWithCredentials()
        self.controller.loginInFramework(credential)
        self.assertTrue(Credential.get("password", self.userCreationUserid))
        form = FakeForm({
            "identifier": self.userCreationUserid,
            "credentialType": "password",
        })
        self.assertReportedError(self.controller.doRemoveCredential,[form], 400, ["You cannot delete the login you are using"])
        self.assertTrue(Credential.get("password", self.userCreationUserid))
