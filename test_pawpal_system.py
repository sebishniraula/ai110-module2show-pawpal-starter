from datetime import date, time

import pytest

from pawpal_system import Owner, Pet, Task, Priority, Scheduler


def test_owner_add_pet_and_task():
    owner = Owner(name="Alex")
    pet = Pet(name="Buddy", species="dog")
    owner.add_pet(pet)

    task = Task(
        title="Feed",
        pet_name="Buddy",
        task_type="feeding",
        duration_minutes=10,
        priority=Priority.high,
        due_date=date.today(),
    )

    owner.add_task(task)
    assert len(owner.all_tasks_for_date(date.today())) == 1


def test_schedule_sorts_by_time_and_priority():
    owner = Owner(name="Alex")
    pet = Pet(name="Bella", species="cat")
    owner.add_pet(pet)

    owner.add_task(
        Task(
            title="Midday walk",
            pet_name="Bella",
            task_type="walk",
            duration_minutes=20,
            due_date=date.today(),
            due_time=time(hour=12, minute=0),
            priority=Priority.medium,
        )
    )
    owner.add_task(
        Task(
            title="Morning feeding",
            pet_name="Bella",
            task_type="feeding",
            duration_minutes=15,
            due_date=date.today(),
            due_time=time(hour=8, minute=0),
            priority=Priority.high,
        )
    )

    scheduler = Scheduler(owner=owner)
    schedule = scheduler.build_daily_schedule(date.today())

    assert schedule[0].task.title == "Morning feeding"
    assert schedule[1].task.title == "Midday walk"


def test_conflict_detection_identifies_overlap():
    owner = Owner(name="Sam")
    pet = Pet(name="Rex", species="dog")
    owner.add_pet(pet)

    owner.add_task(
        Task(
            title="Walk",
            pet_name="Rex",
            task_type="walk",
            duration_minutes=30,
            due_date=date.today(),
            due_time=time(hour=9, minute=0),
        )
    )
    owner.add_task(
        Task(
            title="Groom",
            pet_name="Rex",
            task_type="grooming",
            duration_minutes=20,
            due_date=date.today(),
            due_time=time(hour=9, minute=15),
        )
    )

    scheduler = Scheduler(owner=owner)
    schedule = scheduler.build_daily_schedule(date.today())
    conflicts = scheduler.detect_conflicts(schedule)

    assert len(conflicts) == 1
    assert conflicts[0][0].task.title == "Walk"
    assert conflicts[0][1].task.title == "Groom"


def test_recurring_task_appears_daily():
    owner = Owner(name="Kim")
    pet = Pet(name="Nala", species="cat")
    owner.add_pet(pet)

    owner.add_task(
        Task(
            title="Morning cuddle",
            pet_name="Nala",
            task_type="bonding",
            duration_minutes=10,
            priority=Priority.low,
            due_date=date.today(),
            recurrence="daily",
        )
    )

    schedule = Scheduler(owner=owner).build_daily_schedule(date.today())
    assert any(t.task.title == "Morning cuddle" for t in schedule)
