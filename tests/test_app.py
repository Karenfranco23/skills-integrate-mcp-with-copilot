import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from fastapi import HTTPException
from fastapi.security import HTTPBasicCredentials

from src import app as app_module


class TeacherAuthenticationTests(unittest.TestCase):
    def setUp(self):
        self.credentials_file = tempfile.TemporaryDirectory()
        self.credentials_path = Path(self.credentials_file.name) / "teachers.json"
        salt = "test-salt"
        self.credentials_path.write_text(
            json.dumps(
                {
                    "teachers": [
                        {
                            "username": "teacher",
                            "salt": salt,
                            "password_hash": app_module.hash_teacher_password(
                                "correct-password", salt
                            ),
                        }
                    ]
                }
            ),
            encoding="utf-8",
        )
        self.credentials_file_patch = patch.object(
            app_module, "teacher_credentials_file", self.credentials_path
        )
        self.credentials_file_patch.start()
        self.addCleanup(self.credentials_file_patch.stop)
        self.addCleanup(self.credentials_file.cleanup)

    def test_valid_teacher_credentials_are_accepted(self):
        credentials = HTTPBasicCredentials(
            username="teacher", password="correct-password"
        )

        self.assertEqual(app_module.require_teacher(credentials), "teacher")

    def test_invalid_credentials_are_rejected(self):
        credentials = HTTPBasicCredentials(
            username="teacher", password="wrong-password"
        )

        with self.assertRaises(HTTPException) as context:
            app_module.require_teacher(credentials)

        self.assertEqual(context.exception.status_code, 401)

    def test_missing_credentials_are_rejected(self):
        with self.assertRaises(HTTPException) as context:
            app_module.require_teacher(None)

        self.assertEqual(context.exception.status_code, 401)
        self.assertEqual(
            context.exception.headers["WWW-Authenticate"], "Basic"
        )

    def test_registration_and_cancellation_require_teacher_authentication(self):
        protected_paths = {
            "/activities/{activity_name}/signup",
            "/activities/{activity_name}/unregister",
        }
        routes = {
            route.path: route
            for route in app_module.app.routes
            if getattr(route, "path", None) in protected_paths
        }

        self.assertEqual(set(routes), protected_paths)
        for route in routes.values():
            dependencies = [
                dependency.call for dependency in route.dependant.dependencies
            ]
            self.assertIn(app_module.require_teacher, dependencies)

    def test_activity_listing_remains_public(self):
        route = next(
            route
            for route in app_module.app.routes
            if getattr(route, "path", None) == "/activities"
        )
        dependencies = [
            dependency.call for dependency in route.dependant.dependencies
        ]

        self.assertNotIn(app_module.require_teacher, dependencies)


if __name__ == "__main__":
    unittest.main()
