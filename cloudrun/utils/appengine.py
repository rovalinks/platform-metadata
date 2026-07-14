def parse_name(resource_name: str) -> str:
    prefix = "//appengine.googleapis.com/"
    if resource_name.startswith(prefix):
        return resource_name[len(prefix):]
    return resource_name.lstrip("/")