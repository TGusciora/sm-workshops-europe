import { useEffect, useState } from "react";
import { api } from "../api";
import type { Decision, Question, QuestionSet } from "../types";
import { StateMessage } from "./StateMessage";

interface Props {
  slug: string;
}

interface Edit {
  question: string;
  purpose: string;
  good_answer: string;
}

// Each proposed question is approved, edited or rejected on its own. The approved set
// is stored as final only when the hiring manager confirms it (ADR-0005).
export function QuestionReview({ slug }: Props) {
  const [stages, setStages] = useState<string[]>([]);
  const [stage, setStage] = useState("");
  const [set, setSet] = useState<QuestionSet | null>(null);
  const [editing, setEditing] = useState<{ id: number; values: Edit } | null>(null);
  const [loading, setLoading] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .listStages()
      .then((data) => {
        setStages(data.stages);
        setStage((current) => current || data.stages[0] || "");
      })
      .catch((err: unknown) => setError(err instanceof Error ? err.message : String(err)));
  }, []);

  useEffect(() => {
    if (!stage) return;
    let cancelled = false;
    // Drop the previous stage's set so its buttons cannot act while this one loads.
    setSet(null);
    setError(null);
    setEditing(null);
    setLoading(true);
    api
      .getQuestions(slug, stage)
      .then((data) => !cancelled && setSet(data))
      .catch((err: unknown) => !cancelled && setError(err instanceof Error ? err.message : String(err)))
      .finally(() => !cancelled && setLoading(false));
    return () => {
      cancelled = true;
    };
  }, [slug, stage]);

  async function run(action: () => Promise<QuestionSet>) {
    setBusy(true);
    setError(null);
    try {
      setSet(await action());
      setEditing(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setBusy(false);
    }
  }

  async function decide(question: Question, action: Decision, edits: Partial<Edit> = {}) {
    await run(async () => {
      await api.decideQuestion(question.id, action, edits);
      return api.getQuestions(slug, stage);
    });
  }

  const approvedCount = set?.questions.filter((q) => q.status === "approved").length ?? 0;
  const hasQuestions = (set?.questions.length ?? 0) > 0;

  const waitingCount = set?.questions.filter((q) => q.status === "proposed").length ?? 0;

  return (
    <section aria-labelledby="questions-heading" className="panel">
      <div className="panel-header">
        <div>
          <h2 id="questions-heading">Interview questions</h2>
          <p className="note">Each question is decided on its own. Nothing is final until you confirm the set.</p>
        </div>
        <div className="toolbar">
          <div className="stack stage-field">
            <label htmlFor="stage">Stage</label>
            <select id="stage" value={stage} onChange={(event) => setStage(event.target.value)} disabled={busy}>
              {stages.map((name) => (
                <option key={name} value={name}>
                  {stageLabel(name)}
                </option>
              ))}
            </select>
          </div>
          <button
            type="button"
            className={hasQuestions ? undefined : "primary"}
            onClick={() => run(() => api.proposeQuestions(slug, stage))}
            disabled={busy || !stage || set?.confirmed}
          >
            Propose questions
          </button>
        </div>
      </div>

      {loading && <StateMessage kind="loading">Loading questions…</StateMessage>}
      {!loading && set && !hasQuestions && <StateMessage kind="empty">No questions yet for this stage.</StateMessage>}

      <ul className="questions">
        {set?.questions.map((question) => (
          <li key={question.id} className="card">
            {editing?.id === question.id ? (
              <div className="stack">
                <label htmlFor={`q-${question.id}`}>Question</label>
                <textarea
                  id={`q-${question.id}`}
                  rows={2}
                  value={editing.values.question}
                  onChange={(event) => setEditing({ id: question.id, values: { ...editing.values, question: event.target.value } })}
                />
                <label htmlFor={`p-${question.id}`}>Purpose</label>
                <textarea
                  id={`p-${question.id}`}
                  rows={2}
                  value={editing.values.purpose}
                  onChange={(event) => setEditing({ id: question.id, values: { ...editing.values, purpose: event.target.value } })}
                />
                <label htmlFor={`g-${question.id}`}>What a good answer covers</label>
                <textarea
                  id={`g-${question.id}`}
                  rows={2}
                  value={editing.values.good_answer}
                  onChange={(event) => setEditing({ id: question.id, values: { ...editing.values, good_answer: event.target.value } })}
                />
                <div className="row">
                  <button type="button" disabled={busy} onClick={() => decide(question, "edit", editing.values)}>
                    Save edit
                  </button>
                  <button type="button" disabled={busy} onClick={() => setEditing(null)}>
                    Cancel
                  </button>
                </div>
              </div>
            ) : (
              <>
                <div className="card-head">
                  <p className="question-text">{question.question}</p>
                  <span className={`chip ${statusChipClass(question.status)}`}>{statusLabel(question.status)}</span>
                </div>
                <p className="muted">Purpose: {question.purpose}</p>
                <p className="muted">A good answer covers: {question.good_answer}</p>
                {!set?.confirmed && (
                  <div className="row">
                    {question.status !== "approved" && (
                      <button type="button" className="primary-outline" disabled={busy} onClick={() => decide(question, "approve")}>
                        Approve
                      </button>
                    )}
                    <button
                      type="button"
                      disabled={busy}
                      onClick={() => setEditing({
                        id: question.id,
                        values: { question: question.question, purpose: question.purpose, good_answer: question.good_answer },
                      })}
                    >
                      Edit
                    </button>
                    <button type="button" disabled={busy} onClick={() => decide(question, "reject")}>
                      Reject
                    </button>
                  </div>
                )}
              </>
            )}
          </li>
        ))}
      </ul>

      {set && hasQuestions && (
        <div className="footer">
          {set.confirmed ? (
            <StateMessage kind="success">The {set.stage} set is confirmed.</StateMessage>
          ) : (
            <>
              <span className="muted">
                {approvedCount} approved · {waitingCount} waiting for your decision
              </span>
              <button
                type="button"
                className="primary"
                disabled={busy || approvedCount === 0}
                onClick={() => run(() => api.confirmQuestions(slug, stage))}
              >
                Confirm approved set ({approvedCount})
              </button>
            </>
          )}
        </div>
      )}

      {error && <StateMessage kind="error">{error}</StateMessage>}
    </section>
  );
}

function stageLabel(name: string): string {
  return name.charAt(0).toUpperCase() + name.slice(1);
}

function statusLabel(status: Question["status"]): string {
  return status.charAt(0).toUpperCase() + status.slice(1);
}

function statusChipClass(status: Question["status"]): string {
  if (status === "approved") return "chip-approved";
  if (status === "rejected") return "chip-rejected";
  return "";
}
