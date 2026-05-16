"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
const API_URL =
  process.env.NEXT_PUBLIC_API_URL;

type Run = {
  workflow_id: string;
  status: string;
};

export default function HomePage() {

  const [runs, setRuns] = useState<Run[]>([]);
  const [orderId, setOrderId] = useState("");

  const [creatingRun, setCreatingRun] = useState(false);

  useEffect(() => {

    fetchRuns();

    const interval = setInterval(() => {
      fetchRuns();
    }, 15000);

    return () => clearInterval(interval);

  }, []);

  async function fetchRuns() {

    const response = await fetch(
      `${API_URL}/runs`
    );

    const data = await response.json();

    setRuns(data);
  }

  async function createRun() {

    if (!orderId.trim()) return;

    setCreatingRun(true);

    await fetch(
      `${API_URL}/runs/${orderId}`,
      {
        method: "POST",
      }
    );

    setOrderId("");

    await fetchRuns();

    setCreatingRun(false);
  }

  return (
    <main className="p-10">

      <h1 className="text-3xl font-bold mb-6">
        Order Supervisor Dashboard
      </h1>

      <div className="mb-8 space-y-4">

        <input
          value={orderId}
          onChange={(e) => setOrderId(e.target.value)}
          placeholder="Enter order id"
          className="border p-2 rounded w-full"
        />

        <button
          onClick={createRun}
          disabled={creatingRun}
          className="bg-black text-white px-4 py-2 rounded disabled:opacity-50"
        >
          {creatingRun ? "Starting..." : "Start Workflow"}
        </button>

      </div>

      <div className="space-y-4">

        {runs.map((run)=> (

          <Link
            key={run.workflow_id}
            href={`/runs/${run.workflow_id}`}
          >

            <div className="border p-4 rounded-xl hover:bg-gray-100 cursor-pointer">

              <p>
                <strong>Workflow:</strong> {run.workflow_id}
              </p>

              <p>
                <strong>Status:</strong> {run.status}
              </p>

            </div>

          </Link>

        ))}

      </div>

    </main>
  );
}   