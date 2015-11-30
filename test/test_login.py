import os
import unittest
from kwick import Kwick

user = os.environ['kwick_user'] or 'test'
password = os.environ['kwick_password'] or 'changeme'

class testKwick(unittest.TestCase):

    @classmethod
    def setup_class(cls):
        cls.kwick = Kwick()
        resp = cls.kwick.kwick_login(user, password)
        assert 'session_name' in resp

    def test_index(self):
        resp = self.kwick.kwick_index(page=0)
        assert 'socialstream' in resp

    def test_infobox(self):
        resp = self.kwick.kwick_infobox()
        assert 'infobox' in resp
        assert 'ticker' in resp

    def test_user(self):
        testuser = 'kwick'
        resp = self.kwick.kwick_user(username=testuser)
        assert 'isFriend' in resp

        not_availuser = 'ar5oih435llsv83252jkffSdfs'
        resp = self.kwick.kwick_user(username=not_availuser)
        assert 'errorMsg' in resp
