# LearnFlow — Temporal + Django Tutorial Project

A hands-on project for learning [Temporal](https://temporal.io/) durable workflows by building a realistic online learning platform with Django. The app simulates a full course enrollment flow — payment, confirmation email, enrollment update, and invoice — while demonstrating Temporal's core concepts: activity retries, fault tolerance, and workflow durability.

---

## Project Structure

```
temporal-project/
├── env/                          # Python virtual environment
├── requirements.py               # Python dependencies
│
├── # ── Standalone Temporal scripts (for reference) ──────────────────
├── activity.py                   # Simple standalone activity example
├── workflow.py                   # Simple standalone workflow example
├── worker.py                     # Simple standalone worker example
├── starter.py                    # Standalone workflow starter
│
└── temporaltutorial/             # Main Django project
    ├── manage.py
    ├── worker.py                 # ← Project-level Temporal worker (run this)
    │
    ├── mysite/                   # Django project settings
    │   ├── settings.py
    │   └── urls.py
    │
    └── payments/                 # Django app — course enrollment domain
        ├── activities.py         # Temporal activities
        ├── workflows.py          # Temporal workflows
        ├── views.py              # Django views (triggers workflow on form submit)
        ├── urls.py
        └── templates/
            └── payments/
                └── index.html    # Landing page with enrollment form
```

---

## Tech Stack

| Technology | Version | Role |
|---|---|---|
| Python | 3.12 | Runtime |
| Django | 6.0.4 | Web framework |
| Temporal Python SDK | 1.26.0 | Workflow orchestration |
| SQLite | — | Development database |
| Temporal Server | latest | Workflow state & scheduling |

---

## Prerequisites

- Python 3.12+
- [Temporal CLI](https://docs.temporal.io/cli) installed
- `pip` / virtual environment

---

## Setup

**1. Clone the repo**
```bash
git clone git@github.com:mohammadasim/temporal-project.git
cd temporal-project
```

**2. Create and activate a virtual environment**
```bash
python -m venv env
source env/bin/activate
```

**3. Install dependencies**
```bash
pip install -r requirements.py
```

**4. Apply Django migrations**
```bash
cd temporaltutorial
python manage.py migrate
```

---

## Running the Application

You need **three** processes running simultaneously.

**Terminal 1 — Temporal development server**
```bash
temporal server start-dev
```
Temporal UI will be available at [http://localhost:8233](http://localhost:8233)

**Terminal 2 — Django web server**
```bash
cd temporaltutorial
python manage.py runserver
```
App available at [http://localhost:8000](http://localhost:8000)

**Terminal 3 — Temporal worker**
```bash
cd temporaltutorial
python worker.py
```

> **Note:** The Django dev server auto-reloads on code changes. The Temporal worker does **not** — you must restart it manually after editing `activities.py` or `workflows.py`.

---

## The Enrollment Workflow

When a user submits the enrollment form, Django triggers `EnrollmentWorkflow`, which runs five activities in sequence:

```
EnrollmentWorkflow
 ├── 1. process_payment          — simulates charging the student
 ├── 2. send_confirmation_email  — simulates sending a confirmation
 ├── 3. update_enrollment_status — simulates updating the database
 ├── 4. create_invoice           — simulates generating an invoice
 └── 5. email_invoice            — simulates emailing the invoice
```

Each activity uses `asyncio.sleep()` to simulate real-world latency.

---

## Simulating Failures & Recovery

`send_confirmation_email` is set up to demonstrate Temporal's retry and recovery behaviour using a flag file.

**How it works:**
- On the **first attempt**, the activity raises a retryable `ApplicationError` and creates `/tmp/email_activity_failed_once`
- On the **next attempt**, it finds the flag file, removes it, and succeeds

**To observe worker recovery:**
1. Submit the enrollment form — the activity fails and Temporal schedules a retry
2. Kill the worker (`Ctrl+C`) while the retry is pending
3. Restart the worker — it picks up the scheduled retry from the Temporal server and completes

**To reset the simulation:**
```bash
rm -f /tmp/email_activity_failed_once
```

**Error types:**
```python
# Retryable — Temporal will keep retrying (default)
raise ApplicationError("Something went wrong")

# Non-retryable — workflow fails immediately, no retries
raise ApplicationError("Fatal error", non_retryable=True)
```

---

## Architecture — Temporal + Django

Each Django **app owns its own workflows and activities**. The worker at the project root is the only infrastructure file — it imports from all apps and registers everything with Temporal.

```
payments/workflows.py    ← business logic (owned by the app)
payments/activities.py   ← business logic (owned by the app)
worker.py                ← infrastructure (imports from all apps)
```

To add a new app:
1. Create `your_app/workflows.py` and `your_app/activities.py`
2. Add imports to `temporaltutorial/worker.py`

---

## Key Concepts Demonstrated

| Concept | Where |
|---|---|
| Workflow definition | `payments/workflows.py` |
| Activity definition | `payments/activities.py` |
| Multi-arg activity calls (`args=[...]`) | `payments/workflows.py` |
| Triggering a workflow from Django | `payments/views.py` |
| Single project-level worker | `temporaltutorial/worker.py` |
| Retryable vs non-retryable errors | `payments/activities.py` |
| Worker recovery (kill & restart) | `send_confirmation_email` flag pattern |
| `django.setup()` in worker | `temporaltutorial/worker.py` |
