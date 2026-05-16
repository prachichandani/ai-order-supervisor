from temporalio import activity

from services.ai_services import decide_action, compress_memory


@activity.defn
async def decide_action_activity(
    event: str,
    memory_summary: str,
    instructions: list[str]
):

    return decide_action(
        event=event,
        memory_summary=memory_summary,
        instructions=instructions
    )


@activity.defn
async def compress_memory_activity(memory: str):

    return compress_memory(memory)