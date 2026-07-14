from pathlib import Path

import yaml


class RegistryReader:

    def __init__(self):

        self.registry_directory = (
            Path(__file__).resolve().parent.parent
            / "registry"
            / "applications"
        )

    def load_all(self):

        applications = []

        for file in sorted(self.registry_directory.glob("*.yaml")):

            with open(file, encoding="utf-8") as stream:

                applications.append(
                    (
                        file.name,
                        yaml.safe_load(stream)
                    )
                )

        return applications