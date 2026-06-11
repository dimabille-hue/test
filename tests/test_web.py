from urllib.parse import urlencode
from wsgiref.util import setup_testing_defaults
import unittest

from archive_app.web import app, render_page, ArchiveFilters


class ArchiveWebTest(unittest.TestCase):
    def test_page_contains_python_marker_and_traceability_alert(self):
        html = render_page(ArchiveFilters(selected_id="obj-002"))

        self.assertIn("Python-прототип цифрового архива", html)
        self.assertIn("Разрыв прослеживаемости", html)
        self.assertIn("doc-missing", html)

    def test_filter_query_is_rendered_server_side(self):
        html = render_page(ArchiveFilters(query="подушкино", status="attention"))

        self.assertIn("1 найдено", html)
        self.assertIn("50:21:0050203:88", html)
        self.assertNotIn("77:01:0004010:1542", html)

    def test_page_contains_operational_roadmap(self):
        html = render_page(ArchiveFilters())

        self.assertIn("От прототипа к промышленной системе", html)
        self.assertIn("Авторизация и роли", html)
        self.assertIn("Интеграции с реестрами", html)
        self.assertIn("6 направлений", html)

    def test_wsgi_app_returns_html(self):
        environ = {}
        setup_testing_defaults(environ)
        environ["PATH_INFO"] = "/"
        environ["QUERY_STRING"] = urlencode({"owner_type": "person"})
        status_headers = []

        def start_response(status, headers):
            status_headers.append((status, headers))

        body = b"".join(app(environ, start_response)).decode("utf-8")

        self.assertEqual(status_headers[0][0], "200 OK")
        self.assertIn("Иванова Мария Петровна", body)
        self.assertNotIn("ООО «Северный Контур»</strong></div>", body)


if __name__ == "__main__":
    unittest.main()
