from concurrent.futures import ThreadPoolExecutor
import json
from importlib import import_module

class RedisSubscriber:
    def __init__(self, redis_connection, channels, max_workers=5):
        """
        Initializes the RedisSubscriber with a Redis connection,
        a list of channels to subscribe to, and the maximum number
        of worker threads for processing messages.

        Args:
            redis_connection: The connection object to the Redis server.
            channels (list): A list of channel names to subscribe to.
            max_workers (int, optional): The maximum number of worker
                                         threads in the pool. Defaults to 5.
        """
        self.redis_connection = redis_connection
        self.channels = channels
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

    def handle_message(self, message):
        """
        Handles a message received from the subscribed channels.
        If the message contains asynchronous tasks, it submits
        them to the thread pool executor.

        Args:
            message (dict): The message received from the Redis server.
        """
        try:
            data = json.loads(message['data'])
            if 'kind' in data and data['kind'] == 'async':
                function_path = data.get('function')
                if function_path:
                    module_name, func_name = function_path.rsplit('.', 1)
                    module = import_module(module_name)
                    func = getattr(module, func_name)
                    self.executor.submit(func, data)
        except (json.JSONDecodeError, ImportError, AttributeError) as e:
            print(f"Error processing message: {e}")

    def start_listening(self):
        """
        Starts listening to the configured Redis channels and processes
        incoming messages.
        """
        pubsub = self.redis_connection.pubsub()
        pubsub.subscribe(**{channel: self.handle_message for channel in self.channels})
        for message in pubsub.listen():
            # Redis returns a subscription confirmation as a message, skip it.
            if message['type'] != 'message':
                continue
            self.handle_message(message)
