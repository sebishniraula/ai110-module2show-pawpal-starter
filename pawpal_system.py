from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
from enum import IntEnum
from typing import List, Optional, Dict, Any, Tuple


class Priority(IntEnum):
    low = 1
    medium = 2
    high = 3


@dataclass
class Task:
    title: str
    pet_name: str
    task_type: str
    duration_minutes: int
    priority: Priority = Priority.medium
    due_date: Optional[date] = None
    due_time: Optional[time] = None
    recurrence: Optional[str] = None  # daily, weekly, monthly, etc.
    notes: str = ""
    completed: bool = False
    created_at: datetime = field(default_factory=datetime.now)

    def is_due_on(self, target_date: date) -> bool:
        """Return True when this task should occur on target_date."""
        if self.completed:
            return False

        if self.due_date and self.due_date != target_date:
            if self.recurrence == "daily":
                return self.due_date <= target_date
            if self.recurrence == "weekly":
                days = (target_date - self.due_date).days
                return self.due_date <= target_date and days % 7 == 0
            if self.recurrence == "monthly":
                return (
                    self.due_date <= target_date
                    and self.due_date.day == target_date.day
                )
            return False

        if self.due_date is None and self.recurrence:
            # tasks created without a date but recurring start from today
            if self.recurrence == "daily":
                return True

        if self.due_date is None and self.recurrence is None:
            # no date means flexible; due anytime
            return True

        return self.due_date == target_date if self.due_date else False

    def next_occurrence(self, from_date: date = date.today()) -> Optional[date]:
        """Calculate the next calendar date when the task should occur."""
        if self.completed:
            return None

        if self.due_date is None:
            return from_date

        if not self.recurrence:
            return self.due_date

        if self.due_date > from_date:
            return self.due_date

        if self.recurrence == "daily":
            return from_date

        if self.recurrence == "weekly":
            days = (from_date - self.due_date).days
            offset = days % 7
            return from_date if offset == 0 else from_date + timedelta(days=7 - offset)

        if self.recurrence == "monthly":
            # approximate next same day each month (not calendar-accurate for end-of-month)
            year = from_date.year
            month = from_date.month
            if from_date.day <= self.due_date.day:
                return date(year=year, month=month, day=self.due_date.day)

            month += 1
            if month > 12:
                month = 1
                year += 1
            try:
                return date(year=year, month=month, day=self.due_date.day)
            except ValueError:
                # fallback to last day of month
                next_first = date(year=year, month=month, day=1)
                return next_first - timedelta(days=1)

        return None


@dataclass
class Pet:
    name: str
    species: str
    age_years: Optional[int] = None
    medical_notes: str = ""
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet if the pet name matches."""
        if task.pet_name != self.name:
            raise ValueError("Task pet_name does not match this pet")
        self.tasks.append(task)

    def remove_task(self, task_title: str) -> bool:
        """Remove tasks with matching title and report if anything was removed."""
        start_len = len(self.tasks)
        self.tasks = [t for t in self.tasks if t.title != task_title]
        return len(self.tasks) < start_len

    def tasks_for_date(self, target_date: date) -> List[Task]:
        return [t for t in self.tasks if t.is_due_on(target_date)]


@dataclass
class Owner:
    name: str
    pets: List[Pet] = field(default_factory=list)
    preferences: Dict[str, Any] = field(default_factory=dict)

    def add_pet(self, pet: Pet) -> None:
        """Add a new pet to the owner, preventing duplicates by name."""
        if pet.name in {p.name for p in self.pets}:
            raise ValueError(f"Pet '{pet.name}' already exists for owner '{self.name}'")
        self.pets.append(pet)

    def get_pet(self, name: str) -> Optional[Pet]:
        for pet in self.pets:
            if pet.name == name:
                return pet
        return None

    def add_task(self, task: Task) -> None:
        pet = self.get_pet(task.pet_name)
        if not pet:
            raise ValueError(f"Pet '{task.pet_name}' not found")
        pet.add_task(task)

    def all_tasks_for_date(self, target_date: date) -> List[Task]:
        tasks: List[Task] = []
        for pet in self.pets:
            tasks.extend(pet.tasks_for_date(target_date))
        return tasks


@dataclass
class ScheduledTask:
    task: Task
    start_time: time
    end_time: time


class Scheduler:
    WORKDAY_START = time(8, 0)
    WORKDAY_END = time(20, 0)

    def __init__(self, owner: Owner):
        self.owner = owner

    def _time_to_minutes(self, t: time) -> int:
        return t.hour * 60 + t.minute

    def _minutes_to_time(self, m: int) -> time:
        h, m = divmod(m, 60)
        return time(hour=h, minute=m)

    def detect_conflicts(self, scheduled_tasks: List[ScheduledTask]) -> List[Tuple[ScheduledTask, ScheduledTask]]:
        """Detect overlapping scheduled tasks and return conflicting pairs."""
        conflicts = []
        sorted_tasks = sorted(scheduled_tasks, key=lambda st: st.start_time)

        for i in range(len(sorted_tasks) - 1):
            first = sorted_tasks[i]
            second = sorted_tasks[i + 1]
            if self._time_to_minutes(second.start_time) < self._time_to_minutes(first.end_time):
                conflicts.append((first, second))

        return conflicts

    def build_daily_schedule(self, target_date: date) -> List[ScheduledTask]:
        tasks = self.owner.all_tasks_for_date(target_date)

        fixed = [t for t in tasks if t.due_time is not None]
        flexible = [t for t in tasks if t.due_time is None]

        fixed_schedule: List[ScheduledTask] = []
        for task in fixed:
            start = task.due_time
            end_minutes = self._time_to_minutes(start) + task.duration_minutes
            end = self._minutes_to_time(end_minutes)
            fixed_schedule.append(ScheduledTask(task=task, start_time=start, end_time=end))

        fixed_schedule.sort(key=lambda st: st.start_time)

        # validate fixed tasks conflict
        conflicts = self.detect_conflicts(fixed_schedule)
        if conflicts:
            # For now, we do not raise; we include them and report later.
            pass

        # Build free intervals between workday, accommodating fixed tasks
        intervals = []
        current_start = self.WORKDAY_START

        for job in fixed_schedule:
            if self._time_to_minutes(job.start_time) > self._time_to_minutes(current_start):
                intervals.append((current_start, job.start_time))
            current_start = max(current_start, job.end_time)

        if self._time_to_minutes(current_start) < self._time_to_minutes(self.WORKDAY_END):
            intervals.append((current_start, self.WORKDAY_END))

        # schedule flexible tasks into intervals using priority and duration
        flexible.sort(key=lambda t: (-t.priority, t.created_at))
        flexible_schedule: List[ScheduledTask] = []

        for task in flexible:
            for i, (interval_start, interval_end) in enumerate(intervals):
                available = self._time_to_minutes(interval_end) - self._time_to_minutes(interval_start)
                if task.duration_minutes <= available:
                    start = interval_start
                    end = self._minutes_to_time(self._time_to_minutes(start) + task.duration_minutes)
                    flexible_schedule.append(ScheduledTask(task=task, start_time=start, end_time=end))

                    # update interval
                    new_start = end
                    if self._time_to_minutes(new_start) >= self._time_to_minutes(interval_end):
                        intervals.pop(i)
                    else:
                        intervals[i] = (new_start, interval_end)

                    break

        schedule = fixed_schedule + flexible_schedule
        schedule.sort(key=lambda st: st.start_time)
        return schedule

    def summarize_schedule(self, schedule: List[ScheduledTask]) -> str:
        lines = [f"Schedule for {self.owner.name}" + "\n"]
        for item in schedule:
            lines.append(
                f"{item.start_time.strftime('%H:%M')} - {item.end_time.strftime('%H:%M')}:"
                f" [{item.priority.name}] {item.task.task_type} for {item.task.pet_name} - {item.task.title}"
            )
        if not schedule:
            lines.append("No tasks scheduled for this day.")
        return "\n".join(lines)


def demo() -> None:
    owner = Owner(name="Jordan")
    dog = Pet(name="Mochi", species="dog", age_years=2)
    owner.add_pet(dog)

    owner.add_task(
        Task(
            title="Morning walk",
            pet_name="Mochi",
            task_type="walk",
            duration_minutes=30,
            priority=Priority.high,
            due_time=time(hour=8, minute=30),
            recurrence="daily",
            due_date=date.today(),
            notes="Use harness with blue leash",
        )
    )

    owner.add_task(
        Task(
            title="Evening meal",
            pet_name="Mochi",
            task_type="feeding",
            duration_minutes=15,
            priority=Priority.medium,
            recurrence="daily",
            due_time=time(hour=18, minute=0),
            due_date=date.today(),
        )
    )

    owner.add_task(
        Task(
            title="Pill (joint support)",
            pet_name="Mochi",
            task_type="medication",
            duration_minutes=5,
            priority=Priority.high,
            due_date=date.today(),
            recurrence="daily",
            due_time=time(hour=20, minute=0),
        )
    )

    owner.add_task(
        Task(
            title="Clean litter",
            pet_name="Mochi",
            task_type="maintenance",
            duration_minutes=10,
            priority=Priority.low,
            due_date=date.today(),
            recurrence="daily",
        )
    )

    scheduler = Scheduler(owner=owner)
    today = date.today()
    schedule = scheduler.build_daily_schedule(today)
    print(scheduler.summarize_schedule(schedule))

    conflicts = scheduler.detect_conflicts(schedule)
    if conflicts:
        print("\nConflicts detected:")
        for a, b in conflicts:
            print(f"- {a.task.title} overlaps with {b.task.title}")
    else:
        print("\nNo conflicts")


if __name__ == "__main__":
    demo()
