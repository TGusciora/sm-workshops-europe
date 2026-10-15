import { useEffect, useState } from "react";
import { api } from "../api";
import type { Decision, Question, QuestionSet } from "../types";

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
    setEditing(null);
    api
      .getQuestions(slug, stage)
      .then((data) => !cancelled && setSet(data))
      .catch((err: unknown) => !cancelled && setError(err instanceof Error ? err.message : String(err)));
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

  return (
    <section aria-labelledby="questions-heading" className="panel">
      <h2 id="questions-heading">Interview questions</h2>

      <div className="row">
        <label htmlFor="stage">Stage</label>
        <select id="stage" value={stage} onChange={(event) => setStage(event.target.value)} disabled={busy}>
          {stages.map((name) => (
            <option key={name} value={name}>
              {name}
            </option>
          ))}
        </select>
        <button type="button" onClick={() => run(() => api.proposeQuestions(slug, stage))} disabled={busy || !stage || set?.confirmed}>
          Propose questions
        </button>
      </div>

      {set && set.questions.length === 0 && <p>No questions yet for this stage.</p>}

      <ul className="questions">
        {set?.questions.map((question) => (
          <li key={question.id} className={`question question-${question.status}`}>
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
                <p className="question-text">{question.question}</p>
                <p className="muted">Purpose: {question.purpose}</p>
                <p className="muted">A good answer covers: {question.good_answer}</p>
                <p className="status">Status: {question.status}</p>
                {!set?.confirmed && (
                  <div className="row">
                    <button type="button" disabled={busy} onClick={() => decide(question, "approve")}>
                      Approve
                    </button>
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

      {set && (
        <div className="row">
          {set.confirmed ? (
            <p role="status">The {set.stage} set is confirmed.</p>
          ) : (
            <button
              type="button"
              disabled={busy || approvedCount === 0}
              onClick={() => run(() => api.confirmQuestions(slug, stage))}
            >
              Confirm approved set ({approvedCount})
            </button>
          )}
        </div>
      )}

      {error && <p role="alert" className="error">{error}</p>}
    </section>
  );
}
