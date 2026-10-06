import math
import os
from curses import wrapper
import curses

import numpy as np

MAX_MARK = 20.0 

class Student:
    def __init__(self, student_id, name, dob):
        self.id = student_id
        self.name = name
        self.dob = dob

    def __str__(self):
        return f"{self.id:<12}{self.name:<28}{self.dob:<12}"


class Course:
    def __init__(self, course_id, name, credits):
        self.id = course_id
        self.name = name
        self.credits = credits

    def __str__(self):
        return f"{self.id:<12}{self.name:<28}{self.credits:<8}"


class MarkBook:

    def __init__(self):
        self.students = []
        self.courses = []
        self.marks = {}  # {course_id: {student_id: mark}}

    # ---- lookups -----------------------------------------------------
    def find_student(self, student_id):
        return next((s for s in self.students if s.id == student_id), None)

    def find_course(self, course_id):
        return next((c for c in self.courses if c.id == course_id), None)

    # ---- adding data -------------------------------------------------
    def add_student(self, student):
        if self.find_student(student.id):
            raise ValueError(f"Student ID '{student.id}' already exists.")
        self.students.append(student)

    def add_course(self, course):
        if self.find_course(course.id):
            raise ValueError(f"Course ID '{course.id}' already exists.")
        self.courses.append(course)
        self.marks[course.id] = {}

    # ---- marks (math.floor) -----------------------------------------
    @staticmethod
    def floor_mark(mark):
        """Round DOWN to 1 decimal digit, e.g. 15.79 -> 15.7.
        round(..., 9) removes float noise such as 8.2*10 = 81.99999999."""
        return math.floor(round(mark * 10, 9)) / 10

    def set_mark(self, course_id, student_id, raw_mark):
        if not 0 <= raw_mark <= MAX_MARK:
            raise ValueError(f"Mark must be between 0 and {MAX_MARK:g}.")
        mark = self.floor_mark(raw_mark)
        self.marks[course_id][student_id] = mark
        return mark

    def get_mark(self, course_id, student_id):
        return self.marks[course_id].get(student_id)

    # ---- GPA (numpy) -------------------------------------------------
    def gpa(self, student):
        """Weighted average: sum(mark * credits) / sum(credits)."""
        scores, credits = [], []
        for course in self.courses:
            mark = self.get_mark(course.id, student.id)
            if mark is not None:
                scores.append(mark)
                credits.append(course.credits)
        if not credits:
            return 0.0
        scores = np.array(scores, dtype=float)
        credits = np.array(credits, dtype=float)
        return float(np.sum(scores * credits) / np.sum(credits))

    def sort_by_gpa(self):
        """Sort the student list by GPA, highest first."""
        gpas = np.array([self.gpa(s) for s in self.students], dtype=float)
        order = np.argsort(-gpas, kind="stable")
        self.students = [self.students[i] for i in order]


# --------------------------------------------------------------------------
# curses helpers
# --------------------------------------------------------------------------
def safe_addstr(win, y, x, text, attr=0):
    """addstr that never crashes when text goes outside the window."""
    h, w = win.getmaxyx()
    if y < 0 or y >= h or x >= w - 1:
        return
    try:
        win.addstr(y, x, text[: w - x - 1], attr)
    except curses.error:
        pass


ENTER_KEYS = (10, 13, curses.KEY_ENTER)
QUIT_KEYS = (ord("q"), 27)


class UI:
    def __init__(self, scr, book):
        self.scr = scr
        self.book = book
        try:
            curses.curs_set(0)
        except curses.error:
            pass
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_CYAN, -1)                 # labels / title
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_CYAN)  # highlight
        curses.init_pair(3, curses.COLOR_RED, -1)                  # errors
        curses.init_pair(4, curses.COLOR_GREEN, -1)                # success
        curses.init_pair(5, curses.COLOR_YELLOW, -1)               # table header

    # ---- drawing -----------------------------------------------------
    def draw_header(self, title):
        self.scr.erase()
        _, w = self.scr.getmaxyx()
        banner = " STUDENT MARK MANAGEMENT ".center(w - 1)
        safe_addstr(self.scr, 0, 0, banner, curses.color_pair(2) | curses.A_BOLD)
        safe_addstr(self.scr, 2, 2, title, curses.color_pair(1) | curses.A_BOLD)
        safe_addstr(self.scr, 3, 2, "-" * (w - 5))

    def footer(self, text):
        h, _ = self.scr.getmaxyx()
        safe_addstr(self.scr, h - 1, 2, text, curses.A_DIM)

    def notify(self, text, kind="ok"):
        """Show a message on the bottom lines and wait for a key."""
        h, _ = self.scr.getmaxyx()
        color = curses.color_pair(4 if kind == "ok" else 3) | curses.A_BOLD
        self.scr.move(h - 2, 0)
        self.scr.clrtoeol()
        safe_addstr(self.scr, h - 2, 2, text, color)
        self.footer("Press any key to continue...")
        self.scr.refresh()
        self.scr.getch()

    # ---- input -------------------------------------------------------
    def ask(self, row, label, required=True):
        while True:
            self.scr.move(row, 0)
            self.scr.clrtoeol()
            safe_addstr(self.scr, row, 2, label, curses.color_pair(1))
            col = 2 + len(label) + 1
            curses.echo()
            try:
                curses.curs_set(1)
            except curses.error:
                pass
            self.scr.refresh()
            raw = self.scr.getstr(row, col, 40)
            curses.noecho()
            try:
                curses.curs_set(0)
            except curses.error:
                pass
            text = raw.decode("utf-8", errors="replace").strip()
            if text or not required:
                return text
            self.notify("This field cannot be empty.", "error")

    def ask_number(self, row, label, cast, minimum=None, maximum=None):
        while True:
            raw = self.ask(row, label)
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
                self.notify(f"Invalid input. Please enter {kind}{rng}.", "error")

    # ---- generic widgets --------------------------------------------
    def menu(self, title, options, hotkeys=False):
        """Arrow-key menu. Returns the chosen index, or -1 on q / ESC."""
        sel = 0
        while True:
            self.draw_header(title)
            h, w = self.scr.getmaxyx()
            visible = max(1, h - 7)
            top = max(0, sel - visible + 1)
            for i, opt in enumerate(options[top: top + visible]):
                idx = top + i
                attr = curses.color_pair(2) if idx == sel else 0
                safe_addstr(self.scr, 5 + i, 4, f" {opt} ".ljust(min(60, w - 8)), attr)
            self.footer("Up/Down: move   Enter: select   q: back")
            self.scr.refresh()

            key = self.scr.getch()
            if key == curses.KEY_UP:
                sel = (sel - 1) % len(options)
            elif key == curses.KEY_DOWN:
                sel = (sel + 1) % len(options)
            elif key in ENTER_KEYS:
                return sel
            elif key in QUIT_KEYS:
                return -1
            elif hotkeys and 48 <= key <= 57:
                for i, opt in enumerate(options):
                    if opt.startswith(chr(key)):
                        return i

    def show_table(self, title, header, rows):
        """Scrollable table."""
        offset = 0
        while True:
            self.draw_header(title)
            h, w = self.scr.getmaxyx()
            page = max(1, h - 8)
            safe_addstr(self.scr, 4, 2, header, curses.color_pair(5) | curses.A_BOLD)
            safe_addstr(self.scr, 5, 2, "-" * (w - 5))
            for i, row in enumerate(rows[offset: offset + page]):
                safe_addstr(self.scr, 6 + i, 2, row)
            shown_to = min(offset + page, len(rows))
            self.footer(f"Up/Down: scroll   q/Enter: back   [{shown_to}/{len(rows)}]")
            self.scr.refresh()

            key = self.scr.getch()
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

    # ---- pickers -----------------------------------------------------
    def choose_course(self, title):
        if not self.book.courses:
            self.notify("No courses have been added yet.", "error")
            return None
        options = [f"{c.id} - {c.name} ({c.credits} credits)" for c in self.book.courses]
        idx = self.menu(title, options)
        return None if idx == -1 else self.book.courses[idx]

    def choose_student(self, title):
        if not self.book.students:
            self.notify("No students have been added yet.", "error")
            return None
        options = [f"{s.id} - {s.name}" for s in self.book.students]
        idx = self.menu(title, options)
        return None if idx == -1 else self.book.students[idx]

    # ---- actions -----------------------------------------------------
    def input_students(self):
        self.draw_header("Input students")
        n = self.ask_number(5, "Number of students:", int, minimum=1)
        for i in range(n):
            self.draw_header(f"Student {i + 1} of {n}")
            while True:
                sid = self.ask(5, "Student ID:")
                if self.book.find_student(sid):
                    self.notify(f"ID '{sid}' already exists.", "error")
                    continue
                break
            name = self.ask(6, "Name:")
            dob = self.ask(7, "DoB (DD/MM/YYYY):")
            self.book.add_student(Student(sid, name, dob))
        self.notify(f"Added {n} student(s).")

    def input_courses(self):
        self.draw_header("Input courses")
        n = self.ask_number(5, "Number of courses:", int, minimum=1)
        for i in range(n):
            self.draw_header(f"Course {i + 1} of {n}")
            while True:
                cid = self.ask(5, "Course ID:")
                if self.book.find_course(cid):
                    self.notify(f"ID '{cid}' already exists.", "error")
                    continue
                break
            name = self.ask(6, "Course name:")
            credits = self.ask_number(7, "Credits:", int, minimum=1)
            self.book.add_course(Course(cid, name, credits))
        self.notify(f"Added {n} course(s).")

    def input_marks(self):
        if not self.book.students or not self.book.courses:
            self.notify("Add students and courses before entering marks.", "error")
            return
        course = self.choose_course("Select a course to enter marks for")
        if course is None:
            return
        total = len(self.book.students)
        for i, student in enumerate(self.book.students):
            self.draw_header(f"Marks for {course.name} ({course.id})")
            safe_addstr(self.scr, 5, 2, f"Student {i + 1}/{total}: {student.name} (ID: {student.id})")
            raw = self.ask_number(7, f"Mark (0-{MAX_MARK:g}):", float, 0, MAX_MARK)
            self.book.set_mark(course.id, student.id, raw)
        self.show_course_marks(course)

    def list_students(self):
        if not self.book.students:
            self.notify("No students have been added yet.", "error")
            return
        header = f"{'ID':<12}{'Name':<28}{'DoB':<12}"
        self.show_table("List of students", header, [str(s) for s in self.book.students])

    def list_courses(self):
        if not self.book.courses:
            self.notify("No courses have been added yet.", "error")
            return
        header = f"{'ID':<12}{'Name':<28}{'Credits':<8}"
        self.show_table("List of courses", header, [str(c) for c in self.book.courses])

    def show_course_marks(self, course=None):
        if course is None:
            course = self.choose_course("Select a course to view marks")
            if course is None:
                return
        header = f"{'ID':<12}{'Name':<28}{'Mark':<8}"
        rows = []
        for s in self.book.students:
            mark = self.book.get_mark(course.id, s.id)
            rows.append(f"{s.id:<12}{s.name:<28}{'N/A' if mark is None else f'{mark:.1f}':<8}")
        if not rows:
            self.notify("No students have been added yet.", "error")
            return
        self.show_table(f"Marks for {course.name} ({course.id})", header, rows)

    def show_student_gpa(self):
        student = self.choose_student("Select a student to view GPA")
        if student is None:
            return
        header = f"{'Course':<28}{'Credits':<10}{'Mark':<8}"
        rows = []
        for c in self.book.courses:
            mark = self.book.get_mark(c.id, student.id)
            rows.append(f"{c.name:<28}{c.credits:<10}{'N/A' if mark is None else f'{mark:.1f}':<8}")
        rows += ["", f"GPA (credit-weighted): {self.book.gpa(student):.2f}"]
        self.show_table(f"GPA of {student.name} ({student.id})", header, rows)

    def show_ranking(self):
        if not self.book.students:
            self.notify("No students have been added yet.", "error")
            return
        self.book.sort_by_gpa()
        header = f"{'#':<5}{'ID':<12}{'Name':<28}{'GPA':<8}"
        rows = [f"{i:<5}{s.id:<12}{s.name:<28}{self.book.gpa(s):<8.2f}"
                for i, s in enumerate(self.book.students, start=1)]
        self.show_table("Students sorted by GPA (descending)", header, rows)

    # ---- main loop ---------------------------------------------------
    def run(self):
        entries = [
            ("1. Input students", self.input_students),
            ("2. Input courses", self.input_courses),
            ("3. Input marks for a course", self.input_marks),
            ("4. List students", self.list_students),
            ("5. List courses", self.list_courses),
            ("6. Show student marks for a course", self.show_course_marks),
            ("7. Show GPA of a student", self.show_student_gpa),
            ("8. Students sorted by GPA (descending)", self.show_ranking),
            ("0. Exit", None),
        ]
        labels = [label for label, _ in entries]
        while True:
            idx = self.menu("Main menu", labels, hotkeys=True)
            if idx == -1 or entries[idx][1] is None:
                return
            entries[idx][1]()


def main(stdscr):
    UI(stdscr, MarkBook()).run()


if __name__ == "__main__":
    os.environ.setdefault("ESCDELAY", "25")  # make ESC respond instantly
    wrapper(main)
    print("Exiting program")
