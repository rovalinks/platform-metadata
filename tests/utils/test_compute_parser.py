from utils.compute import (
    parse_instance_name,
)


def test_parse_instance_name():

    parsed = parse_instance_name(

        "projects/test/zones/europe-west2-a/instances/vm1"

    )

    assert parsed["project"] == "test"

    assert parsed["zone"] == "europe-west2-a"

    assert parsed["instance"] == "vm1"