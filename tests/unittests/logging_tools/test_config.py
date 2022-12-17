from pathlib import Path

from pyfakefs import fake_filesystem_unittest

import logging_tools.config as config


class TestConfig(fake_filesystem_unittest.TestCase):
    def setUp(self) -> None:
        """Set up a fake file system."""
        self.setUpPyfakefs()

        self.fs.create_dir("module_a")
        self.fs.create_file(Path("module_a", "__init__.py"))

        self.fs.create_dir("module_b")
        self.fs.create_file(Path("module_a", "test.py"))

    def test_is_module__true_case(self):
        self.assertTrue(config.is_module(Path("module_a")))

    def test_is_module__false_case(self):
        self.assertFalse(config.is_module(Path("module_b")))

    def test_find_child_modules(self):
        expected = ["module_a"]
        child_modules = config.find_child_modules(Path(self.fs.cwd))

        self.assertListEqual(expected, child_modules)

