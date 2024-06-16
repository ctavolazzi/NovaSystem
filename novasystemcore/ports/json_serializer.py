# Example JSON Serializer implementation
from typing import Any
import json
from .data_serializer import DataSerializer

class JSONSerializer(DataSerializer):
    def serialize(self, data: Any) -> str:
        return json.dumps(data)

    def deserialize(self, data_str: str) -> Any:
        return json.loads(data_str)