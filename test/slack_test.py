from app.slack import Slack
import unittest
import matplotlib.pyplot as plt

class SlackTest(unittest.TestCase):
    '''
    def test_send_message_with_channel(self):
        s = Slack()
        s.send_message_with_channel("C07F1H97G5V", "*Hello, World!*\n#### This is a test message.")
        self.assertTrue(True)
    '''
    def test_send_image_with_channel(self):
        markdown = r"\frac{a}{b} = \int_{0}^{\infty} e^{-x} dx"
        fig = plt.figure(figsize=(4, 2))
        plt.text(0.5, 0.5, f'${markdown}$', fontsize=18, ha='center')
        plt.axis('off')
        plt.savefig("test.png", bbox_inches='tight', pad_inches=0)
        s = Slack()
        s.send_local_image("C07F1H97G5V", "test.png", "This is a test image.")

if __name__ == "__main__":
    unittest.main()