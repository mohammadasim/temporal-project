# My Understanding of Temporal

Personal notes for quick context when revisiting this project.

---

## What is Temporal?

Temporal is a framework that can be embedded in applications to ensure tasks are **always executed** — even in the face of failures, crashes, or network issues. It guarantees that a workflow will run to completion, retrying failed steps automatically and preserving state across restarts.

---

## Core Concepts

### Activity
The **basic unit of work** in Temporal. An activity is a function that does one specific thing — call an API, send an email, write to a database. Activities can fail and be retried independently without affecting the rest of the workflow.

### Workflow
A **container of activities**. A workflow is made up of one or many activities executed in a defined order. It represents the full business process. Temporal tracks every step of the workflow — if something fails mid-way, it knows exactly where to resume.

### Worker
The **workhorse of Temporal**. A worker is a long-running process that listens on a specific task queue and executes workflows and activities as Temporal schedules them. Workers have no state of their own — all state lives in the Temporal server.

---

## How This Django Project Is Structured

### Activities & Workflow — at the app level
Inside `payments/`, I created a set of activities representing the steps taken when a student enrolls in a course:

1. Process payment
2. Send confirmation email
3. Update enrollment status
4. Create invoice
5. Email invoice

These were then composed into a single `EnrollmentWorkflow`. Activities and workflows live inside the Django app (`payments/`) because they contain **domain/business logic** — they belong to the app, not the infrastructure.

### Worker — at the project root
A single `worker.py` lives at the Django project root (`temporaltutorial/`). It imports workflows and activities from all apps and registers them with Temporal. It's infrastructure, not business logic, so it sits above the apps.

As the project grows with new apps, you just add their imports to this one file.

### View — the trigger point
When a specific Django view is called (the enrollment form submission), the view creates a Temporal client, connects to the Temporal server, and starts an instance of `EnrollmentWorkflow`. The workflow is placed on the task queue, and the worker picks it up and executes it.

---

## Local vs Production

### Local (this project)
The Temporal server runs on `localhost:7233` via the Temporal CLI (`temporal server start-dev`). The client connects to it directly:

```python
client = await Client.connect("localhost:7233")
```

### Production
In production, the client connects to **Temporal Cloud** instead of localhost. Temporal Cloud manages all workflow state, retries, and history — you don't run the Temporal server yourself.

```python
client = await Client.connect(
    "your-namespace.tmprl.cloud:7233",
    namespace="your-namespace",
    tls=TLSConfig(...),
)
```

---

## Scaling — just like Celery

The Temporal worker runs as a **separate process**, independent of the Django web server. In a containerised deployment (e.g. ECS):

- One ECS task runs the Django app
- A separate ECS task runs the Temporal worker (`python worker.py`)

The worker container can be **scaled horizontally** — spin up more worker containers under high load, scale them down when idle. Temporal automatically distributes workflow executions across all available workers on the same task queue.

This is the same mental model as Celery workers, but with durable state and built-in observability baked in.
