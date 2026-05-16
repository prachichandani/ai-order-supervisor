import asyncio

from temporalio.client import Client
from temporalio.worker import Worker

from workflows.order_workflow import OrderWorkflow
from activities.actions import (
   message_logistics_team,
   message_customer,
   message_payments_team,
   create_internal_note,
   message_fulfillment_team
)
from activities.db import (
    save_event,
    save_action,
    update_run_status,
    save_instruction,
    update_memory_summary
)
from activities.ai import (
    decide_action_activity,
    compress_memory_activity
)


async def main():

    client = await Client.connect("localhost:7233")

    worker = Worker(
        client,
        task_queue="order-task-queue",
        workflows=[OrderWorkflow],
        activities=[
            message_logistics_team,
            message_customer,
            message_payments_team,
            create_internal_note,
            message_fulfillment_team,
            save_event,
            save_action,
            update_run_status,
            save_instruction,
            update_memory_summary,
            decide_action_activity,
            compress_memory_activity
        ]
    )

    print("Worker started...")

    await worker.run()


asyncio.run(main())