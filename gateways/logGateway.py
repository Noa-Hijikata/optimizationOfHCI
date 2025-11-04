from abc import ABC, abstractmethod


class LogGateway(ABC):

    @abstractmethod
    def save(self, log_event):
        pass
