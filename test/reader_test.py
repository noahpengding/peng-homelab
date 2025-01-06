import unittest
from app.read_file import FileReader

class ReaderTest(unittest.TestCase):
    def test_read_pdf(self):
        r = FileReader()
        text = r.read_pdf("2023-tables-fam-s.pdf")
        self.assertTrue(text)

if __name__ == "__main__":
    unittest.main()