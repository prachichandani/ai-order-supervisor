"use client";

import { useEffect, useState, use } from "react";
const API_URL =
  process.env.NEXT_PUBLIC_API_URL;

type Activity = {
  type: string;
  message: string;
};

type Run = {
  workflow_id: string;
  status: string;
  memory_summary: string;
};

export default function RunPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {

  const { id } = use(params);

  const [activities, setActivities] = useState<Activity[]>([]);
  const [run, setRun] = useState<Run | null>(null);

  const [event, setEvent] = useState("");
  const [instruction, setInstruction] = useState("");

  const [terminating, setTerminating] = useState(false);

  const [sendingEvent, setSendingEvent] = useState(false);
  const [sendingInstruction, setSendingInstruction] = useState(false);

  useEffect(() => {
    fetchActivities();
    fetchRun();
  }, []);

  async function fetchRun() {

    const response = await fetch(
      `${API_URL}/runs/${id}`
    );

    const data = await response.json();

    setRun(data);
  }

  async function fetchActivities() {

    const response = await fetch(
      `${API_URL}/activities/${id}`
    );

    const data = await response.json();

    setActivities(data);
  }

  async function sendEvent() {

    if (!event.trim()) return;

    setSendingEvent(true);

    await fetch(
      `${API_URL}/events/${id}`,
      {
        method: "POST",

        headers: {
          "Content-Type": "application/json",
        },

        body: JSON.stringify({
          event,
        }),
      }
    );

    setEvent("");

    await new Promise((resolve) =>
      setTimeout(resolve, 1500)
    );

    await fetchActivities();

    await fetchRun();

    // If delivered event, fetch memory summary again after compression
    if (event.toLowerCase() === "delivered") {
      await new Promise((resolve) =>
        setTimeout(resolve, 1500)
      );
      await fetchRun();
    }

    setSendingEvent(false);
  }

  async function sendInstruction() {

    if (!instruction.trim()) return;

    setSendingInstruction(true);

    await fetch(
      `${API_URL}/runs/${id}/instructions`,
      {
        method: "POST",

        headers: {
          "Content-Type": "application/json",
        },

        body: JSON.stringify({
          instruction,
        }),
      }
    );

    setInstruction("");

    await new Promise((resolve) =>
      setTimeout(resolve, 1000)
    );

    await fetchActivities();

    await fetchRun();

    setSendingInstruction(false);
  }

  async function terminateWorkflow() {

    setTerminating(true);

    await fetch(
      `${API_URL}/runs/${id}/terminate`,
      {
        method: "POST",
      }
    );

    await new Promise((resolve) =>
      setTimeout(resolve, 500)
    );

    await fetchRun();

    await fetchActivities();

    setTerminating(false);
  }

  const isTerminated =
    run?.status === "TERMINATED";

  const isDelivered = activities.some(
    (activity) =>
        activity.message.toLowerCase() === "delivered"
    );
    


  return (
    <main className="p-10 w-full">

      {/* Header */}

      <div className="flex items-center justify-between  gap-4 mb-2">

        <h1 className="text-3xl font-bold">
          Workflow: {id}
        </h1>

        <button
          onClick={terminateWorkflow}
          disabled={terminating || isTerminated || isDelivered}
          className="bg-red-600 text-white px-4 py-2 rounded disabled:opacity-50"
        >
          {terminating
            ? "Terminating..."
            : "Terminate Workflow"}
        </button>

      </div>

      <p className="mb-8 text-gray-600">
        Status: {run?.status || "Loading..."}
      </p>

      {/* Event Input */}

      <div className="mb-6 space-y-4">

        <input
          value={event}
          onChange={(e) => setEvent(e.target.value)}
          placeholder="Enter event"
          disabled={isTerminated || isDelivered}
          className="border p-3 rounded-xl w-full disabled:opacity-50"
        />

        <button
          onClick={sendEvent}
          disabled={sendingEvent || isTerminated || isDelivered}
          className="bg-black text-white px-4 py-2 rounded-xl disabled:opacity-50"
        >
          {sendingEvent
            ? "Sending..."
            : "Send Event"}
        </button>

      </div>

      {/* Instruction Input */}

      <div className="mb-8 space-y-4">

        <input
          value={instruction}
          onChange={(e) => setInstruction(e.target.value)}
          placeholder="Enter instruction"
          disabled={isTerminated || isDelivered}
          className="border p-3 rounded-xl w-full disabled:opacity-50"
        />

        <button
          onClick={sendInstruction}
          disabled={
            sendingInstruction || isTerminated || isDelivered
          }
          className="bg-blue-600 text-white px-4 py-2 rounded-xl disabled:opacity-50"
        >
          {sendingInstruction
            ? "Adding..."
            : "Add Instruction"}
        </button>

      </div>

      {/* AI Supervisor Context */}

      <div className="mb-10">

        <h2 className="text-2xl font-semibold mb-4">
          AI Supervisor Context
        </h2>

        <div className="bg-black text-white p-6 rounded-2xl whitespace-pre-wrap break-words w-full">

          {run?.memory_summary
            ? run.memory_summary
            : "No memory summary yet"}

        </div>

      </div>

      {/* Activity Timeline */}

      <div>

        <h2 className="text-2xl font-semibold mb-4">
          Activity Timeline
        </h2>

        <div className="space-y-4">

          {[...activities].reverse().map((activity, index) => (

            <div
              key={index}
              className="border p-4 rounded-2xl"
            >

              <p className="font-semibold mb-1">
                {activity.type}
              </p>

              <p>
                {activity.message}
              </p>

            </div>

          ))}

        </div>

      </div>

    </main>
  );
}