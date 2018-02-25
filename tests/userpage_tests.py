import os

from django.test import LiveServerTestCase
from selenium import webdriver

'''
class UserPageTest(StaticLiveServerTestCase):

    browser = None

    @classmethod
    def set_up_class(cls):
        super(UserPageTest, cls).setUpClass()
        cls.browser = webdriver.PhantomJs()
        cls.username = os.environ.get('username', '')
        cls.password = os.environ.get('password', '')

    @classmethod
    def tear_down_class(cls):
        cls.browser.quit()
        super(UserPageTest, cls).tear_down_class()

    def test_bind_user(self):
        self.browser.get('%s%s' % (self.live_server_url, '/u/bind'))

        name_box = WebDriverWait(self.browser, 10).until(
            expected_conditions.presence_of_element_located((By.id, 'inputUsername'))
        )
        name_box.send_keys(self.username)

        name_box = self.browser.find_element_by_id('inputPassword')
        name_box.send_keys(self.password)

        submit_button = self.browser.find_element_by_css_selector('#validationHolder button')
        submit_button.click()

        self.assertIn('认证成功', self.browser.find_element_by_id('mainbody').text)
'''