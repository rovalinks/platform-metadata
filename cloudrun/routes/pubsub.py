from ingress.pubsub import PubSubIngress

_ingress = PubSubIngress()


def handle(request):
    return _ingress.process(request)