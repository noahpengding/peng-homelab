import unittest
from app.openai_api import OpenAIHandler
from app.slack import Slack

class TestOpenAI(unittest.TestCase):
    '''
    def test_list_models(self):
        o = OpenAIHandler()
        models = o.list_models()
        print(models)
        self.assertTrue(len(models) > 0)

    def test_create_chat_completion(self):
        o = OpenAIHandler()
        completion = o.create_chat_completion("Create a 200 words Story about Computer Science")
        print(completion)
        completion = o.create_chat_completion("Make the stoy more detailed with some professional jokes")
        print(completion)
        self.assertTrue(len(completion) > 0)
    def test_image_generation(self):
        o = OpenAIHandler()
        image = o.image_generation("Generate an image of a cat")
        print(image)
        self.assertTrue(len(image) > 0)
    def test_list_parameters(self):
        o = OpenAIHandler()
        parameters = o.list_parameters()
        print(parameters)
        self.assertTrue(len(parameters) > 0)
    def test_slack_start(self):
        s = Slack()
        s.start()
    def test_openai_usage(self):
        o = OpenAIHandler()
        print(o.get_usage())
'''
    def test_openai_handler(self):
        o1 = OpenAIHandler("123")
        o2 = OpenAIHandler("123")
        o3 = OpenAIHandler("456")
        o1.create_chat_completion("Create a 200 words Story about Computer Science")
        self.assertEqual(o1, o2)
        self.assertNotEqual(o1, o3)
        print(o1.get_coversions())
        print(o3.get_coversions())


if __name__ == '__main__':
    unittest.main()