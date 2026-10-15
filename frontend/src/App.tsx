import { useEffect, useState } from "react";
import { api } from "./api";
import { HealthBadge } from "./components/HealthBadge";
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

  return (
    <main>
      <header>
        <h1>Onboarding interview</h1>
        <HealthBadge health={health} error={healthError} />
      </header>

      <section aria-labelledby="positions-heading" className="panel">
        <h2 id="positions-heading">Positions</h2>
        <ul className="positions">
          {positions.map((position) => (
            <li key={position.slug}>
              <button
                type="button"
                aria-pressed={selected === position.slug}
                onClick={() => setSelected(position.slug)}
              >
                {position.title}
              </button>
            </li>
          ))}
        </ul>
        <form onSubmit={addPosition} className="row">
          <label htmlFor="new-position">New position</label>
          <input
            id="new-position"
            value={newTitle}
            onChange={(event) => setNewTitle(event.target.value)}
          />
          <button type="submit" disabled={!newTitle.trim()}>
            Add position
          </button>
        </form>
        {error && <p role="alert" className="error">{error}</p>}
      </section>

      {selected && (
        <>
          <nav aria-label="Sections" className="tabs">
            <button type="button" aria-pressed={tab === "job"} onClick={() => setTab("job")}>
              Job description
            </button>
            <button type="button" aria-pressed={tab === "questions"} onClick={() => setTab("questions")}>
              Interview questions
            </button>
          </nav>
          {tab === "job" ? <JobTalk key={selected} slug={selected} /> : <QuestionReview key={selected} slug={selected} />}
        </>
      )}
    </main>
  );
}
