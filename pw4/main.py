
import os
from curses import wrapper

import input as inp          # our own module (not the built-in input())
import output as out
from domains import MarkBook


# ---- menu actions (each takes the screen and the MarkBook) -----------
def do_input_students(scr, book):
    inp.input_students(scr, book)


def do_input_courses(scr, book):
    inp.input_courses(scr, book)


def do_input_marks(scr, book):
    course = inp.input_marks(scr, book)
    if course is not None:
        out.show_course_marks(scr, book, course)


def do_list_students(scr, book):
    out.show_students(scr, book)


def do_list_courses(scr, book):
    out.show_courses(scr, book)


def do_show_marks(scr, book):
    course = inp.choose_course(scr, book, "Select a course to view marks")
    if course is not None:
        out.show_course_marks(scr, book, course)


def do_show_gpa(scr, book):
    student = inp.choose_student(scr, book, "Select a student to view GPA")
    if student is not None:
        out.show_student_gpa(scr, book, student)


def do_ranking(scr, book):
    book.sort_by_gpa()
    out.show_ranking(scr, book)


ENTRIES = [
    ("1. Input students", do_input_students),
    ("2. Input courses", do_input_courses),
    ("3. Input marks for a course", do_input_marks),
    ("4. List students", do_list_students),
    ("5. List courses", do_list_courses),
    ("6. Show student marks for a course", do_show_marks),
    ("7. Show GPA of a student", do_show_gpa),
    ("8. Students sorted by GPA (descending)", do_ranking),
    ("0. Exit", None),
]


def main(scr):
    out.init_ui()
    book = MarkBook()
    labels = [label for label, _ in ENTRIES]
    while True:
        idx = inp.menu(scr, "Main menu", labels, hotkeys=True)
        if idx == -1 or ENTRIES[idx][1] is None:
            return
        ENTRIES[idx][1](scr, book)


if __name__ == "__main__":
    os.environ.setdefault("ESCDELAY", "25")  # make ESC respond instantly
    wrapper(main)
    print("Exiting program. Don't forget to push your work to your GitHub repository!")
