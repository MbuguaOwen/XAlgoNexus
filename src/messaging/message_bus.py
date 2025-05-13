# /src/messaging/message_bus.py

from typing import Callable, List

class MessageBus:
    def __init__(self):
        self.subscribers: List[Callable] = []

    def subscribe(self, callback: Callable):
        self.subscribers.append(callback)

    def publish(self, event):
        for callback in self.subscribers:
            callback(event)
