from abc import ABC, abstractmethod


class EmbeddingModel(ABC):
    def __init__(self):
        super().__init__()

    @property
    @abstractmethod
    def model_name(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def embedding_dim(self):
        raise NotImplementedError

    @abstractmethod
    def get_embedding(self, *args, **kwargs):
        raise NotImplementedError
