from temporalio import activity

from database import SessionLocal
from models import Activity, Run


@activity.defn
async def save_event(
    workflow_id: str,
    event: str
):
    db = None
    try:
        db = SessionLocal()

        activity_log = Activity(
            workflow_id=workflow_id,
            type="EVENT",
            message=event
        )

        db.add(activity_log)

        db.commit()

        return "event saved"
    except Exception as e:
        if db:
            db.rollback()
        raise e
    finally:
        if db:
            db.close()


@activity.defn
async def save_action(
    workflow_id: str,
    action: str
):
    db = None
    try:
        db = SessionLocal()

        activity_log = Activity(
            workflow_id=workflow_id,
            type="ACTION",
            message=action
        )

        db.add(activity_log)

        db.commit()

        return "action saved"
    except Exception as e:
        if db:
            db.rollback()
        raise e
    finally:
        if db:
            db.close()


@activity.defn
async def update_run_status(
    workflow_id: str,
    status: str
):
    db = None
    try:
        db = SessionLocal()

        run = db.query(Run).filter(
            Run.workflow_id == workflow_id
        ).first()

        if run:
            run.status = status

        db.commit()

        return "status updated"
    except Exception as e:
        if db:
            db.rollback()
        raise e
    finally:
        if db:
            db.close()


@activity.defn
async def save_instruction(
    workflow_id: str,
    instruction: str
):
    db = None
    try:
        db = SessionLocal()

        activity_log = Activity(
            workflow_id=workflow_id,
            type="INSTRUCTION",
            message=instruction
        )

        db.add(activity_log)

        db.commit()

        return "instruction saved"
    except Exception as e:
        if db:
            db.rollback()
        raise e
    finally:
        if db:
            db.close()


@activity.defn
async def update_memory_summary(
    workflow_id: str,
    summary: str
):
    try:
        db = SessionLocal()

        run = db.query(Run).filter(
            Run.workflow_id == workflow_id
        ).first()

        if run:
            run.memory_summary = summary

        db.commit()
        return "memory updated"

    except Exception as e:
        if db:
            db.rollback()
        raise e
        
    finally:
        if db:
            db.close()


    

    