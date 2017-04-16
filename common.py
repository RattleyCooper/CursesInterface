

class TypeLocked(object):
    """
    Object used to facilitate binding attributes to a specific type
    so that a TypeError is thrown if the type changes.

    Example:

        class Parent(TypeLocked):
            type_bindings = {'x': int}

        class Child(Parent):
            type_bindings = dict(Parent.type_bindings)
            type_bindings['y'] = int

        child = Child(0, 12)
        child.y = 'a'  # Throws error like expected.
        child.x = 'a'  # Throws error like expected.

        parent = Parent(5)
        parent.y = 'h'  # No error like expected.
        parent.x = 'a'  # Throws error like expected.
    """

    type_bindings = {}

    def __setattr__(self, key, value):
        """
        Set attributes on the object. If the key is in the attribute_type_bindings
        keys, and the value does not match the type given from accessing the key
        on the attribute_type_bindings, then a TypeError will be raised.

        :param key:
        :param value:
        :return:
        """

        if key in self.type_bindings.keys() and not isinstance(value, self.type_bindings[key]):
            raise TypeError(
                'Cannot set \'{}\' because the type was not \'{}\': {} - {}'.format(
                    key,
                    self.type_bindings[key],
                    str(value),
                    type(value)
                )
            )
        object.__setattr__(self, key, value)


class Cursor(TypeLocked):
    """
    Cursor object for keeping track of the cursor's x and y location.

    Object is TypeLocked so that `x` and `y` can not have their type
    changed from an int.
    """

    type_bindings = {'x': int}
    type_bindings['y'] = int

    def __init__(self, x, y):
        """
        Instantiate the Cursor object with 2 integers. The first integer
        is `x` and the second integer is `y`.

        :param int x:
        :param int y:
        """

        self.x = x
        self.y = y

    def __getitem__(self, item):
        if item == 0:
            return self.x
        if item == 1:
            return self.y


class Mouse(TypeLocked):
    """
    Mouse object for keeping track of attributes related to mouse events.

    Object is TypeLocked so that its attributes can not have their type
    changed from an int.
    """

    type_bindings = {'id': int}
    type_bindings['x'] = int
    type_bindings['y'] = int
    type_bindings['z'] = int
    type_bindings['bstate'] = int

    def __init__(self, id, x, y, z, bstate):
        """
        All parameters must be integers.

        :param id:
        :param x:
        :param y:
        :param z:
        :param bstate:
        """

        self.id = id
        self.x = x
        self.y = y
        self.z = z
        self.bstate = bstate

    def __getitem__(self, item):
        """
        Access

        :param item:
        :return:
        """

        if item == 0:
            return self.id
        if item == 1:
            return self.x
        if item == 2:
            return self.y
        if item == 3:
            return self.z
        if item == 4:
            return self.bstate


class Screen(object):
    """
    Monkey-patched Window object for facilitating higher-level methods for manipulating
    the given window object.
    """

    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.cursor = Cursor(0, 0)

    def __getattr__(self, item):
        """
        Use the stdscr object as a fallback if the `item` doesn't exist
        as an attribute on the Screen object.

        :param item:
        :return:
        """

        attr = False
        try:
            attr = object.__getattribute__(self, item)
            base_obj_missing_attr = False
        except AttributeError:
            base_obj_missing_attr = True

        if base_obj_missing_attr and hasattr(self.stdscr, item):
            return getattr(self.stdscr, item)
        else:
            try:
                return attr
            except AttributeError:
                raise AttributeError("{} is not set as an attribute.".format(item))

    def move_cursor(self, x, y):
        """
        Move the cursor to the given x, y coordinates on the standard screen.

        :param x:
        :param y:
        :return:
        """

        self.stdscr.addstr(y, x, '')
        return self


class Callback(TypeLocked):
    debug = False
    ch = -1
    type_bindings = {'debug': bool, 'ch': int}

    def __init__(self):
        self.debug = Callback.debug
        self.ch = Callback.ch

    @staticmethod
    def callback(self, interface):
        pass


def interface_info_refresh(interface, x=0, y=0):
    """
    Update stats for the Interface object passed to it.

    :param interface:
    :param x:
    :param y:
    :return:
    """

    interface.debug_pad.addstr(0, 0, 'CURRENT:    {}'.format(' ' * 75))
    interface.debug_pad.addstr(1, 0, 'CURSOR:     {}'.format(' ' * 75))
    interface.debug_pad.addstr(2, 0, 'SCURSOR:    {}'.format(' ' * 75))
    interface.debug_pad.addstr(3, 0, 'CH:         {}'.format(' ' * 75))
    interface.debug_pad.addstr(4, 0, 'CHAR:       {}'.format(' ' * 75))
    interface.debug_pad.addstr(5, 0, 'MOUSE:      {}'.format(' ' * 75))
    interface.debug_pad.addstr(6, 0, 'LINE NO:    {}'.format(' ' * 75))
    interface.debug_pad.addstr(7, 0, 'LINES:      {}'.format(' ' * 75))

    interface.debug_pad.addstr(0, 0, 'CURRENT:    {}'.format(interface.current_line))
    interface.debug_pad.addstr(1, 0, 'CURSOR:     {}, {}'.format(interface.cursor.x, interface.cursor.y))
    interface.debug_pad.addstr(2, 0, 'SCURSOR:    {}, {}'.format(interface.stdscr.cursor.x, interface.stdscr.cursor.y))
    interface.debug_pad.addstr(3, 0, 'CH:         {}'.format(interface.ch))
    interface.debug_pad.addstr(4, 0, 'CHAR:       {}'.format(chr(interface.ch)))
    interface.debug_pad.addstr(5, 0, 'MOUSE:      {}, {}'.format(str(interface.mouse.x), str(interface.mouse.y)))
    interface.debug_pad.addstr(6, 0, 'LINE NO:    {}'.format(interface.line_no))
    interface.debug_pad.addstr(7, 0, 'LINES:      {}'.format(interface.lines))

    interface.stdscr.move(y, x)


def string_insert(string, i, x):
    start = string[:i]
    finish = string[i:]
    return start + x + finish


def string_remove(string, i):
    return string[:i - 1] + string[i:]


def update_line(string, interface):
    interface.current_line = string
    interface.lines[interface.line_no] = interface.current_line
    return

