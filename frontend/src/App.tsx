import { useEffect, useState } from "react";
import { api } from "./api";
import { HealthBadge } from "./components/HealthBadge";
import { StateMessage } from "./components/StateMessage";
import { JobTalk } from "./components/JobTalk";
import { QuestionReview } from "./components/QuestionReview";
import type { Health, Position } from "./types";

type Tab = "job" | "questions";

export function App() {
  const [health, setHealth] = useState<Health | null>(null);
  const [healthError, setHealthError] = useState<string | null>(null);
  const [positions, setPositions] = useState<Position[]>([]);
  const [selected, setSelected] = useState<string | null>(null);
  const [tab, setTab] = useState<Tab>("job");
  const [newTitle, setNewTitle] = useState("");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .health()
      .then(setHealth)
      .catch((err: unknown) => setHealthError(err instanceof Error ? err.message : String(err)));
    api
      .listPositions()
      .then(setPositions)
      .catch((err: unknown) => setError(err instanceof Error ? err.message : String(err)));
  }, []);

  async function addPosition(event: React.FormEvent) {
    event.preventDefault();
    setError(null);
    try {
      const position = await api.createPosition(newTitle);
      setPositions((current) => [...current, position]);
      setSelected(position.slug);
      setNewTitle("");
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    }
  }

  const current = positions.find((position) => position.slug === selected) ?? null;

  return (
    <div className="shell">
      <aside className="sidebar">
        <div className="brand">
          <span className="brand-mark" aria-hidden="true">
            O
          </span>
          <span>Onboarding interview</span>
        </div>

        <section aria-labelledby="positions-heading">
          <h2 id="positions-heading" className="eyebrow">
            Positions
          </h2>
          <ul className="positions">
            {positions.map((position) => {
              const isOpen = selected === position.slug;
              return (
                <li key={position.slug}>
                  <button
                    type="button"
                    className="position"
                    aria-pressed={isOpen}
                    onClick={() => setSelected(position.slug)}
                  >
                    <span>{position.title}</span>
                    {isOpen && <span className="position-open">Open</span>}
                  </button>
                </li>
              );
            })}
          </ul>
        </section>

        <form onSubmit={addPosition} className="new-position">
          <label htmlFor="new-position">New position</label>
          <input
            id="new-position"
            placeholder="For example, Head of Sales"
            value={newTitle}
            onChange={(event) => setNewTitle(event.target.value)}
          />
          <button type="submit" disabled={!newTitle.trim()}>
            Add position
          </button>
        </form>
        {error && <StateMessage kind="error">{error}</StateMessage>}
      </aside>

      <main className="workspace">
        <header className="page-header">
          <div>
            <p className="breadcrumb">{current ? `Positions / ${current.title}` : "Positions"}</p>
            <h1 className="page-title">{current ? current.title : "Choose a position"}</h1>
          </div>
          <HealthBadge health={health} error={healthError} />
        </header>

        {selected && (
          <>
            <nav aria-label="Sections" className="segmented">
              <button
                type="button"
                className="segment"
                aria-pressed={tab === "job"}
                onClick={() => setTab("job")}
              >
                Job description
              </button>
              <button
                type="button"
                className="segment"
                aria-pressed={tab === "questions"}
                onClick={() => setTab("questions")}
              >
                Interview questions
              </button>
            </nav>
            {tab === "job" ? <JobTalk key={selected} slug={selected} /> : <QuestionReview key={selected} slug={selected} />}
          </>
        )}
      </main>
    </div>
  );
}
