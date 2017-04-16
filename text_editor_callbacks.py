from common import *


class Unregistered(Callback):
    """
    Handle tapping any other key that doesn't have a registered callback.
    """

    debug = True
    ch = -1

    def __init__(self):
        self.debug = Unregistered.debug
        self.ch = Unregistered.ch

    def callback(self, interface):
        """
        Handle tapping any unregistered keys.

        :param interface:
        :return:
        """

        cursor_y, cursor_x = interface.cursor.y, interface.cursor.x

        try:
            chr_ch = chr(interface.ch)
        except ValueError:
            return True

        interface.current_line = string_insert(interface.current_line, cursor_x, chr_ch)
        interface.lines[interface.line_no] = interface.current_line
        interface.stdscr.addstr(interface.cursor.y, interface.cursor.x, chr_ch)

        interface.refresh()

        # Run debug if possible.
        if Unregistered.debug:
            interface_info_refresh(interface)

        interface.stdscr.move(cursor_y, cursor_x + 1)
        # interface.stdscr.move_cursor(cursor_x + 1, cursor_y)
        return True


class CntrlRightArrow(Callback):

    debug = True
    ch = 27

    def __init__(self):
        self.debug = CntrlRightArrow.debug
        self.ch = CntrlRightArrow.ch

    def callback(self, interface):
        cursor_x, cursor_y = len(interface.current_line), interface.cursor.y
        interface.stdscr.move(cursor_y, cursor_x)
        # interface.stdscr.move_cursor(cursor_x, cursor_y)

        if CntrlRightArrow.debug:
            interface_info_refresh(interface, cursor_x, cursor_y)

        return True


class CntrlLeftArrow(Callback):

    debug = True
    ch = 26

    def __init__(self):
        self.debug = CntrlLeftArrow.debug
        self.ch = CntrlLeftArrow.ch

    def callback(self, interface):
        cursor_x, cursor_y = 0, interface.cursor.y
        interface.stdscr.move(cursor_y, cursor_x)
        # interface.stdscr.move_cursor(cursor_x, cursor_y)

        if CntrlLeftArrow.debug:
            interface_info_refresh(interface, cursor_x, cursor_y)

        return True


class Mouse1(Callback):

    debug = True
    ch = 409

    def __init__(self):
        self.debug = Mouse1.debug
        self.ch = Mouse1.ch

    def callback(self, interface):
        mouse = interface.mouse

        current_line_no = mouse.y
        if current_line_no > len(interface.lines) - 1:
            return True

        if Mouse1.debug:
            interface_info_refresh(interface, mouse.x, mouse.y)

        interface.line_no = mouse.y

        interface.current_line = interface.lines[mouse.y]

        cl_len = len(interface.current_line)
        if mouse.x >= cl_len:
            interface.stdscr.move(mouse.y, cl_len)
            interface.cursor.y, interface.cursor.x = mouse.y, 0
        else:
            interface.stdscr.move_cursor(mouse.y, mouse.x)
            # interface.stdscr.move_cursor(mouse.x, mouse.y)
            interface.cursor.y, interface.cursor.x = mouse.y, mouse.x

        return True


class Backspace(Callback):
    """
    Handle tapping the backspace key.
    """

    debug = True
    ch = 127

    def __init__(self):
        self.debug = Backspace.debug
        self.ch = Backspace.ch

    def callback(self, interface):
        """
        Handle tapping the backspace key.

        :param interface:
        :return:
        """

        cursor_y, cursor_x = interface.cursor.y, interface.cursor.x

        # Cannot go any further back.
        if cursor_x == 0 and cursor_y == 0:
            return True

        # Beginning of current line needs to wrap backwards.
        if cursor_x == 0:
            try:
                end = interface.lines.pop(interface.line_no)
            except IndexError:
                end = ''
                pass

            interface.stdscr.addstr(cursor_y, 0, ' ' * len(end))
            interface.line_no -= 1
            cl = interface.lines[interface.line_no]
            update_line(cl, interface)

            # move cursor to end of last line.
            # add the current line to the end of the last line.
            interface.stdscr.addstr(cursor_y, 0, ' ' * len(cl))
            interface.stdscr.addstr(cursor_y - 1, len(cl), end)
            update_line(interface.current_line + end, interface)

            interface.refresh()

            if Backspace.debug:
                interface_info_refresh(interface)

            interface.stdscr.move_cursor(len(interface.current_line) - len(end), cursor_y - 1)
            return True

        update_line(string_remove(interface.current_line, cursor_x), interface)
        interface.stdscr.addstr(cursor_y, 0, interface.current_line + ' ')
        interface.stdscr.addstr(cursor_y, cursor_x - 1, '')

        # Next 2 lines are paired.
        if Backspace.debug:
            interface_info_refresh(interface)

        interface.stdscr.move_cursor(cursor_x - 1, cursor_y)

        return True


class Space(Callback):
    """
    Handle tapping the space key.
    """

    debug = True
    ch = 32

    def __init__(self):
        self.debug = Space.debug
        self.ch = Space.ch

    def callback(self, interface):
        """
        Handle tapping the space key.

        :param interface:
        :return:
        """
        cursor_y, cursor_x = interface.cursor.y, interface.cursor.x

        if cursor_x < len(interface.current_line):
            update_line(string_insert(interface.current_line, cursor_x, ' '), interface)
            interface.stdscr.addstr(cursor_y, cursor_x - 1, '{}'.format(interface.current_line[cursor_x - 1:]))

            if Space.debug:
                interface_info_refresh(interface)

            interface.stdscr.move_cursor(cursor_x + 1, cursor_y)
            return True

        update_line(interface.current_line + ' ', interface)
        interface.stdscr.addstr(cursor_y, cursor_x, ' ')

        if Space.debug:
            interface_info_refresh(interface)
        interface.stdscr.move_cursor(cursor_x + 1, cursor_y)

        return True


class Enter(Callback):
    """
    Handle tapping the enter key.
    """

    debug = True
    ch = 10

    def __init__(self):
        self.debug = Enter.debug
        self.ch = Enter.ch

    def callback(self, interface):
        """
        Handle tapping the enter key.

        :param interface:
        :return:
        """

        cursor_y, cursor_x = interface.cursor.y, interface.cursor.x

        # Handle wrapped text.
        if cursor_x < len(interface.current_line):
            # Get the remainder of the line.
            remainder = interface.current_line[cursor_x:]
            old_line = interface.current_line[:cursor_x]

            # Insert a new blank line into the interfaces "lines" list.
            interface.lines.insert(interface.line_no + 1, '')
            # Update the current line to match the old line(previous line).
            update_line(old_line, interface)
            # Increment the current line number and then update that line
            # to match the remainder of the line.
            interface.line_no += 1
            update_line(remainder, interface)

            # Add a new line and return plus the remainder to the screen.
            interface.stdscr.addstr('\n\r' + remainder)
            interface.stdscr.addstr(cursor_y + 1, 0, '')

            interface.refresh()

            if Enter.debug:
                interface_info_refresh(interface, 0, cursor_y + 1)
            interface.stdscr.move_cursor(0, cursor_y + 1)

            del remainder
            del old_line
            return True

        update_line(interface.current_line, interface)
        interface.line_no += 1
        interface.lines.insert(interface.line_no, '')
        update_line('', interface)
        # interface.lines[interface.line_no] = ''
        interface.refresh()

        if Enter.debug:
            interface_info_refresh(interface, 0, cursor_y + 1)

        interface.pad_pos += 1
        interface.pad.refresh(interface.pad_pos, 0, 5, 5, 10, 60)

        interface.stdscr.move_cursor(0, cursor_y + 1)
        return True


class ArrowUp(Callback):
    """
    Handle tapping the up arrow key.
    """

    debug = True
    ch = 259

    def __init__(self):
        self.debug = ArrowUp.debug
        self.ch = ArrowUp.ch

    def callback(self, interface):
        """
        Handle tapping the up arrow key.

        :param interface:
        :return:
        """

        cursor_y, cursor_x = interface.cursor.y, interface.cursor.x

        if cursor_y == 0 or interface.line_no == 0:
            if ArrowUp.debug:
                interface_info_refresh(interface, cursor_x, cursor_y)
            return True

        interface.line_no -= 1
        interface.current_line = interface.lines[interface.line_no]

        if ArrowUp.debug:
            interface_info_refresh(interface)

        previous_line_len = len(interface.lines[interface.line_no])
        move_x = previous_line_len if cursor_x > previous_line_len else cursor_x
        interface.stdscr.move_cursor(move_x, cursor_y - 1)

        return True


class ArrowDown(Callback):

    debug = True
    ch = 258

    def __init__(self):
        self.debug = ArrowDown.debug
        self.ch = ArrowDown.ch

    def callback(self, interface):
        """
        Handle tapping the down arrow key.

        :param interface:
        :return:
        """

        cursor_y, cursor_x = interface.cursor.y, interface.cursor.x
        if len(interface.lines) <= interface.line_no + 1:
            if ArrowDown.debug:
                interface_info_refresh(interface, cursor_x, cursor_y)
            return True
        try:
            interface.current_line = interface.lines[interface.line_no + 1]
            interface.stdscr.move_cursor(len(interface.current_line), cursor_y + 1)
            interface.line_no += 1
        except IndexError:
            pass

        next_line_len = len(interface.lines[interface.line_no])
        move_x = next_line_len if cursor_x > next_line_len else cursor_x

        if ArrowDown.debug:
            interface_info_refresh(interface, move_x, cursor_y + 1)

        interface.stdscr.move_cursor(move_x, cursor_y + 1)

        return True


class ArrowLeft(Callback):

    debug = True
    ch = 260

    def __init__(self):
        self.debug = ArrowLeft.debug
        self.ch = ArrowLeft.ch

    def callback(self, interface):
        """
        Handle tapping the left arrow key.

        :param interface:
        :return:
        """

        cursor_y, cursor_x = interface.cursor.y, interface.cursor.x

        if cursor_x == 0 and cursor_y == 0:
            if ArrowLeft.debug:
                interface_info_refresh(interface, 0, 0)
            return True
        if cursor_x == 0:
            if ArrowLeft.debug:
                interface_info_refresh(interface, 0, cursor_y)

            interface.current_line = interface.lines[cursor_y - 1]
            interface.line_no = cursor_y - 1
            cll = len(interface.current_line)
            interface.stdscr.move_cursor(cll, cursor_y - 1)

            if ArrowLeft.debug:
                interface_info_refresh(interface, cll, cursor_y - 1)
            return True

        interface.stdscr.addstr(cursor_y, cursor_x - 1, '')

        if ArrowLeft.debug:
            interface_info_refresh(interface, cursor_x - 1, cursor_y)

        interface.stdscr.move_cursor(cursor_x - 1, cursor_y)

        return True


class ArrowRight(Callback):

    debug = True
    ch = 261

    def __init__(self):
        self.debug = ArrowRight.debug
        self.ch = ArrowRight.ch

    def callback(self, interface):
        """
        Handle tapping the right arrow key.

        :param interface:
        :return:
        """

        cursor_y, cursor_x = interface.cursor.y, interface.cursor.x

        current_line_length = len(interface.current_line)
        if cursor_x >= current_line_length:
            if ArrowRight.debug:
                interface_info_refresh(interface)

            # Check for the next line, if it isn't there block movement.
            try:
                interface.current_line = interface.lines[interface.line_no + 1]
            except IndexError:
                interface.stdscr.move_cursor(current_line_length, cursor_y)
                return True

            # Move the cursor to the start of the next line.
            interface.stdscr.move_cursor(0, cursor_y + 1)
            interface.line_no = cursor_y + 1
            return True

        interface.stdscr.move_cursor(cursor_x + 1, cursor_y)

        if ArrowRight.debug:
            interface_info_refresh(interface, cursor_x + 1, cursor_y)

        return True
