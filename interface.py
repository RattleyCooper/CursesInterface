import curses
from common import Cursor, Mouse, Screen


class Interface(object):
    """
    A class to facilitate the creation of text interfaces with curses.
    """
    def __init__(self, stdscr, callbacks=None):
        self.curses = curses
        self.curses.cbreak()
        self.curses.noecho()
        self.pad_pos = 0

        self.debug_pad = stdscr.subpad(0, 80)

        if callbacks is None:
            self.callbacks = {}
        else:
            if type(callbacks) != dict:
                raise TypeError('The callbacks keyword should be a dict, but got a {}'.format(type(callbacks)))
            self.callbacks = callbacks

        self.cursor = Cursor(0, 0)
        self.mouse = Mouse(0, 0, 0, 0, 0)

        self.current_line = ''
        self.ch = 0
        self.line_no = 0
        self.lines = ['']
        self.stdscr = Screen(stdscr)
        self.stdscr.cursor = self.cursor
        self.stdscr.keypad(True)

    def __del__(self):
        self.curses.nocbreak()
        self.stdscr.keypad(False)
        self.curses.echo()
        self.curses.endwin()

    def __setattr__(self, key, value):
        try:
            self.stdscr.cursor = self.cursor
        except AttributeError:
            # Need to handle attribute error because
            # the attribute doesn't exist before
            # an attribute is set.
            pass

        object.__setattr__(self, key, value)

    def refresh(self):
        """
        Refresh the screen by clearing it and printing all the lines out again.

        :return:
        """

        self.stdscr.clear()
        self.stdscr.addstr('\n\r'.join(self.lines))
        return self

    def _run_callback(self, ch, unregistered=False):
        """
        Run a callback for the given ch.

        :param ch:
        :param unregistered:
        :return:
        """

        if unregistered:
            return self.callbacks[-1](self)
        return self.callbacks[ch](self)

    def set_callback(self, ch, callback):
        """
        Register a callback for a specific key press.

        :param ch:
        :param callback:
        :return:
        """

        self.callbacks[ch] = callback
        return self

    def main(self):
        """
        Main loop that calls the callback functions.

        :return:
        """

        callback_keys = list(self.callbacks.keys())
        while True:
            self.stdscr.refresh()

            # Get the cursor and set the data as an
            # attribute on the interface.
            cursor_y, cursor_x = self.curses.getsyx()
            self.cursor.y, self.cursor.x = cursor_y, cursor_x

            # Get the ch and set it as an attribute
            # on the interface.
            ch = self.stdscr.getch()
            self.ch = ch
            if ch == curses.KEY_MOUSE:
                mouse = self.curses.getmouse()
                self.mouse.id = mouse[0]
                self.mouse.x, self.mouse.y, self.mouse.z = mouse[1], mouse[2], mouse[3]
                self.mouse.bstart = mouse[4]
                y, x = self.stdscr.getyx()
                # self.mouse = list(self.mouse) + [y, x]

            # Run registered key callbacks.
            if ch in callback_keys:
                result = self._run_callback(ch)
                if not result:
                    break
                continue
            else:
                self._run_callback(ch, unregistered=True)


if __name__ == '__main__':
    def get_callback_dict(module_name, excludes=None, ch=False):
        """
        Get a dict of callback methods on instantiated Callback's

        :param excludes:
        :param ch:
        :return dict:
        """

        if not excludes or excludes is None:
            excludes = []

        # Get list of exclusions.
        exclusions = []
        for exclude in excludes:
            exclusions += dir(__import__(exclude))

        # Import the given callbacks module.
        all_callbacks = __import__(module_name)
        # Get the import names.
        callback_item_names = dir(all_callbacks)
        # Filter out anything that was in the exclusions list.
        callback_item_names = [item for item in callback_item_names if item not in exclusions]

        # Create a callback dictionary for output.
        callback_dict = {}
        for callback_item_name in callback_item_names:
            # If ch was set to True, then we should output a dict with
            # the ch as the key and the callback method as the value.
            # Then continue early.
            if ch:
                cbi = getattr(all_callbacks, callback_item_name)()
                callback_dict[cbi.ch] = cbi.callback
                continue

            # If ch is not set to true, this piece of code runes and
            # gives a callback dictionary with the callback name
            # as the key and the Callback object as the value.
            # That means the `callback` method must still be accessed.
            callback_dict[callback_item_name] = getattr(all_callbacks, callback_item_name)()

        return callback_dict


    def main():
        stdscr = curses.initscr()
        # curses.curs_set(0)
        curses.mousemask(1)
        stdscr.scrollok(1)
        stdscr.idlok(1)

        # Create a scrolling pad.
        pad = stdscr.subpad(0, 0)
        pad.scrollok(1)
        pad.idlok(1)
        pad.nodelay(1)

        # Get a callback dictionary with the ch as the keys
        # and the `callback` method as the values
        callback_dictionary = get_callback_dict('text_editor_callbacks', excludes=['common'], ch=True)

        # Instantiate the interface.
        interface = Interface(pad, callbacks=callback_dictionary)
        # A callback can be registered using the instance.
        # interface.set_callback(32, callback_dictionary[32])

        # Start the main function and make sure everything restarts.
        try:
            interface.main()
        finally:
            interface.curses.nocbreak()
            interface.stdscr.keypad(False)
            interface.curses.echo()
            interface.curses.endwin()

    main()
