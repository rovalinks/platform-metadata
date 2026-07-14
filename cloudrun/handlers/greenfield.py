from services.greenfield import GreenfieldService

service = GreenfieldService()


def greenfield(payload):
    """
    Handles Eventarc CloudEvents.
    """

    result = service.process(
        payload
    )

    return result, 200
