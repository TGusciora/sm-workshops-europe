import { useEffect, useState } from "react";
import { api, ApiError } from "../api";
import type { ChatMessage, Draft } from "../types";
import { StateMessage } from "./StateMessage";

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
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [savedPath, setSavedPath] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setError(null);
    setSavedPath(null);
    setLoading(true);
    Promise.all([api.getChat(slug), api.getJobDescription(slug)])
      .then(([chat, jd]) => {
        if (cancelled) return;
        setMessages(chat.messages);
        setDraft(chat.draft);
        setDraftText(chat.draft?.text ?? "");
        setCurrentText(jd.text);
      })
      .catch((err: unknown) => !cancelled && setError(message(err)))
      .finally(() => !cancelled && setLoading(false));
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

  if (loading) {
    return (
      <section aria-labelledby="conversation-heading" className="panel">
        <h2 id="conversation-heading">Conversation</h2>
        <StateMessage kind="loading">Loading the job description…</StateMessage>
      </section>
    );
  }

  return (
    <section aria-labelledby="conversation-heading" className="panel">
      <div className="panel-header">
        <div>
          <h2 id="conversation-heading">Conversation</h2>
          <p className="note">Nothing is saved until you accept a draft</p>
        </div>
      </div>

      <details>
        <summary>Current job description</summary>
        <pre className="code-block">{currentText ?? "No job description saved yet."}</pre>
      </details>

      <ol className="chat" aria-label="Conversation">
        {messages.map((item, index) => (
          <li key={index} className={`msg msg-${item.role}`}>
            {item.role === "assistant" && (
              <span className="avatar" aria-hidden="true">
                A
              </span>
            )}
            <p className="bubble">
              <span className="sr-only">{item.role === "user" ? "You: " : "Assistant: "}</span>
              {item.content}
            </p>
          </li>
        ))}
      </ol>

      {draft && (
        <div className="draft" aria-label="Draft">
          <div className="card-head">
            <h3>Draft · not saved</h3>
            <span className="chip chip-accent">Needs your decision</span>
          </div>
          <label htmlFor="draft-text">Edit the draft before accepting</label>
          <textarea
            id="draft-text"
            rows={14}
            value={draftText}
            onChange={(event) => setDraftText(event.target.value)}
            disabled={busy}
          />
          <div className="row draft-actions">
            <button type="button" className="primary" onClick={() => decide(false)} disabled={busy}>
              {draftText === draft.text ? "Accept draft" : "Accept edited draft"}
            </button>
            <button type="button" onClick={() => decide(true)} disabled={busy}>
              Reject draft
            </button>
          </div>
        </div>
      )}

      {savedPath && <StateMessage kind="success">Saved to {savedPath}.</StateMessage>}
      {error && <StateMessage kind="error">{error}</StateMessage>}

      <form onSubmit={send} className="stack composer">
        <label htmlFor="chat-input">Message</label>
        <textarea
          id="chat-input"
          rows={3}
          placeholder="Ask for a change to the job description"
          value={input}
          onChange={(event) => setInput(event.target.value)}
          disabled={busy}
        />
        <button type="submit" disabled={busy || !input.trim()}>
          Send
        </button>
      </form>
    </section>
  );
}

function message(err: unknown): string {
  return err instanceof ApiError || err instanceof Error ? err.message : String(err);
}
