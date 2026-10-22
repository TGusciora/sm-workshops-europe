// Shapes returned by the backend (backend/app/schemas.py).

export interface Health {
  status: "ok";
  auth_method: "subscription" | "api_key";
}

export interface Position {
  slug: string;
  title: string;
}

export interface JobDescription {
  slug: string;
  text: string | null;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  created_at: string;
}

export interface Draft {
  id: number;
  text: string;
  status: string;
}

export interface Chat {
  messages: ChatMessage[];
  draft: Draft | null;
}

export interface DraftDecision {
  status: string;
  path: string | null;
}

export type Decision = "approve" | "edit" | "reject";

export interface Question {
  id: number;
  question: string;
  purpose: string;
  good_answer: string;
  status: "proposed" | "approved" | "rejected";
}

export interface QuestionSet {
  stage: string;
  confirmed: boolean;
  questions: Question[];
}

export type InterviewStatus = "planned" | "cancelled";

export interface Interview {
  id: number;
  stage: string;
  starts_at: string;
  duration_minutes: number;
  interviewer: string;
  location: string;
  candidate_ref: string;
  status: InterviewStatus;
}

export interface InterviewInput {
  stage: string;
  starts_at: string;
  duration_minutes: number;
  interviewer: string;
  location: string;
  candidate_ref: string;
}
