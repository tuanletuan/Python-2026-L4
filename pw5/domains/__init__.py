"""Package containing the domain classes."""
from .student import Student
from .course import Course
from .markbook import MarkBook, MAX_MARK

__all__ = ["Student", "Course", "MarkBook", "MAX_MARK"]
