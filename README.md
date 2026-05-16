# AI Order Supervisor

AI-powered order orchestration and workflow supervision system built using Temporal, FastAPI, PostgreSQL, and Next.js.

This project simulates a production-style distributed order workflow system where workflows can receive real-time events, dynamic instructions, AI-generated memory compression, and live monitoring through a dashboard.

---

# Features

## Workflow Orchestration

* Distributed workflow orchestration using Temporal
* Long-running workflow execution
* Runtime event injection
* Dynamic instruction handling
* Workflow termination support
* Persistent workflow state tracking

## AI Supervisor Memory

* Continuous workflow memory accumulation
* LLM-based memory compression
* Structured operational summaries
* Prompt-engineered workflow summarization
* Final compressed workflow context after delivery

## Monitoring Dashboard

* Real-time workflow monitoring UI
* Activity timeline tracking
* AI supervisor context panel
* Workflow status display
* Loading and disabled states
* Automatic UI locking after delivery/termination

---

# Tech Stack

## Backend

* Python
* FastAPI
* Temporal
* PostgreSQL
* SQLAlchemy
* Groq / Llama 3.3

## Frontend

* Next.js
* React
* TypeScript
* Tailwind CSS

---

# Architecture

```text
Next.js Frontend
        ↓
FastAPI Backend
        ↓
Temporal Workflows
        ↓
Activities + AI Memory Compression
        ↓
PostgreSQL Persistence
```

---

# API Endpoints

## Runs

```text
POST   /runs/{order_id}
GET    /runs
GET    /runs/{workflow_id}
POST   /runs/{workflow_id}/terminate
```

## Events

```text
POST   /events/{workflow_id}
```

## Instructions

```text
POST   /runs/{workflow_id}/instructions
```

## Activities

```text
GET    /activities/{workflow_id}
```

---

# AI Memory Compression

Workflow history is continuously accumulated and compressed into structured operational memory using an LLM.

The system extracts:

* workflow statuses
* operational issues
* actions taken
* active instructions
* latest workflow events

Example compressed memory:

```text
Statuses: CREATED -> PAYMENT_PENDING -> DELIVERED
Issues: payment_delay
Actions: notify_customer, escalate_order
Instructions: prioritize_delivery
Last Event: delivered
```

The compressed memory is stored in PostgreSQL and displayed inside the dashboard as the AI Supervisor Context.

---

# Prompt Engineering

The project uses structured prompting to generate compact workflow memory.

The prompt is designed to:

* preserve active instructions
* preserve operational issues
* extract workflow state transitions
* compress long histories into concise summaries
* generate structured operational memory for future workflow reasoning

---

# Frontend Behavior

* Activities appear in reverse chronological order
* Buttons are disabled while requests are processing
* Workflow controls are disabled after delivery
* Workflow controls are disabled after termination
* Activity timeline refreshes automatically after actions
* AI memory expands dynamically with workflow context

---

# Running Locally

## Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

## Frontend

```bash
cd frontend
npm install
npm run dev
```

---

# Environment Variables

## Backend

```env
TEMPORAL_SERVER=localhost:7233
```

## Frontend

```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

---

# Future Improvements

* State machine validation
* Human approval workflow
* Predictive ETA AI
* AI decision timeline
* Event priority queues

