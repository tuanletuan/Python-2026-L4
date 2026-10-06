import curses
import output
from domains import Student, Course, MAX_MARK


def ask(scr, row, label, required=True):
    """Prompt for a line of text at the given row."""
    while True:
        scr.move(row, 0)
        scr.clrtoeol()
        output.safe_addstr(scr, row, 2, label, curses.color_pair(1))
        col = 2 + len(label) + 1
        curses.echo()
        try:
            curses.curs_set(1)
        except curses.error:
            pass
        scr.refresh()
        raw = scr.getstr(row, col, 40)
        curses.noecho()
        try:
            curses.curs_set(0)
        except curses.error:
            pass
        text = raw.decode("utf-8", errors="replace").strip()
        if text or not required:
            return text
        output.notify(scr, "This field cannot be empty.", "error")


def ask_number(scr, row, label, cast, minimum=None, maximum=None):
    """Prompt until a valid int/float (within optional bounds) is entered."""
    while True:
        raw = ask(scr, row, label)
        try:
            value = cast(raw)
            if minimum is not None and value < minimum:
                raise ValueError
            if maximum is not None and value > maximum:
                raise ValueError
            return value
        except ValueError:
            rng = ""
            if minimum is not None and maximum is not None:
                rng = f" between {minimum:g} and {maximum:g}"
            elif minimum is not None:
                rng = f" >= {minimum:g}"
            kind = "an integer" if cast is int else "a number"
            output.notify(scr, f"Invalid input. Please enter {kind}{rng}.", "error")


# ---- menus / pickers ---------------------------------------------------
def menu(scr, title, options, hotkeys=False):
    """Arrow-key menu. Returns the chosen index, or -1 on q / ESC."""
    sel = 0
    while True:
        output.draw_header(scr, title)
        h, w = scr.getmaxyx()
        visible = max(1, h - 7)
        top = max(0, sel - visible + 1)
        for i, opt in enumerate(options[top: top + visible]):
            attr = curses.color_pair(2) if top + i == sel else 0
            output.safe_addstr(scr, 5 + i, 4, f" {opt} ".ljust(min(60, w - 8)), attr)
        output.footer(scr, "Up/Down: move   Enter: select   q: back")
        scr.refresh()

        key = scr.getch()
        if key == curses.KEY_UP:
            sel = (sel - 1) % len(options)
        elif key == curses.KEY_DOWN:
            sel = (sel + 1) % len(options)
        elif key in output.ENTER_KEYS:
            return sel
        elif key in output.QUIT_KEYS:
            return -1
        elif hotkeys and 48 <= key <= 57:
            for i, opt in enumerate(options):
                if opt.startswith(chr(key)):
                    return i


def choose_course(scr, book, title):
    if not book.courses:
        output.notify(scr, "No courses have been added yet.", "error")
        return None
    options = [f"{c.id} - {c.name} ({c.credits} credits)" for c in book.courses]
    idx = menu(scr, title, options)
    return None if idx == -1 else book.courses[idx]


def choose_student(scr, book, title):
    if not book.students:
        output.notify(scr, "No students have been added yet.", "error")
        return None
    options = [f"{s.id} - {s.name}" for s in book.students]
    idx = menu(scr, title, options)
    return None if idx == -1 else book.students[idx]


# ---- data entry --------------------------------------------------------
def input_students(scr, book):
    output.draw_header(scr, "Input students")
    n = ask_number(scr, 5, "Number of students:", int, minimum=1)
    for i in range(n):
        output.draw_header(scr, f"Student {i + 1} of {n}")
        while True:
            sid = ask(scr, 5, "Student ID:")
            if book.find_student(sid):
                output.notify(scr, f"ID '{sid}' already exists.", "error")
                continue
            break
        name = ask(scr, 6, "Name:")
        dob = ask(scr, 7, "DoB (DD/MM/YYYY):")
        book.add_student(Student(sid, name, dob))
    output.notify(scr, f"Added {n} student(s).")


def input_courses(scr, book):
    output.draw_header(scr, "Input courses")
    n = ask_number(scr, 5, "Number of courses:", int, minimum=1)
    for i in range(n):
        output.draw_header(scr, f"Course {i + 1} of {n}")
        while True:
            cid = ask(scr, 5, "Course ID:")
            if book.find_course(cid):
                output.notify(scr, f"ID '{cid}' already exists.", "error")
                continue
            break
        name = ask(scr, 6, "Course name:")
        credits = ask_number(scr, 7, "Credits:", int, minimum=1)
        book.add_course(Course(cid, name, credits))
    output.notify(scr, f"Added {n} course(s).")


def input_marks(scr, book):
    """Enter marks for every student in a chosen course.
    Returns the course (so the caller can display it) or None."""
    if not book.students or not book.courses:
        output.notify(scr, "Add students and courses before entering marks.", "error")
        return None
    course = choose_course(scr, book, "Select a course to enter marks for")
    if course is None:
        return None
    total = len(book.students)
    for i, student in enumerate(book.students):
        output.draw_header(scr, f"Marks for {course.name} ({course.id})")
        output.safe_addstr(scr, 5, 2, f"Student {i + 1}/{total}: {student.name} (ID: {student.id})")
        raw = ask_number(scr, 7, f"Mark (0-{MAX_MARK:g}):", float, 0, MAX_MARK)
        book.set_mark(course.id, student.id, raw)
    return course
