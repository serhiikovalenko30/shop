from threading import Thread
from time import sleep


class Cron:

    def __init__(self, func):
        self._func = func

    def run(self):
        Thread(target=self._func).start()

    @staticmethod
    def cron_decorator(time=60):
        def cron(func):
            def wrapper(*args):
                while True:
                    func(*args)
                    sleep(time)
            return wrapper
        return cron
