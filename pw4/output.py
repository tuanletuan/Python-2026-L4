"""Module for all curses OUTPUT (drawing, messages, tables)."""
import curses

ENTER_KEYS = (10, 13, curses.KEY_ENTER)
QUIT_KEYS = (ord("q"), 27)


def init_ui():
    """Call once after curses has started."""
    try:
        curses.curs_set(0)
    except curses.error:
        pass
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_CYAN, -1)                  # labels / title
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_CYAN)  # highlight
    curses.init_pair(3, curses.COLOR_RED, -1)                   # errors
    curses.init_pair(4, curses.COLOR_GREEN, -1)                 # success
    curses.init_pair(5, curses.COLOR_YELLOW, -1)                # table header


def safe_addstr(scr, y, x, text, attr=0):
    """addstr that never crashes when text goes outside the window."""
    h, w = scr.getmaxyx()
    if y < 0 or y >= h or x >= w - 1:
        return
    try:
        scr.addstr(y, x, text[: w - x - 1], attr)
    except curses.error:
        pass


def draw_header(scr, title):
    scr.erase()
    _, w = scr.getmaxyx()
    banner = " STUDENT MARK MANAGEMENT ".center(w - 1)
    safe_addstr(scr, 0, 0, banner, curses.color_pair(2) | curses.A_BOLD)
    safe_addstr(scr, 2, 2, title, curses.color_pair(1) | curses.A_BOLD)
    safe_addstr(scr, 3, 2, "-" * (w - 5))


def footer(scr, text):
    h, _ = scr.getmaxyx()
    safe_addstr(scr, h - 1, 2, text, curses.A_DIM)


def notify(scr, text, kind="ok"):
    """Show a message on the bottom lines and wait for a key."""
    h, _ = scr.getmaxyx()
    color = curses.color_pair(4 if kind == "ok" else 3) | curses.A_BOLD
    scr.move(h - 2, 0)
    scr.clrtoeol()
    safe_addstr(scr, h - 2, 2, text, color)
    footer(scr, "Press any key to continue...")
    scr.refresh()
    scr.getch()


# ---- generic scrollable table -----------------------------------------
def show_table(scr, title, header, rows):
    offset = 0
    while True:
        draw_header(scr, title)
        h, w = scr.getmaxyx()
        page = max(1, h - 8)
        safe_addstr(scr, 4, 2, header, curses.color_pair(5) | curses.A_BOLD)
        safe_addstr(scr, 5, 2, "-" * (w - 5))
        for i, row in enumerate(rows[offset: offset + page]):
            safe_addstr(scr, 6 + i, 2, row)
        shown_to = min(offset + page, len(rows))
        footer(scr, f"Up/Down: scroll   q/Enter: back   [{shown_to}/{len(rows)}]")
        scr.refresh()

        key = scr.getch()
        if key in QUIT_KEYS or key in ENTER_KEYS:
            return
        if key == curses.KEY_DOWN and offset + page < len(rows):
            offset += 1
        elif key == curses.KEY_UP and offset > 0:
            offset -= 1
        elif key == curses.KEY_NPAGE and offset + page < len(rows):
            offset = min(offset + page, max(0, len(rows) - page))
        elif key == curses.KEY_PPAGE:
            offset = max(0, offset - page)


# ---- specific views ---------------------------------------------------
def show_students(scr, book):
    if not book.students:
        notify(scr, "No students have been added yet.", "error")
        return
    header = f"{'ID':<12}{'Name':<28}{'DoB':<12}"
    show_table(scr, "List of students", header, [str(s) for s in book.students])


def show_courses(scr, book):
    if not book.courses:
        notify(scr, "No courses have been added yet.", "error")
        return
    header = f"{'ID':<12}{'Name':<28}{'Credits':<8}"
    show_table(scr, "List of courses", header, [str(c) for c in book.courses])


def show_course_marks(scr, book, course):
    if not book.students:
        notify(scr, "No students have been added yet.", "error")
        return
    header = f"{'ID':<12}{'Name':<28}{'Mark':<8}"
    rows = []
    for s in book.students:
        mark = book.get_mark(course.id, s.id)
        text = "N/A" if mark is None else f"{mark:.1f}"
        rows.append(f"{s.id:<12}{s.name:<28}{text:<8}")
    show_table(scr, f"Marks for {course.name} ({course.id})", header, rows)


def show_student_gpa(scr, book, student):
    header = f"{'Course':<28}{'Credits':<10}{'Mark':<8}"
    rows = []
    for c in book.courses:
        mark = book.get_mark(c.id, student.id)
        text = "N/A" if mark is None else f"{mark:.1f}"
        rows.append(f"{c.name:<28}{c.credits:<10}{text:<8}")
    rows += ["", f"GPA (credit-weighted): {book.gpa(student):.2f}"]
    show_table(scr, f"GPA of {student.name} ({student.id})", header, rows)


def show_ranking(scr, book):
    """Expects book.students to be already sorted by GPA."""
    if not book.students:
        notify(scr, "No students have been added yet.", "error")
        return
    header = f"{'#':<5}{'ID':<12}{'Name':<28}{'GPA':<8}"
    rows = [f"{i:<5}{s.id:<12}{s.name:<28}{book.gpa(s):<8.2f}"
            for i, s in enumerate(book.students, start=1)]
    show_table(scr, "Students sorted by GPA (descending)", header, rows)
