from datetime import date, time

from pawpal_system import Owner, Pet, Task, Priority, Scheduler


def main():
    owner = Owner(name="Jamie")
    owner.add_pet(Pet(name="Mochi", species="dog", age_years=2))
    owner.add_pet(Pet(name="Nala", species="cat", age_years=4))

    owner.add_task(
        Task(
            title="Morning walk",
            pet_name="Mochi",
            task_type="walk",
            duration_minutes=30,
            priority=Priority.high,
            due_date=date.today(),
            due_time=time(hour=8, minute=30),
            recurrence="daily",
        )
    )

    owner.add_task(
        Task(
            title="Feed",
            pet_name="Nala",
            task_type="feeding",
            duration_minutes=15,
            priority=Priority.medium,
            due_date=date.today(),
            due_time=time(hour=9, minute=0),
        )
    )

    owner.add_task(
        Task(
            title="Play session",
            pet_name="Mochi",
            task_type="exercise",
            duration_minutes=20,
            priority=Priority.low,
            due_date=date.today(),
        )
    )

    scheduler = Scheduler(owner=owner)
    schedule = scheduler.build_daily_schedule(date.today())

    print("Today's schedule:\n")
    for item in schedule:
        print(
            f"{item.start_time.strftime('%H:%M')} - {item.end_time.strftime('%H:%M')}: "
            f"{item.task.task_type} ({item.task.title}) for {item.task.pet_name} "
            f"[{item.task.priority.name}]"
        )

    conflicts = scheduler.detect_conflicts(schedule)
    if conflicts:
        print("\nConflicts detected:")
        for a, b in conflicts:
            print(f"- {a.task.title} overlaps with {b.task.title}")
    else:
        print("\nNo conflicts")


if __name__ == "__main__":
    main()
