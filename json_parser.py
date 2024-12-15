class JsonParser:
    def __init__(self, rawJson):
        self.string = ""
        for item in rawJson:
            self.string += str(item) + '\n'

    def __str__(self):
        return self.string
