import unittest
from silero_api_server.tts import SileroTtsService
from silero_api_server.server import SAMPLE_PATH

class SileroApiServerTest(unittest.TestCase):
    def test_get_languages(self):
        svc = SileroTtsService(SAMPLE_PATH)
        lang = svc.get_languages()
        self.assertIn('https://models.silero.ai/models/tts/es/v3_es.pt',lang.values())