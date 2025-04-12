class Changes:
    def __init__(self, file, key, value):
        self.file = file
        self.key = key
        self.value = value

    def __str__(self):
        return f"{self.file}: {self.key} = {self.value}"

    def get_file(self):
        return self.file

    def get_key(self):
        return self.key

    def get_value(self):
        return self.value

    def get_changes(self):
        return {"file": self.file, "key": self.key, "value": self.value}

    def __eq__(self, other):
        return (
            self.file == other.file
            and self.key == other.key
            and self.value == other.value
        )
