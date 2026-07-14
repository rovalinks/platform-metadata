from pathlib import Path
import json


class SchemaLoader:

    def __init__(self):

        self.schema_directory = (
            Path(__file__).resolve().parent.parent
            / "registry"
            / "schemas"
        )

    def load(self, schema_name: str) -> dict:

        schema_file = self.schema_directory / schema_name

        with open(schema_file, encoding="utf-8") as file:

            return json.load(file)