
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading
from sgtpyutils.logger import logger
host = ('localhost', 35080)
_directory = None

class FrontWebHandler(SimpleHTTPRequestHandler):
    def __init__(self, request, client_address, server) -> None:
        super().__init__(request, client_address, server, directory=_directory)
        self.extensions_map['.vue'] = 'text/html'

class FrontWebServices(threading.Thread):
    def run(self) -> None:
        logger.debug(f'web service start at:{host}')
        server = HTTPServer(host, FrontWebHandler)
        server.serve_forever()
        return super().run()


client: FrontWebServices = None


def start(directory:str):
    global client
    global _directory
    _directory = directory
    client = FrontWebServices()
    client.directory = directory
    client.start()
