import unittest
from silero_api_server.tts import SileroTtsService

class SileroApiServerTest(unittest.TestCase):
    def test_list_languages(self):
        svc = SileroTtsService('samples')
        lang = svc.list_languages()
        self.assertIn('https://models.silero.ai/models/tts/es/v3_es.pt',lang.values())

    def test_init_model(self):
        svc = SileroTtsService('samples')
        lang = svc.list_languages()
        svc.load_model(list(lang.keys())[0])
        model_file = svc.model_file
        self.assertTrue(model_file.exists())