# SPDX-License-Identifier: AGPL-3.0-or-later
# pylint: disable=missing-module-docstring,disable=missing-class-docstring,invalid-name

import pathlib
import os
import aiounittest


os.environ.pop('aperion_SETTINGS_PATH', None)
os.environ['aperion_DISABLE_ETC_SETTINGS'] = '1'


class AperionTestLayer:
    """Base layer for non-robot tests."""

    __name__ = 'AperionTestLayer'

    @classmethod
    def setUp(cls):
        pass

    @classmethod
    def tearDown(cls):
        pass

    @classmethod
    def testSetUp(cls):
        pass

    @classmethod
    def testTearDown(cls):
        pass


class AperionTestCase(aiounittest.AsyncTestCase):
    """Base test case for non-robot tests."""

    layer = AperionTestLayer

    SETTINGS_FOLDER = pathlib.Path(__file__).parent / "unit" / "settings"
    TEST_SETTINGS = "test_settings.yml"

    def setUp(self):
        self.init_test_settings()

    def setattr4test(self, obj, attr, value):
        """setattr(obj, attr, value) but reset to the previous value in the
        cleanup."""
        previous_value = getattr(obj, attr)

        def cleanup_patch():
            setattr(obj, attr, previous_value)

        self.addCleanup(cleanup_patch)
        setattr(obj, attr, value)

    def init_test_settings(self):
        """Sets ``aperion_SETTINGS_PATH`` environment variable an initialize
        global ``settings`` variable and the ``logger`` from a test config in
        :origin:`tests/unit/settings/`.
        """

        os.environ['aperion_SETTINGS_PATH'] = str(self.SETTINGS_FOLDER / self.TEST_SETTINGS)

        # pylint: disable=import-outside-toplevel
        import aperion
        import aperion.locales
        import aperion.plugins
        import aperion.search
        import aperion.webapp

        # https://flask.palletsprojects.com/en/stable/config/#builtin-configuration-values
        # aperion.webapp.app.config["DEBUG"] = True
        aperion.webapp.app.config["TESTING"] = True  # to get better error messages
        aperion.webapp.app.config["EXPLAIN_TEMPLATE_LOADING"] = True

        aperion.init_settings()
        aperion.plugins.initialize(aperion.webapp.app)

        # aperion.search.initialize will:
        # - load the engines and
        # - initialize aperion.network, aperion.metrics, aperion.processors and aperion.search.checker

        aperion.search.initialize(
            enable_checker=True,
            check_network=True,
            enable_metrics=aperion.get_setting("general.enable_metrics"),  # type: ignore
        )

        # pylint: disable=attribute-defined-outside-init
        self.app = aperion.webapp.app
        self.client = self.app.test_client()
