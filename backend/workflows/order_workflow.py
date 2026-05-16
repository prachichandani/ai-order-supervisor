from temporalio import workflow
from datetime import timedelta
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
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


@workflow.defn
class OrderWorkflow:

    def __init__(self):

        self.pending_events = []
        self.timeline = []

        # queue for processing instructions
        self.instructions = []

        # permanent instruction memory
        self.all_instructions = []

        self.memory_summary = ""

    async def compress_memory_if_needed(self, order_id):

        if len(self.memory_summary.split()) > 250:

            print("Compressing memory...")

            compressed = await workflow.execute_activity(
                compress_memory_activity,
                args=[self.memory_summary],
                start_to_close_timeout=timedelta(seconds=30),
            )

            self.memory_summary = compressed

            await workflow.execute_activity(
                update_memory_summary,
                args=[
                    order_id,
                    self.memory_summary
                ],
                start_to_close_timeout=timedelta(seconds=10),
            )

    @workflow.signal
    async def new_event(self, event: str):

        print(f"Received event: {event}")

        self.pending_events.append(event)

    @workflow.signal
    async def add_instruction(self, instruction: str):

        print(f"New instruction added: {instruction}")

        self.instructions.append(instruction)
        self.all_instructions.append(instruction)

        self.memory_summary += (
            f"Instruction added: {instruction}. "
        )

    @workflow.run
    async def run(self, order_id: str):

        print(f"Workflow started for {order_id}")

        while True:

            # Wait until event or instruction arrives
            await workflow.wait_condition(
                lambda: (
                    len(self.pending_events) > 0
                    or len(self.instructions) > 0
                )
            )

            # =========================
            # PROCESS INSTRUCTIONS
            # =========================
            if len(self.instructions) > 0:

                instruction = self.instructions.pop(0)

                print(f"Processing instruction: {instruction}")

                await workflow.execute_activity(
                    save_instruction,
                    args=[
                        order_id,
                        instruction
                    ],
                    start_to_close_timeout=timedelta(seconds=10),
                )

                self.timeline.append(
                    f"INSTRUCTION: {instruction}"
                )

                await workflow.execute_activity(
                    update_memory_summary,
                    args=[
                        order_id,
                        self.memory_summary
                    ],
                    start_to_close_timeout=timedelta(seconds=10),
                )

                continue

            # =========================
            # PROCESS EVENTS
            # =========================
            event = self.pending_events.pop(0)

            print(f"Processing event: {event}")

            self.memory_summary += (
                f"Event received: {event}. "
            )

            self.timeline.append(
                f"EVENT: {event}"
            )

            # Save event
            await workflow.execute_activity(
                save_event,
                args=[
                    order_id,
                    event
                ],
                start_to_close_timeout=timedelta(seconds=10),
            )

            # =========================
            # AI REASONING
            # =========================
            decision = await workflow.execute_activity(
                decide_action_activity,
                args=[
                    event,
                    self.memory_summary,
                    self.all_instructions
                ],
                start_to_close_timeout=timedelta(seconds=120),

                retry_policy=RetryPolicy(
                    maximum_attempts=2
                )
            )
            print("AI Decision:", decision)

            actions = decision.get("actions", [])
            reason = decision.get("reason", "")

            self.memory_summary += (
                f"AI Reasoning: {reason}. "
            )

            # =========================
            # DYNAMIC ACTION EXECUTION
            # =========================
            for action in actions:

                # -------------------------
                # LOGISTICS
                # -------------------------
                if action == "message_logistics_team":

                    await workflow.execute_activity(
                        message_logistics_team,
                        args=[
                            "Shipment issue detected",
                            order_id
                        ],
                        start_to_close_timeout=timedelta(seconds=10),
                    )

                    await workflow.execute_activity(
                        update_run_status,
                        args=[
                            order_id,
                            "LOGISTICS_ALERT"
                        ],
                        start_to_close_timeout=timedelta(seconds=10),
                    )

                # -------------------------
                # CUSTOMER
                # -------------------------
                elif action == "message_customer":

                    await workflow.execute_activity(
                        message_customer,
                        args=[
                            "Customer update sent",
                            order_id
                        ],
                        start_to_close_timeout=timedelta(seconds=10),
                    )

                # -------------------------
                # PAYMENTS
                # -------------------------
                elif action == "message_payments_team":

                    await workflow.execute_activity(
                        message_payments_team,
                        args=[
                            "Payment issue detected",
                            order_id
                        ],
                        start_to_close_timeout=timedelta(seconds=10),
                    )

                    await workflow.execute_activity(
                        update_run_status,
                        args=[
                            order_id,
                            "PAYMENT_ISSUE"
                        ],
                        start_to_close_timeout=timedelta(seconds=10),
                    )

                # -------------------------
                # FULFILLMENT
                # -------------------------
                elif action == "message_fulfillment_team":

                    await workflow.execute_activity(
                        message_fulfillment_team,
                        args=[
                            "Fulfillment action required",
                            order_id
                        ],
                        start_to_close_timeout=timedelta(seconds=10),
                    )

                # -------------------------
                # INTERNAL NOTE
                # -------------------------
                elif action == "create_internal_note":

                    await workflow.execute_activity(
                        create_internal_note,
                        args=[
                            f"AI Note: {reason}",
                            order_id
                        ],
                        start_to_close_timeout=timedelta(seconds=10),
                    )

                # -------------------------
                # NO ACTION
                # -------------------------
                elif action == "no_action":

                    print("AI decided no action required")

                else:

                    print(f"Unknown action: {action}")

                # Save action in timeline
                self.timeline.append(
                    f"ACTION: {action}"
                )


            # =========================
            # TERMINAL EVENT
            # =========================
            if event == "delivered":

                print("Order completed")

                await workflow.execute_activity(
                    update_run_status,
                    args=[
                        order_id,
                        "DELIVERED"
                    ],
                    start_to_close_timeout=timedelta(seconds=10),
                )

                self.memory_summary += (
                    "Order successfully delivered. "
                )

                self.timeline.append(
                    "ACTION: order completed"
                )

                await workflow.execute_activity(
                    message_fulfillment_team,
                    args=[
                        "Order delivered",
                        order_id
                    ],
                    start_to_close_timeout=timedelta(seconds=10),
                )


                # Compress memory on delivery
                print("Compressing memory on delivery...")
                compressed = await workflow.execute_activity(
                    compress_memory_activity,
                    args=[self.memory_summary],
                    start_to_close_timeout=timedelta(seconds=30),
                )
                self.memory_summary = compressed

                await workflow.execute_activity(
                    update_memory_summary,
                    args=[
                        order_id,
                        self.memory_summary
                    ],
                    start_to_close_timeout=timedelta(seconds=10),
                )

                print("Workflow completed")
                print("Final Timeline:", self.timeline)

                return

            # =========================
            # UPDATE MEMORY
            # =========================
            await workflow.execute_activity(
                update_memory_summary,
                args=[
                    order_id,
                    self.memory_summary
                ],
                start_to_close_timeout=timedelta(seconds=10),
            )
            await self.compress_memory_if_needed(order_id)

            print("Timeline:", self.timeline)