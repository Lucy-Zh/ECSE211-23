"""
Module for providing access to a single, simple, GUI that can easily display data.
It also allows the creation of buttons and sliders for adjusting starting parameters.

Author: Ryan Au
"""

from collections import deque
from queue import Empty, Queue
from tkinter import Scale, ttk, StringVar, TclError, Button as TkButton

import tkinter as tk
from tkinter.constants import HORIZONTAL
import threading
from uuid import UUID, SafeUUID
import time

"""WINDOW - None when closed, Not None when open"""
WINDOW: tk.Tk = None

"""LABELS - filled with labels. {} when closed. {...} when open.
Should use WINDOW.destroy() to delete actual widgets in window.
"""
LABELS = {}

"""_EXIT_FLAG - True to when closed. False when open.
"""
_EXIT_FLAG = True

"""_TK_THREAD - Should be None when closed. No WINDOW to alter."""
_TK_THREAD = None

"""_USER_THREAD - Used for start_threaded.
None to start. Not None after a start_threaded.
_USER_THREAD.is_alive() is True while loop runs.
_USER_THREAD.is_alive() is False when the windowhas closed.
"""
_USER_THREAD = None


class Command:
    WAIT_DONE = 0.001

    def __init__(self, func, args):
        if not callable(func):
            raise RuntimeError("func is not a callable function")
        self.func = func
        self.args = args
        self.result_given = False
        self.error_given = False
        self.result = None
        # self.cid = UUID(is_safe=SafeUUID.safe)

    def execute(self):
        """To be executed in the main thread"""
        try:
            self.result = self.func(*(self.args))
            self.result_given = True
        except BaseException as e:
            self.result = e
            self.error_given = True

    def wait_done(self):
        """To be executed in the worker process"""
        while not self.result_given and not self.error_given:
            time.sleep(Command.WAIT_DONE)
        if self.result_given:
            return self.result
        if self.error_given:
            raise self.result


class CommandQueue:
    def __init__(self):
        self.queue = Queue()

    def put_func(self, func, args):
        c = Command(func, args)
        self.queue.put(c)
        return c

    def execute_all(self):
        size = self.queue.qsize()
        try:
            while size > 0:
                command: Command = self.queue.get(block=False)
                command.execute()
                size -= 1
        except Empty:
            pass


"""Commands function requests, from threads outside TK thread.
All commands are executed upon calls to telemetry.update()
"""
_COMMANDQUEUE = CommandQueue()


def remote(func, *args):
    """When outside the telemetry thread (thread where telemetry.start() executed)
    This will queue the function func for execution during the telemetry.update() call.
    """
    if _TK_THREAD is None or threading.current_thread().name == _TK_THREAD.name:
        raise RuntimeError(
            "Cannot run this function in the same thread as telemetry.update")
    c = _COMMANDQUEUE.put_func(func, args)
    return c.wait_done()


def remote_capable(func):
    """A function decorator, used to allow functions to run in both
    main telemetry thread and outside threads.
    """
    def inner(*args):
        if _TK_THREAD is None or threading.current_thread().name == _TK_THREAD.name:
            return func(*args)
        else:
            return remote(func, *args)
    return inner


def _on_closing():
    """Private method: cleans up internal values on window destruction"""
    global WINDOW, _EXIT_FLAG, LABELS, _TK_THREAD
    WINDOW.destroy()
    WINDOW = None
    _EXIT_FLAG = True
    _TK_THREAD = None
    LABELS = {}


def start():
    """Open the telemetry window.

    Thread that runs this function, will be called the telemetry thread.
    """
    global WINDOW, _EXIT_FLAG, _TK_THREAD
    _EXIT_FLAG = False
    if WINDOW is None:
        WINDOW = tk.Tk()
        _TK_THREAD = threading.current_thread()
    WINDOW.protocol("WM_DELETE_WINDOW", _on_closing)
    update()


def _start_threaded_target(pre_update_func, sleep_interval, *args):
    """Private method: the target function used in start_threaded."""
    try:
        start()
        while True:
            if not isopen():
                break
            pre_update_func()
            update()
            time.sleep(sleep_interval)
    except KeyboardInterrupt:
        pass


def start_threaded(pre_update_func=None, sleep_interval=0.01):
    """Starts the telemetry window in a separate thread.

    pre_update_func is a function with no arguments, which will be
    executed before every call to telemetry.update
    """
    global _USER_THREAD
    if pre_update_func is None:
        def func():
            pass
        pre_update_func = func
    if not callable(pre_update_func):
        raise RuntimeError("pre_update_func must be a callable function")
    if not isopen():
        _USER_THREAD = threading.Thread(target=_start_threaded_target, args=(
            pre_update_func, sleep_interval), daemon=True)
        _USER_THREAD.start()
        return True
    return False


def isopen():
    """Determines if the telemtry window has been opened or closed"""
    return not _EXIT_FLAG


@remote_capable
def resize(width=100, height=100):
    """Resize telemtry to a set width and height in pixels"""
    if WINDOW is None:
        return
    WINDOW.geometry("{}x{}".format(width, height))


@remote_capable
def stop():
    """Closes telemtry window"""
    if WINDOW is not None:
        _on_closing()


class _Updater:
    """Starts a thread with a constantly running while loop.
    While loop repeatedly runs the given func with the given arguments.
    """
    UPDATE_DELAY = 0.01

    def __init__(self, func, *args):
        self.thread = threading.Thread(
            target=self._listener, args=args, daemon=True)
        self.func = func
        self.event = threading.Event()
        self.event.set()

    def start(self):
        self.thread.start()

    def stop(self):
        self.event.clear()

    def _listener(self, *args):
        while self.event.is_set():
            try:
                (self.func)(*args)
                time.sleep(_Updater.UPDATE_DELAY)
            except BaseException as e:
                print(e)
                break


class _Updatable:
    """A class that inherits from this mixin gains two methods:
    set_updater and stop_updater

    set_updater will create an internal _updater varaible, and
        assign an _Updater object to it. The expected input function
        will always get the self as the first argument.

    stop_updater will stop the internal _updater if it isn't already
        stopped.
    """

    def set_updater(self, func, *args):
        """set_updater will create an internal _updater varaible, and
            assign an _Updater object to it. The expected input function
            will always get the self as the first argument.
        """
        if hasattr(self, '_updater') and self._updater is not None:
            if not isinstance(self._updater, _Updater):
                return  # Something went wrong, so we won't touch _updater anymore
            self._updater.stop()
        self._updater = _Updater(func, self, *args)
        self._updater.start()

    def stop_updater(self):
        """stop_updater will stop the internal _updater if it isn't already
        stopped.
        """
        if hasattr(self, '_updater') and self._updater is not None and isinstance(self._updater, _Updater):
            self._updater.stop()


class _Slider(_Updatable):
    """An internal _Slider object, that should not be instantiated
    using this class. Use telemetry.create_slider
    """

    def __init__(self, lower, upper, value, func=None):
        self.s = Scale(WINDOW, from_=lower, to=upper, orient=HORIZONTAL)
        self.s.set(value)
        self.s.pack()

        self.lower = lower
        self.upper = upper

        if func is not None:
            self.set_updater(func)

    @remote_capable
    def get_value(self):
        return self.s.get()

    @remote_capable
    def destroy(self):
        self.s.destroy()
        self.stop_updater()

    def __repr__(self):
        return f"Slider[{self.lower} <-> {self.upper}, {self.get_value()}]"


@remote_capable
def create_slider(lower, upper=None, value=None, func=None):
    """Adds a slider to the telemetry window AND returns the slider object added

    create_slider(50) creates: 0<---25--->50
    create_slider(25, 50) creates: 25<---37--->50
    create_slider(-100, 100, 50) creates: -100<---50--->100
    """
    if upper is None:
        upper = lower
        lower = 0

    if value is None:
        value = lower

    if WINDOW is None or not isopen():
        return

    return _Slider(lower, upper, value, func)


class _Button(_Updatable):
    """An internal _Button object, that should not be instantiated
    using this class. Use telemetry.create_button
    """

    def __init__(self, name, func=None):
        self.b = TkButton(WINDOW, text=name)
        self.b.bind("<ButtonPress>", self._on_press)
        self.b.bind("<ButtonRelease>", self._on_release)
        self.name = name
        self._is_pressed = False
        self.b.pack()

        if func is not None:
            self.set_updater(func)

    def _on_press(self, *args):
        self._is_pressed = True

    def _on_release(self, *args):
        self._is_pressed = False

    @remote_capable
    def is_pressed(self):
        return self._is_pressed

    @remote_capable
    def destroy(self):
        self.b.destroy()
        self.stop_updater()

    def __repr__(self):
        return f"Button[{self.name}, {self.is_pressed()}]"


@remote_capable
def create_button(name, func=None):
    """Adds a button to the telemetry window AND returns the button object added"""
    if WINDOW is None or not isopen():
        return

    return _Button(name, func)


def label(key, data, showkey=False):
    """Adds a textual Label based on a key to the telemetry window.

    If the key has not been used before, then it will create a new Label
    If the key has been used before, then it will change the old Label

    If showkey == True, then Label will have the format "key: data"
    If showkey == False, then Label will have the format "data" only
    """
    add(key, data, showkey)


@remote_capable
def add(key, data, showkey=False):
    """Adds a textual Label based on a key to the telemetry window.

    If the key has not been used before, then it will create a new Label
    If the key has been used before, then it will change the old Label

    If showkey == True, then Label will have the format "key: data"
    If showkey == False, then Label will have the format "data" only
    """
    if WINDOW is None or not isopen():
        return
    key = str(key)
    data = str(data)
    if showkey:
        data = "{} : {}".format(key, data)
    if key in LABELS:
        LABELS[key][1].set(data)
    else:
        var = StringVar()
        var.set(data)
        LABELS[key] = (tk.Label(WINDOW, textvariable=var), var)
        LABELS[key][0].pack()


def update(retries=1):
    """Updates the display, allowing it to function and respond to input/output.

    It also runs telemetry.remote commands
    """
    global WINDOW
    if WINDOW is not None:
        try:
            ### Execute CommandQueue Operations ###
            _COMMANDQUEUE.execute_all()
            ### Execute CommandQueue Operations ###
            if WINDOW is None or not isopen():
                return False
            for i in range(retries):
                WINDOW.update()
        except TclError as e:
            err = str(e)
            if err == 'can\'t invoke "update" command: application has been destroyed':
                WINDOW = None
        return True
    return False


def clear_labels():
    clear()


@remote_capable
def clear():
    """Destroy and remove all LABELS of the telemetry window"""
    global LABELS
    for i, widget in LABELS.items():
        try:
            widget[0].destroy()
        except TclError:
            pass
    LABELS = {}


def mainloop(pre_update_func=None, sleep_interval=0.01):
    """Starts a while loop that calls update for you! 
    Usage of telemetry.update not needed when using this

    pre_update_func is a function with no arguments, which will be
    executed before every call to telemetry.update
    """
    if pre_update_func is None:
        def func():
            pass
        pre_update_func = func
    if not callable(pre_update_func):
        raise RuntimeError("pre_update_func must be a callable function")
    if WINDOW is not None and isopen():
        _start_threaded_target(pre_update_func, sleep_interval)


if __name__ == '__main__':
    import time
    start()
    resize(500, 200)
    i = 0
    add("word", "heyo this is the start")
    update()
    while True:
        time.sleep(1)

        ### Test clearing window despite still updating ###
        if i == 10:
            clear()
            if not isopen():
                start()

        # Adding data
        add("color", "red", True)
        i = i + 2 if i < 40 else 0

        print(i, isopen())
        add("counter", "*"*i)

        # Must update window to see changes
        update()
