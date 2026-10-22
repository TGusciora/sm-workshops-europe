import { useEffect, useState } from "react";
import { api } from "../api";
import type { Interview, InterviewInput } from "../types";
import { StateMessage } from "./StateMessage";

interface Props {
  slug: string;
}

// The form state. Date and time are kept apart because the browser inputs use them apart.
interface Form {
  stage: string;
  date: string;
  time: string;
  duration: string;
  interviewer: string;
  location: string;
  candidateRef: string;
}

const blankForm = (stage: string): Form => ({
  stage,
  date: "",
  time: "",
  duration: "60",
  interviewer: "",
  location: "",
  candidateRef: "",
});

function toInput(form: Form): InterviewInput {
  return {
    stage: form.stage,
    starts_at: `${form.date}T${form.time}`,
    duration_minutes: Number(form.duration),
    interviewer: form.interviewer,
    location: form.location,
    candidate_ref: form.candidateRef,
  };
}

function toForm(interview: Interview): Form {
  const [date, time] = interview.starts_at.split("T");
  return {
    stage: interview.stage,
    date,
    time: time.slice(0, 5),
    duration: String(interview.duration_minutes),
    interviewer: interview.interviewer,
    location: interview.location,
    candidateRef: interview.candidate_ref,
  };
}

// Interviews grouped by the day they start, in the order the API returns them (time order).
function groupByDay(interviews: Interview[]): [string, Interview[]][] {
  const groups = new Map<string, Interview[]>();
  for (const interview of interviews) {
    const day = interview.starts_at.slice(0, 10);
    groups.set(day, [...(groups.get(day) ?? []), interview]);
  }
  return [...groups.entries()];
}

// The interview calendar for one position (F0010). The hiring manager plans, edits and cancels
// every interview. Nothing is sent to a candidate or an interviewer.
export function InterviewCalendar({ slug }: Props) {
  const [stages, setStages] = useState<string[]>([]);
  const [interviews, setInterviews] = useState<Interview[]>([]);
  const [form, setForm] = useState<Form | null>(null);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [confirmingId, setConfirmingId] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .listStages()
      .then((data) => setStages(data.stages))
      .catch((err: unknown) => setError(err instanceof Error ? err.message : String(err)));
  }, []);

  useEffect(() => {
    let cancelled = false;
    setInterviews([]);
    setForm(null);
    setEditingId(null);
    setConfirmingId(null);
    setError(null);
    setLoading(true);
    api
      .listInterviews(slug)
      .then((data) => !cancelled && setInterviews(data))
      .catch((err: unknown) => !cancelled && setError(err instanceof Error ? err.message : String(err)))
      .finally(() => !cancelled && setLoading(false));
    return () => {
      cancelled = true;
    };
  }, [slug]);

  function startPlanning() {
    setError(null);
    setEditingId(null);
    setForm(blankForm(stages[0] ?? ""));
  }

  function startEditing(interview: Interview) {
    setError(null);
    setEditingId(interview.id);
    setForm(toForm(interview));
  }

  function update(field: keyof Form, value: string) {
    setForm((current) => (current ? { ...current, [field]: value } : current));
  }

  async function save(event: React.FormEvent) {
    event.preventDefault();
    if (!form) return;
    setBusy(true);
    setError(null);
    try {
      const input = toInput(form);
      if (editingId === null) {
        await api.planInterview(slug, input);
      } else {
        await api.editInterview(editingId, input);
      }
      setForm(null);
      setEditingId(null);
      // Re-read the agenda so the order matches the server's time order.
      setInterviews(await api.listInterviews(slug));
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setBusy(false);
    }
  }

  async function cancel(interview: Interview) {
    setBusy(true);
    setError(null);
    try {
      const cancelled = await api.cancelInterview(interview.id);
      setInterviews((current) => current.map((i) => (i.id === cancelled.id ? cancelled : i)));
      setConfirmingId(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setBusy(false);
    }
  }

  const days = groupByDay(interviews);

  return (
    <section aria-labelledby="calendar-heading" className="calendar">
      <div className="calendar-header">
        <h2 id="calendar-heading" className="eyebrow">
          Interviews
        </h2>
        {!form && (
          <button type="button" className="primary" onClick={startPlanning} disabled={busy}>
            Plan interview
          </button>
        )}
      </div>

      {error && <StateMessage kind="error">{error}</StateMessage>}
      {loading && <StateMessage kind="loading">Loading interviews…</StateMessage>}

      {form && (
        <form className="interview-form" onSubmit={save} aria-label={editingId === null ? "Plan interview" : "Edit interview"}>
          <label htmlFor="interview-stage">Stage</label>
          <select id="interview-stage" value={form.stage} onChange={(e) => update("stage", e.target.value)}>
            {stages.map((stage) => (
              <option key={stage} value={stage}>
                {stage}
              </option>
            ))}
          </select>

          <label htmlFor="interview-date">Date</label>
          <input id="interview-date" type="date" required value={form.date} onChange={(e) => update("date", e.target.value)} />

          <label htmlFor="interview-time">Start time</label>
          <input id="interview-time" type="time" required value={form.time} onChange={(e) => update("time", e.target.value)} />

          <label htmlFor="interview-duration">Duration (minutes)</label>
          <input
            id="interview-duration"
            type="number"
            min={5}
            max={480}
            required
            value={form.duration}
            onChange={(e) => update("duration", e.target.value)}
          />

          <label htmlFor="interview-interviewer">Interviewer</label>
          <input id="interview-interviewer" required value={form.interviewer} onChange={(e) => update("interviewer", e.target.value)} />

          <label htmlFor="interview-location">Place or meeting link</label>
          <input id="interview-location" value={form.location} onChange={(e) => update("location", e.target.value)} />

          <label htmlFor="interview-candidate">Candidate reference</label>
          <input id="interview-candidate" required value={form.candidateRef} onChange={(e) => update("candidateRef", e.target.value)} />

          <div className="interview-form-actions">
            <button type="submit" className="primary" disabled={busy}>
              {editingId === null ? "Save interview" : "Save changes"}
            </button>
            <button
              type="button"
              onClick={() => {
                setForm(null);
                setEditingId(null);
              }}
            >
              Discard
            </button>
          </div>
        </form>
      )}

      {!loading && interviews.length === 0 && !form && (
        <StateMessage kind="empty">No interviews planned for this position yet.</StateMessage>
      )}

      {days.map(([day, items]) => (
        <section key={day} aria-label={day} className="calendar-day">
          <h3 className="calendar-date">{day}</h3>
          <ul className="calendar-items">
            {items.map((interview) => {
              const cancelled = interview.status === "cancelled";
              return (
                <li key={interview.id} className={cancelled ? "interview cancelled" : "interview"}>
                  <p>
                    <strong>{interview.starts_at.slice(11, 16)}</strong> · {interview.stage} · {interview.duration_minutes} min
                    {cancelled && <span className="interview-status"> Cancelled</span>}
                  </p>
                  <p>
                    {interview.interviewer}
                    {interview.location && ` · ${interview.location}`} · Candidate {interview.candidate_ref}
                  </p>
                  {!cancelled && confirmingId !== interview.id && (
                    <div className="interview-actions">
                      <button type="button" onClick={() => startEditing(interview)} disabled={busy}>
                        Edit
                      </button>
                      <button type="button" onClick={() => setConfirmingId(interview.id)} disabled={busy}>
                        Cancel interview
                      </button>
                    </div>
                  )}
                  {confirmingId === interview.id && (
                    <div className="interview-actions">
                      <StateMessage kind="empty">Cancel this interview? It stays in the list, marked as cancelled.</StateMessage>
                      <button type="button" className="primary" onClick={() => cancel(interview)} disabled={busy}>
                        Yes, cancel it
                      </button>
                      <button type="button" onClick={() => setConfirmingId(null)} disabled={busy}>
                        Keep it
                      </button>
                    </div>
                  )}
                </li>
              );
            })}
          </ul>
        </section>
      ))}
    </section>
  );
}
