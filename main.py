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

    # Add tasks out of order to validate sorting logic
    owner.add_task(
        Task(
            title="Midday nap",
            pet_name="Nala",
            task_type="rest",
            duration_minutes=30,
            priority=Priority.low,
            due_date=date.today(),
            due_time=time(hour=13, minute=0),
        )
    )

    owner.add_task(
        Task(
            title="Quick check",
            pet_name="Mochi",
            task_type="health",
            duration_minutes=10,
            priority=Priority.medium,
            due_date=date.today(),
            due_time=time(hour=9, minute=0),
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

    print("\nSorted tasks by time and priority:")
    all_tasks = owner.all_tasks_for_date(date.today())
    sorted_tasks = scheduler.sort_tasks_by_time(all_tasks)
    for task in sorted_tasks:
        time_str = task.due_time.strftime('%H:%M') if task.due_time else 'flexible'
        print(f"- {time_str}: {task.title} [{task.pet_name}] ({task.priority.name})")

    print("\nFiltered tasks (Mochi, incomplete):")
    filtered_tasks = scheduler.filter_tasks(all_tasks, pet_name="Mochi", completed=False)
    for task in filtered_tasks:
        print(f"- {task.title} at {task.due_time if task.due_time else 'anytime'}")

    # Mark a recurring task complete and auto-generate the next occurrence
    next_task = owner.mark_task_complete("Mochi", "Morning walk")
    if next_task:
        print(f"\nRecurring task created for next occurrence: {next_task.title} on {next_task.due_date}")

    # Create a direct conflict with same time for both pets
    owner.add_task(
        Task(
            title="Conflict check",
            pet_name="Nala",
            task_type="play",
            duration_minutes=30,
            priority=Priority.high,
            due_date=date.today(),
            due_time=time(hour=9, minute=0),
        )
    )
    conflict_schedule = scheduler.build_daily_schedule(date.today())
    conflict_pairs = scheduler.detect_conflicts(conflict_schedule)
    if conflict_pairs:
        print("\nConflict detection works with new tasks:")
        for a, b in conflict_pairs:
            print(f"- {a.task.title} conflicts with {b.task.title}")


if __name__ == "__main__":
    main()
