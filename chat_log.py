
class ChatLog:
    filename = "chat_log.txt"
    def msg(self, message):
        with open(self.filename, "a") as f:
            f.write(message + "\n")
            f.close()

    def err(self, source, message):
        print(f'{source}: {message}')
        self.write_line(f'{source}: {message}')