import { useEffect, useState } from "react";
import { api, ApiError } from "../api";
import type { ChatMessage, Draft } from "../types";

interface Props {
  slug: string;
}

// Chat with the assistant about a job description. The draft is shown apart from
// the chat and is written to hiring/ only when the hiring manager accepts it (ADR-0005).
export function JobTalk({ slug }: Props) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [draft, setDraft] = useState<Draft | null>(null);
  const [draftText, setDraftText] = useState("");
  const [currentText, setCurrentText] = useState<string | null>(null);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [savedPath, setSavedPath] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setError(null);
    setSavedPath(null);
    Promise.all([api.getChat(slug), api.getJobDescription(slug)])
      .then(([chat, jd]) => {
        if (cancelled) return;
        setMessages(chat.messages);
        setDraft(chat.draft);
        setDraftText(chat.draft?.text ?? "");
        setCurrentText(jd.text);
      })
      .catch((err: unknown) => !cancelled && setError(message(err)));
    return () => {
      cancelled = true;
    };
  }, [slug]);

  async function send(event: React.FormEvent) {
    event.preventDefault();
    if (!input.trim()) return;
    setBusy(true);
    setError(null);
    try {
      const chat = await api.sendChat(slug, input.trim());
      setMessages(chat.messages);
      setDraft(chat.draft);
      setDraftText(chat.draft?.text ?? "");
      setSavedPath(null);
      setInput("");
    } catch (err) {
      setError(message(err));
    } finally {
      setBusy(false);
    }
  }

  async function decide(reject: boolean) {
    if (!draft) return;
    setBusy(true);
    setError(null);
    try {
      // Accepting an unchanged draft is "approve"; accepting changed text is "edit".
      const action = reject ? "reject" : draftText === draft.text ? "approve" : "edit";
      const result = await api.decideDraft(draft.id, action, draftText);
      setDraft(null);
      setSavedPath(result.path);
      if (result.path) setCurrentText(draftText);
    } catch (err) {
      setError(message(err));
    } finally {
      setBusy(false);
    }
  }

  return (
    <section aria-labelledby="job-talk-heading" className="panel">
      <h2 id="job-talk-heading">Job description</h2>

      <details>
        <summary>Current job description</summary>
        <pre className="scroll">{currentText ?? "No job description saved yet."}</pre>
      </details>

      <ol className="chat" aria-label="Conversation">
        {messages.map((item, index) => (
          <li key={index} className={`msg msg-${item.role}`}>
            <strong>{item.role === "user" ? "You" : "Assistant"}:</strong> {item.content}
          </li>
        ))}
      </ol>

      <form onSubmit={send} className="stack">
        <label htmlFor="chat-input">Message</label>
        <textarea
          id="chat-input"
          rows={3}
          value={input}
          onChange={(event) => setInput(event.target.value)}
          disabled={busy}
        />
        <button type="submit" disabled={busy || !input.trim()}>
          Send
        </button>
      </form>

      {draft && (
        <div className="draft" aria-label="Draft">
          <h3>Draft (not saved)</h3>
          <label htmlFor="draft-text">Edit the draft before accepting</label>
          <textarea
            id="draft-text"
            rows={14}
            value={draftText}
            onChange={(event) => setDraftText(event.target.value)}
            disabled={busy}
          />
          <div className="row">
            <button type="button" onClick={() => decide(false)} disabled={busy}>
              {draftText === draft.text ? "Accept draft" : "Accept edited draft"}
            </button>
            <button type="button" onClick={() => decide(true)} disabled={busy}>
              Reject draft
            </button>
          </div>
        </div>
      )}

      {savedPath && <p role="status">Saved to {savedPath}.</p>}
      {error && <p role="alert" className="error">{error}</p>}
    </section>
  );
}

function message(err: unknown): string {
  return err instanceof ApiError || err instanceof Error ? err.message : String(err);
}
