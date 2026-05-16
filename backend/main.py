from fastapi import FastAPI
from pydantic import BaseModel

from temporalio.client import Client

from workflows.order_workflow import OrderWorkflow
from database import engine, SessionLocal
from models import Base, Run, Activity
from dotenv import load_dotenv
import os
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()
TEMPORAL_SERVER = os.getenv("TEMPORAL_SERVER", "localhost:7233")

app = FastAPI()
Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "http://localhost:3000"
    ],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)



class EventRequest(BaseModel):
    event: str

class InstructionRequest(BaseModel):
    instruction: str


@app.get("/")
async def home():
    return {"message": "Order Supervisor API running"}


@app.post("/runs/{order_id}")
async def start_run(order_id: str):

    client = await Client.connect(TEMPORAL_SERVER)

    handle = await client.start_workflow(
        OrderWorkflow.run,
        order_id,
        id=order_id,
        task_queue="order-task-queue",
    )
    db = SessionLocal()
    
    try:
        new_run = Run(
            workflow_id=handle.id,
            status="RUNNING"
        )

        db.add(new_run)

        db.commit()
    
        return {
            "message": "Workflow started",
            "workflow_id": handle.id
        }
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


@app.post("/events/{workflow_id}")
async def send_event(
    workflow_id: str,
    body: EventRequest
):

    client = await Client.connect(TEMPORAL_SERVER)

    handle = client.get_workflow_handle(workflow_id)

    await handle.signal(
        OrderWorkflow.new_event,
        body.event
    )

    return {
        "message": "Event sent",
        "event": body.event
    }

@app.get("/runs")
async def get_runs():

    db = SessionLocal()
    
    try:
        runs = db.query(Run).order_by(Run.id.desc()).all()

        result = []

        for run in runs:
            result.append({
                "workflow_id": run.workflow_id,
                "status": run.status
            })

        return result
    except Exception as e:
        raise e
    finally:
        db.close()


@app.get("/runs/{workflow_id}")
async def get_run(workflow_id: str):

    db = SessionLocal()
    
    try:
        run = db.query(Run).filter(
            Run.workflow_id == workflow_id
        ).first()

        if not run:
            return {
                "error": "Run not found"
            }

        return {
            "workflow_id": run.workflow_id,
            "status": run.status,
            "memory_summary":run.memory_summary
        }
    except Exception as e:
        raise e
    finally:
        db.close()

@app.get("/activities/{workflow_id}")
async def get_activities(workflow_id: str):

    db = SessionLocal()
    
    try:
        activities = db.query(Activity).filter(
            Activity.workflow_id == workflow_id
        ).all()

        result = []

        for activity in activities:
            result.append({
                "type": activity.type,
                "message": activity.message
            })

        return result
    except Exception as e:
        raise e
    finally:
        db.close()


@app.post("/runs/{workflow_id}/terminate")
async def terminate_run(workflow_id: str):

    client = await Client.connect(TEMPORAL_SERVER)

    handle = client.get_workflow_handle(workflow_id)

    await handle.terminate()

    db = SessionLocal()
    
    try:
        run = db.query(Run).filter(
            Run.workflow_id == workflow_id
        ).first()

        if run:
            run.status = "TERMINATED"

        db.commit()

        return {
            "message": "Workflow terminated"
        }
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()



@app.post("/runs/{workflow_id}/instructions")
async def add_instruction(
    workflow_id: str,
    body: InstructionRequest
):
    try:
        client = await Client.connect(TEMPORAL_SERVER)
        handle = client.get_workflow_handle(workflow_id)

        await handle.signal(
            OrderWorkflow.add_instruction,
            body.instruction
        )

        return {
            "message": "Instruction added",
            "instruction": body.instruction
        }
    except Exception as e:
        return {
            "error": str(e)
        }

    