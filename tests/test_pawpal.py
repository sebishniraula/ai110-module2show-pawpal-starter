from datetime import date, time

from pawpal_system import Owner, Pet, Task, Priority


def test_task_mark_complete():
    task = Task(
        title="Evening walk",
        pet_name="Mochi",
        task_type="walk",
        duration_minutes=30,
        priority=Priority.medium,
        due_date=date.today(),
        due_time=time(hour=18, minute=0),
    )

    assert not task.completed
    task.completed = True
    assert task.completed


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
