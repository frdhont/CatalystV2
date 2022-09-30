from app import app


def test_pass_correct(self):
    tester = app.test_client(self)
    response = tester.get('/index')
    self.assertEqual(response.status_code, 200)