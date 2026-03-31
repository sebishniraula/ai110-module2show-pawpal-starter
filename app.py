import streamlit as st
from datetime import date, time
from pawpal_system import Owner, Pet, Task, Priority, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

# session state persistence for the Owner model
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan")

if "tasks" not in st.session_state:
    st.session_state.tasks = []

st.subheader("Quick Demo Inputs (UI only)")
owner_name = st.text_input("Owner name", value=st.session_state.owner.name)

if owner_name != st.session_state.owner.name:
    st.session_state.owner.name = owner_name
# Add / manage pets
st.markdown("### Pets")
with st.form("add_pet_form", clear_on_submit=True):
    new_pet_name = st.text_input("Pet name")
    new_species = st.selectbox("Species", ["dog", "cat", "other"])
    add_pet_button = st.form_submit_button("Add pet")

if add_pet_button:
    if not new_pet_name.strip():
        st.warning("Please enter a pet name.")
    else:
        try:
            st.session_state.owner.add_pet(Pet(name=new_pet_name.strip(), species=new_species))
            st.success(f"Added pet: {new_pet_name.strip()}")
        except ValueError as e:
            st.error(str(e))

if st.session_state.owner.pets:
    st.write("Current pets:")
    pet_table = [{"name": p.name, "species": p.species, "tasks": len(p.tasks)} for p in st.session_state.owner.pets]
    st.table(pet_table)
else:
    st.info("No pets yet. Add one above.")

st.markdown("### Tasks")
st.caption("Add a few tasks. These should feed into your scheduler.")

if not st.session_state.owner.pets:
    st.warning("Add a pet first before scheduling tasks.")
else:
    with st.form("add_task_form", clear_on_submit=True):
        task_title = st.text_input("Task title", value="Morning walk")
        task_pet = st.selectbox("For pet", [p.name for p in st.session_state.owner.pets])
        task_type = st.selectbox("Task type", ["walk", "feeding", "medication", "appointment", "general"], index=0)
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
        due_date = st.date_input("Due date", value=date.today())
        set_time = st.checkbox("Set specific due time")
        due_time_val = st.time_input("Due time", value=time(8, 0)) if set_time else None
        recurrence = st.selectbox("Recurrence", ["none", "daily", "weekly", "monthly"], index=0)

        add_task_button = st.form_submit_button("Add task")

    if add_task_button:
        recurrence_val = None if recurrence == "none" else recurrence
        due_time = due_time_val if set_time else None
        try:
            st.session_state.owner.add_task(
                Task(
                    title=task_title,
                    pet_name=task_pet,
                    task_type=task_type,
                    duration_minutes=int(duration),
                    priority=Priority[priority],
                    due_date=due_date,
                    due_time=due_time,
                    recurrence=recurrence_val,
                )
            )
            st.success(f"Added task '{task_title}' for {task_pet}")
        except Exception as e:
            st.error(str(e))

    all_tasks = []
    for pet in st.session_state.owner.pets:
        for t in pet.tasks:
            all_tasks.append(
                {
                    "pet": pet.name,
                    "task": t.title,
                    "type": t.task_type,
                    "duration": t.duration_minutes,
                    "priority": t.priority.name,
                    "due_date": t.due_date.isoformat() if t.due_date else "Any",
                    "due_time": t.due_time.strftime("%H:%M") if t.due_time else "Flexible",
                    "recurrence": t.recurrence or "none",
                }
            )

    if all_tasks:
        st.write("Current tasks:")
        st.table(all_tasks)
    else:
        st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("This button calls your scheduling logic with the owner data in session state.")

# Show today's raw tasks and advanced controls
owner = st.session_state.owner
scheduler = Scheduler(owner=owner)

today_tasks = owner.all_tasks_for_date(date.today())
if today_tasks:
    st.write("### Today's task list")
    today_table = [
        {
            "pet": t.pet_name,
            "task": t.title,
            "type": t.task_type,
            "due_time": t.due_time.strftime("%H:%M") if t.due_time else "Flexible",
            "priority": t.priority.name,
            "recurrence": t.recurrence or "none",
            "completed": t.completed,
        }
        for t in today_tasks
    ]
    st.table(today_table)

    st.write("### Sorting and filtering")
    selected_pet = st.selectbox("Filter by pet", options=["all"] + [p.name for p in owner.pets], index=0)
    show_completed = st.checkbox("Show completed tasks", value=True)
    tasks_for_filter = today_tasks
    if selected_pet != "all":
        tasks_for_filter = scheduler.filter_tasks(tasks_for_filter, pet_name=selected_pet)
    if not show_completed:
        tasks_for_filter = scheduler.filter_tasks(tasks_for_filter, completed=False)

    sorted_tasks = scheduler.sort_tasks_by_time(tasks_for_filter)
    if sorted_tasks:
        sorted_table = [
            {
                "pet": t.pet_name,
                "task": t.title,
                "due_time": t.due_time.strftime("%H:%M") if t.due_time else "Flexible",
                "priority": t.priority.name,
                "completed": t.completed,
            }
            for t in sorted_tasks
        ]
        st.success("Displaying sorted tasks")
        st.table(sorted_table)
    else:
        st.info("No tasks match the selected filter criteria.")
else:
    st.info("No tasks for today. Add tasks to populate the schedule.")

if st.button("Generate schedule"):
    if not owner.pets:
        st.warning("Add a pet and tasks first before generating schedule.")
    else:
        schedule = scheduler.build_daily_schedule(date.today())

        if schedule:
            schedule_table = [
                {
                    "start": s.start_time.strftime("%H:%M"),
                    "end": s.end_time.strftime("%H:%M"),
                    "task": s.task.title,
                    "pet": s.task.pet_name,
                    "type": s.task.task_type,
                    "priority": s.task.priority.name,
                }
                for s in schedule
            ]

            st.write("## Generated schedule")
            st.table(schedule_table)

            conflicts = scheduler.detect_conflicts(schedule)
            if conflicts:
                st.warning("⚠️ Conflicts detected in schedule")
                for a, b in conflicts:
                    st.write(f"- {a.task.title} ({a.task.pet_name}) overlaps with {b.task.title} ({b.task.pet_name})")
                st.error("Please adjust task times or remove duplicates to resolve conflicts.")
            else:
                st.success("✅ No conflicts detected. Your schedule is clear.")
        else:
            st.info("No scheduled tasks for today")

