from abc import ABC, abstractmethod
from typing import Any

class DataSerializer(ABC):
    """
    An abstract base class defining the interface for data serializers in the NovaSystem.

    Methods:
        serialize(data) -> str: Serializes the given data into a string representation.
        deserialize(data_str) -> Any: Deserializes a string representation back into data.
    """

    @abstractmethod
    def serialize(self, data: Any) -> str:
        """
        Serializes the given data into a string representation.

        Args:
            data: The data to be serialized.

        Returns:
            A string representation of the serialized data.
        """
        pass

    @abstractmethod
    def deserialize(self, data_str: str) -> Any:
        """
        Deserializes a string representation back into data.

        Args:
            data_str: A string representation of serialized data.

        Returns:
            The deserialized data.
        """
        pass


