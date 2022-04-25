import os
import time

from dwebsocket.decorators import accept_websocket

from AutomationPlatformDjango.settings import log_path


@accept_websocket
def echo(request):
    if request.is_websocket:
        try:
            for message in request.websocket:
                message = message.decode('utf-8')
                print(message)
                if message == 'connect':
                    logs = sorted([i for i in os.listdir(log_path) if 'all-' in i], reverse=True)[0]
                    file = os.path.join(log_path, logs)
                    print(file)
                    with open(file, 'rb') as f:
                        f.seek(0, 2)
                        while True:
                            time.sleep(0.5)
                            line = f.readline().strip()
                            if line:
                                request.websocket.send(line)
                else:
                    request.websocket.shutdown(2)
                    request.websocket.close()
        except Exception as e:
            request.websocket.close()


