
import csv
import os
import zipfile

from domains import Student, Course

DATA_DIR = os.path.dirname(os.path.abspath(__file__))

STUDENTS_FILE = "students.txt"
COURSES_FILE = "courses.txt"
MARKS_FILE = "marks.txt"
ARCHIVE_FILE = "students.dat"
TEXT_FILES = (STUDENTS_FILE, COURSES_FILE, MARKS_FILE)


def _path(name):
    return os.path.join(DATA_DIR, name)



def _write_rows(name, rows):
    with open(_path(name), "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(rows)


def _read_rows(name):
    path = _path(name)
    if not os.path.exists(path):
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return [row for row in csv.reader(f) if row]



def save_students(book):
   
    _write_rows(STUDENTS_FILE, [(s.id, s.name, s.dob) for s in book.students])


def save_courses(book):
    
    _write_rows(COURSES_FILE, [(c.id, c.name, c.credits) for c in book.courses])


def save_marks(book):
    
    rows = [(cid, sid, f"{mark:.1f}")
            for cid, per_student in book.marks.items()
            for sid, mark in per_student.items()]
    _write_rows(MARKS_FILE, rows)



def compress_all():
    
    existing = [n for n in TEXT_FILES if os.path.exists(_path(n))]
    if not existing:
        return False
    tmp = _path(ARCHIVE_FILE + ".tmp")
    with zipfile.ZipFile(tmp, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for name in existing:
            zf.write(_path(name), arcname=name)
    os.replace(tmp, _path(ARCHIVE_FILE))  # replace only once fully written
    return True


def decompress():
    
    path = _path(ARCHIVE_FILE)
    if not os.path.exists(path):
        return False
    with zipfile.ZipFile(path) as zf:
        names = set(zf.namelist())
        for name in TEXT_FILES:  # only our known names -> no path tricks
            if name in names:
                with open(_path(name), "wb") as f:
                    f.write(zf.read(name))
    return True



def load_all(book):
    for row in _read_rows(STUDENTS_FILE):
        if len(row) == 3 and not book.find_student(row[0]):
            book.add_student(Student(*row))

    for row in _read_rows(COURSES_FILE):
        try:
            cid, name, credits = row
            if not book.find_course(cid):
                book.add_course(Course(cid, name, int(credits)))
        except ValueError:
            continue

    for row in _read_rows(MARKS_FILE):
        try:
            cid, sid, mark = row
            if book.find_course(cid) and book.find_student(sid):
                book.set_mark(cid, sid, float(mark))
        except ValueError:
            continue


def startup(book):
    
    restored, error = False, None
    try:
        restored = decompress()
    except zipfile.BadZipFile:
        error = f"{ARCHIVE_FILE} is corrupted and was ignored."
    load_all(book)
    return restored, error
