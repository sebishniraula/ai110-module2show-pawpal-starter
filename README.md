# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## Completed Implementation

- `pawpal_system.py` contains OOP model: `Owner`, `Pet`, `Task`, `ScheduledTask`, `Scheduler`.
- Scheduler handles daily task collection, fixed vs flexible times, priority ordering, conflict detection, and simple recurrence rules.
- `app.py` now calls `Scheduler` on button click, rendering task table and conflict warnings.
- `test_pawpal_system.py` includes pytest coverage for task assignment, ordering, recurrence, and conflict detection.

## Smarter Scheduling

The latest version includes:

- `Scheduler.sort_tasks_by_time` for chronological ordering with flexible tasks last
- `Scheduler.filter_tasks` for pet and completion status filtering
- `Task.mark_complete` auto-creates next recurrence for daily/weekly/monthly tasks
- `Owner.mark_task_complete` as a UI-friendly helper to mark and reload repeating tasks
- Enhanced conflict detection with `Scheduler.detect_conflicts` warning about overlapping times

## Testing PawPal+

To run the test suite:

```bash
python -m pytest
```

What the tests cover:

- Sorting correctness for tasks by due time
- Recurrence behavior: completing a daily task schedules the next date
- Conflict detection works when tasks overlap in scheduled time
- Basic task management (add task to pet, duplicate prevention)

Confidence Level: ⭐⭐⭐⭐⭐ (5/5) based on 7 passing tests and focused edge case coverage.


