import json
import threading
import unittest
from urllib.request import urlopen
from urllib.error import HTTPError
from unittest.mock import patch
from http.server import ThreadingHTTPServer

from app import Handler


class TestApp(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.url = f"http://127.0.0.1:{cls.server.server_port}"
        cls.thread = threading.Thread(
            target=cls.server.serve_forever,
            daemon=True
        )
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def get(self, path):
        return urlopen(self.url + path, timeout=5)

    def test_health(self):
        with self.get("/healthz") as response:
            self.assertEqual(response.status, 200)
            self.assertEqual(json.load(response)["status"], "healthy")

    @patch.dict("os.environ", {"FAIL_MODE": "0"})
    def test_work_success(self):
        with self.get("/work") as response:
            self.assertEqual(response.status, 200)
            self.assertEqual(json.load(response)["status"], "success")

    @patch.dict("os.environ", {"FAIL_MODE": "1"})
    def test_work_failure(self):
        with self.assertRaises(HTTPError) as result:
            self.get("/work")

        with result.exception as response:
            self.assertEqual(response.code, 500)
            self.assertEqual(json.load(response)["status"], "error")


if __name__ == "__main__":
    unittest.main()