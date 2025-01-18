import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.utils.minio_connection import MinioStorage
m = MinioStorage()
print(m.file_list_name(prefix="Chat"))
with open("test.txt", "w") as f:
    f.write("This is a test message")
print(m.file_upload("test.txt", "test.txt", "text/plain"))
print(m.file_list_name())
print(m.file_download("test.txt", "test_download.txt"))
os.remove("test.txt")
print(m.file_list_name())
print(m.remove_file("test.txt"))
with open("test_download.txt", "r") as f:
    print(f.read())
os.remove("test_download.txt")