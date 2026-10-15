import { vi } from "vitest";

export interface Call {
  method: string;
  path: string;
  body: unknown;
}

type Handler = (call: Call) => unknown;

// Replaces fetch with a router. Each handler returns the JSON body, or throws a Response.
export function mockApi(handler: Handler): Call[] {
  const calls: Call[] = [];
  const fetchMock = vi.fn(async (input: string, init?: RequestInit) => {
    const call: Call = {
      method: init?.method ?? "GET",
      path: input.replace(/^\/api/, ""),
      body: init?.body ? JSON.parse(String(init.body)) : undefined,
    };
    calls.push(call);
    try {
      const data = handler(call);
      return new Response(JSON.stringify(data), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      });
    } catch (err) {
      if (err instanceof Response) return err;
      throw err;
    }
  });
  vi.stubGlobal("fetch", fetchMock);
  return calls;
}

export function problem(status: number, detail: string): Response {
  return new Response(JSON.stringify({ detail }), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}
