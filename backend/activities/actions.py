from temporalio import activity

from database import SessionLocal
from models import Activity

@activity.defn
async def message_logistics_team(
    message: str,
    workflow_id: str
):
    try:
        print(f"[ACTION] Logistics Team Notified: {message}")
        db = SessionLocal()

        activity_log = Activity(
            workflow_id=workflow_id,
            type="ACTION",
            message='Logistics team notified'
        )

        db.add(activity_log)

        db.commit()

    except Exception as e:
        print(f"[ERROR] Failed to notify Logistics team: {e}")
    finally:
        db.close()

    return 'done' 



@activity.defn
async def message_customer(
    message: str,
    workflow_id: str
):
    try:
        print(f"[ACTION] Customer Messaged: {message}")
        db = SessionLocal()
        activity_log = Activity(
            workflow_id=workflow_id,
            type="ACTION",
            message='Customer messaged'
        )

        db.add(activity_log)

        db.commit()

    except Exception as e:
        print(f"[ERROR] Failed to message customer: {e}")
    finally:
        db.close()

    return 'done' 


@activity.defn
async def message_payments_team(
    message: str,
    workflow_id: str
):
    try:

        print(f"[ACTION] Payments Team Notified: {message}")
        db = SessionLocal()

        activity_log = Activity(
            workflow_id=workflow_id,
            type="ACTION",
            message='Payments team notified'
        )

        db.add(activity_log)

        db.commit()
    except Exception as e:
        print(f"[ERROR] Failed to notify Payments team: {e}")
    finally:
        db.close()

    return 'done' 
    


@activity.defn
async def message_fulfillment_team(
    message: str,
    workflow_id: str
):
    try:
        print(f"[ACTION] Fulfillment Team Notified: {message}")
        db = SessionLocal()

        activity_log = Activity(        
            workflow_id=workflow_id,
            type="ACTION",
            message='Fulfillment team notified'
        )

        db.add(activity_log)

        db.commit()
    except Exception as e:
        print(f"[ERROR] Failed to notify Fulfillment team: {e}")
    finally:
        db.close()

    return 'done' 

@activity.defn
async def create_internal_note(
    message: str,
    workflow_id: str
):
    try:
        print(f"[ACTION] Internal Note Created: {message}")
        db = SessionLocal()

        activity_log = Activity(
            workflow_id=workflow_id,
            type="ACTION",
            message='Internal note created'
        )

        db.add(activity_log)

        db.commit()
    except Exception as e:
        print(f"[ERROR] Failed to create internal note: {e}")
    finally:
        db.close()

    return 'done'






