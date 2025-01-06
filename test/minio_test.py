import unittest
from app.minio_storage import MinioStorage

class MinioTest(unittest.TestCase):
    def test_file_list(self):
        m = MinioStorage()
        files = m.file_list_name("peng", "Chat")
        print(files)
        self.assertTrue(len(files) > 0)
    def test_file_download(self):
        m = MinioStorage()
        file_name = "20240928-011418_write_something_rand.json"
        m.file_download("peng", f"Chat/{file_name}", "test.json")
    '''
    def test_upload_file(self):
        m = MinioStorage()
        file_name = "20240928-011947_write_a_poem_randoml.json"
        m.file_upload("peng", file_name, f"Chat/{file_name}", "application/json")
        self.assertTrue(m.file_exists("peng", f"Chat/{file_name}"))
        '''

if __name__ == '__main__':
    unittest.main()