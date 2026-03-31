from datetime import date, time, timedelta

from pawpal_system import Owner, Pet, Task, Priority, Scheduler


def test_task_mark_complete():
    task = Task(
        title="Evening walk",
        pet_name="Mochi",
        task_type="walk",
        duration_minutes=30,
        priority=Priority.medium,
        due_date=date.today(),
        due_time=time(hour=18, minute=0),
        recurrence="daily",
    )

    assert not task.completed
    next_task = task.mark_complete(completed_date=date.today())
    assert task.completed
    assert next_task is not None
    assert next_task.due_date == date.today() + timedelta(days=1)
    assert not next_task.completed


def test_sort_and_filter_tasks():
    owner = Owner(name="Sam")
    pet = Pet(name="Rex", species="dog")
    owner.add_pet(pet)
    tasks = [
        Task(title="Lunchtime", pet_name="Rex", task_type="feeding", duration_minutes=10, due_date=date.today(), due_time=time(hour=12, minute=0)),
        Task(title="Morning", pet_name="Rex", task_type="walk", duration_minutes=30, due_date=date.today(), due_time=time(hour=8, minute=0)),
        Task(title="Afternoon", pet_name="Rex", task_type="play", duration_minutes=15, due_date=date.today(), due_time=time(hour=15, minute=0), completed=True),
    ]
    for t in tasks:
        owner.add_task(t)

    scheduler = Scheduler(owner=owner)
    sorted_tasks = scheduler.sort_tasks_by_time(pet.tasks)
    assert [t.title for t in sorted_tasks] == ["Morning", "Lunchtime", "Afternoon"]

    filtered = scheduler.filter_tasks(sorted_tasks, pet_name="Rex", completed=False)
    assert [t.title for t in filtered] == ["Morning", "Lunchtime"]


def test_add_task_increases_pet_tasks():
    owner = Owner(name="Sam")
    pet = Pet(name="Rex", species="dog")
    owner.add_pet(pet)

    assert len(pet.tasks) == 0

    task = Task(
        title="Feed",
        pet_name="Rex",
        task_type="feeding",
        duration_minutes=10,
        priority=Priority.high,
        due_date=date.today(),
    )

    owner.add_task(task)
    assert len(pet.tasks) == 1
