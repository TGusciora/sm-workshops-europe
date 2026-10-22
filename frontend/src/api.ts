// The only place the frontend talks to the backend. All calls go over HTTP to /api.
import type {
  Chat,
  Decision,
  DraftDecision,
  Health,
  Interview,
  InterviewInput,
  JobDescription,
  Position,
  Question,
  QuestionSet,
} from "./types";

export class ApiError extends Error {
  readonly status: number;

  constructor(status: number, message: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

async function request<T>(method: string, path: string, body?: unknown): Promise<T> {
  const response = await fetch(`/api${path}`, {
    method,
    headers: body === undefined ? undefined : { "Content-Type": "application/json" },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  if (!response.ok) {
    let detail = response.statusText || `HTTP ${response.status}`;
    try {
      const data = (await response.json()) as { detail?: unknown };
      if (typeof data.detail === "string") detail = data.detail;
    } catch {
      // The body was not JSON. Keep the status text.
    }
    throw new ApiError(response.status, detail);
  }
  return (await response.json()) as T;
}

export const api = {
  health: () => request<Health>("GET", "/health"),
  listPositions: () => request<Position[]>("GET", "/positions"),
  createPosition: (title: string) => request<Position>("POST", "/positions", { title }),
  getJobDescription: (slug: string) =>
    request<JobDescription>("GET", `/positions/${slug}/job-description`),
  getChat: (slug: string) => request<Chat>("GET", `/positions/${slug}/chat`),
  sendChat: (slug: string, message: string) =>
    request<Chat>("POST", `/positions/${slug}/chat`, { message }),
  decideDraft: (draftId: number, action: Decision, text?: string) =>
    request<DraftDecision>("POST", `/drafts/${draftId}/decision`, { action, text }),
  listStages: () => request<{ stages: string[] }>("GET", "/stages"),
  getQuestions: (slug: string, stage: string) =>
    request<QuestionSet>("GET", `/positions/${slug}/stages/${stage}/questions`),
  proposeQuestions: (slug: string, stage: string) =>
    request<QuestionSet>("POST", `/positions/${slug}/stages/${stage}/questions`),
  decideQuestion: (
    questionId: number,
    action: Decision,
    edits: { question?: string; purpose?: string; good_answer?: string } = {},
  ) => request<Question>("POST", `/questions/${questionId}/decision`, { action, ...edits }),
  confirmQuestions: (slug: string, stage: string) =>
    request<QuestionSet>("POST", `/positions/${slug}/stages/${stage}/confirm`),
  listInterviews: (slug: string) => request<Interview[]>("GET", `/positions/${slug}/interviews`),
  planInterview: (slug: string, input: InterviewInput) =>
    request<Interview>("POST", `/positions/${slug}/interviews`, input),
  editInterview: (interviewId: number, input: InterviewInput) =>
    request<Interview>("PUT", `/interviews/${interviewId}`, input),
  cancelInterview: (interviewId: number) =>
    request<Interview>("POST", `/interviews/${interviewId}/cancel`),
};
