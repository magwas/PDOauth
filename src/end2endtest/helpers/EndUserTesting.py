#pylint: disable=unused-import, line-too-long, too-many-arguments
from integrationtest.helpers.UserTesting import UserTesting
from twatson.unittest_annotations import Fixture, test  # @UnusedImport
from end2endtest.helpers.BrowserSetup import BrowserSetup
from end2endtest import config
import time
import assurancetool

class EndUserTesting(Fixture, UserTesting, BrowserSetup):
    def setUp(self):
        self.setupDriver()
        self.baseUrl = config.Config.BASE_URL
        self.verificationErrors = []

    def fillInAndSubmitRegistrationForm(self, driver, email=None, userid=None, password=None, digest=None):
        if email is None:
            email=self.userCreationEmail
        if userid is None:
            userid=self.userCreationUserid
        if password is None:
            password=self.usercreationPassword
        if digest is None:
            digest = self.createHash()
        self.switchToTab('registration')
        driver.find_element_by_id("RegistrationForm_digest_input").clear()
        if digest is not False:
            driver.find_element_by_id("RegistrationForm_digest_input").send_keys(digest)
        driver.find_element_by_id("RegistrationForm_identifier_input").clear()
        driver.find_element_by_id("RegistrationForm_identifier_input").send_keys(userid)
        driver.find_element_by_id("RegistrationForm_secret_input").clear()
        driver.find_element_by_id("RegistrationForm_secret_input").send_keys(password)
        driver.find_element_by_id("RegistrationForm_email_input").clear()
        driver.find_element_by_id("RegistrationForm_email_input").send_keys(email)
        driver.find_element_by_id("RegistrationForm_submitButton").click()


    def loginAsAssurer(self, driver):
        driver.get(self.baseUrl + "/static/login.html?next=/v1/users/me")
        self.setupUserCreationData()
        self.assurer = self.userCreationUserid
        self.assurerEmail = self.userCreationEmail
        self.fillInAndSubmitRegistrationForm(driver, password=self.usercreationPassword, userid=self.assurer, email=self.assurerEmail)
        time.sleep(1)
        assurancetool.do_main(0, self.assurerEmail, 'self', ["assurer", "assurer.test"])

