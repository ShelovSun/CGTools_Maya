from ngSkinTools2.python_compatibility import Object
from functools import partial

from ngSkinTools2.log import getLogger
from ngSkinTools2 import cleanup

log = getLogger("signal")


class SignalQueue(Object):
    def __init__(self):
        self.max_length = 100
        self.queue = []

    def emit(self, handler):
        if len(self.queue) > self.max_length:
            log.error("queue max length reached: emitting too many events?")
            raise Exception("queue max length reached: emitting too many events?")

        should_start = len(self.queue) == 0

        self.queue.append(handler)
        if should_start:
            self.process()

    def process(self):
        current_handler = 0
        queue = self.queue

        while current_handler < len(queue):
            # noinspection PyBroadException
            try:
                queue[current_handler]()
            except Exception:
                import ngSkinTools2

                if ngSkinTools2.DEBUG_MODE:
                    import sys
                    import traceback

                    traceback.print_exc(file=sys.__stderr__)

            current_handler += 1

        log.info("handler queue finished with %d items", len(self.queue))
        self.queue = []


# noinspection PyBroadException
class Signal(Object):
    """
    Signal class collects observers, interested in some particular event,and handles
    signaling them all when some event occurs. Both handling and signaling happens outside
    of signal's own code


    Handlers are processed breath first, in a queue based system.
    1. root signal fires, adds all it's handlers to the queue;
    2. queue starts being processed
    3. handlers fire more signals, in turn adding more handlers to the end of the queue.
    """

    all = []

    queue = SignalQueue()

    def __init__(self, name):
        if name is None:
            raise Exception("need name for debug purposes later")
        self.name = name
        self.handlers = []
        self.executing = False

        self.reset()
        Signal.all.append(self)
        cleanup.registerCleanupHandler(self.reset)

    def reset(self):
        self.handlers = []
        self.executing = False

    def emitDeferred(self, *args):
        import maya.utils as mu

        mu.executeDeferred(self.emit, *args)

    def emit(self, *args):
        """
        emit mostly just adds handlers to the processing queue,
        but if nobody is processing handlers at the emit time,
        it is started here as well.
        """
        # log.info("emit: %s", self.name)
        if self.executing:
            raise Exception('Nested emit on %s detected' % self.name)

        for i in self.handlers[:]:
            Signal.queue.emit(partial(i, *args))

    def addHandler(self, handler, qtParent=None):
        if hasattr(handler, 'emit'):
            handler = handler.emit

        self.handlers.append(handler)

        def remove():
            return self.removeHandler(handler)

        if qtParent is not None:
            qtParent.destroyed.connect(remove)

        return remove

    def removeHandler(self, handler):
        try:
            self.handlers.remove(handler)
        except ValueError:
            # not found in list? no biggie.
            pass


def on(*signals, **kwargs):
    """
    decorator for function: list signals that should fire for this function.

        @signal.on(signalReference)
        def something():
            ...
    """

    def decorator(fn):
        for i in signals:
            i.addHandler(fn, **kwargs)
        return fn

    return decorator
