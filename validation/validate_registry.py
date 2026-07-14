from registry_reader import RegistryReader
from schema_loader import SchemaLoader
from validator import RegistryValidator


def main():
    schema = SchemaLoader().load("application.schema.json")
    validator = RegistryValidator(schema)
    
    # Load all applications
    applications = {filename: app for filename, app in RegistryReader().load_all()}
    
    failed = False
    # Tracks {project_id: source_description}
    project_ids = {}

    for filename, application in applications.items():
        # 1. Schema Validation
        errors = validator.validate(application)
        if errors:
            failed = True
            print(f"\n{filename}")
            for error in errors:
                print(f"  - {error.message}")
        
        # 2. Cross-binding and Cross-file Project ID Validation
        if "bindings" in application:
            for index, binding in enumerate(application["bindings"]):
                # Only validate GCP projects
                if binding.get("cloud") != "gcp":
                    continue

                project_id = binding.get("projectId")
                if not project_id:
                    continue

                # Define a unique identifier for the location of this binding
                location = f"{filename} (binding index {index})"

                if project_id in project_ids:
                    print(
                        f"Duplicate projectId '{project_id}' found in "
                        f"{project_ids[project_id]} and {location}"
                    )
                    failed = True
                else:
                    project_ids[project_id] = location

        if not errors and not failed:
            print(f"{filename} ✓")

    if failed:
        raise SystemExit(1)

    print("\nRegistry validation successful")


if __name__ == "__main__":
    main()