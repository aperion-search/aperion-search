# SPDX-License-Identifier: AGPL-3.0-or-later
# pylint: disable=missing-module-docstring,disable=missing-class-docstring,invalid-name

from parameterized import parameterized

import aperion.plugins
import aperion.answerers
import aperion.preferences

from aperion.extended_types import sxng_request

from tests import AperionTestCase


class AnswererTest(AperionTestCase):

    def setUp(self):
        super().setUp()

        self.storage = aperion.plugins.PluginStorage()
        engines = {}
        self.pref = aperion.preferences.Preferences(["simple"], ["general"], engines, self.storage)
        self.pref.parse_dict({"locale": "en"})

    @parameterized.expand(aperion.answerers.STORAGE.answerer_list)
    def test_unicode_input(self, answerer_obj: aperion.answerers.Answerer):

        with self.app.test_request_context():
            sxng_request.preferences = self.pref

            unicode_payload = "árvíztűrő tükörfúrógép"
            for keyword in answerer_obj.keywords:
                query = f"{keyword} {unicode_payload}"
                self.assertIsInstance(answerer_obj.answer(query), list)
