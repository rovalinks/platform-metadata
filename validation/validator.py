from jsonschema import Draft202012Validator


class RegistryValidator:

    def __init__(self, schema: dict):

        self.validator = Draft202012Validator(schema)

    def validate(self, application: dict):

        errors = sorted(
            self.validator.iter_errors(application),
            key=lambda error: error.path
        )

        return errors