from flask_testing import TestCase
from main import create_app
from flask import current_app, url_for

class mainTestCase(TestCase):
    def create_app(self):
        app = create_app()
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        return app

    def test_app_exists(self):
        self.assertFalse( current_app is None )

    def test_app_is_testing(self):
        self.assertTrue( current_app.config['TESTING'] )

    def test_index_redirects(self):
        response = self.client.get( url_for('public.index') )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, '/auth/login')
