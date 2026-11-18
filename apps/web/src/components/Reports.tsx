import { useState } from "react";
import { AlertTriangle, MessageCircle } from "lucide-react";
import { api } from "../api";
import type { Place } from "../types";
import { ago } from "../format";

export function Reports({ place, onSent }: { place: Place; onSent: () => void }) {
  const [text, setText] = useState("");
  const [status, setStatus] = useState<{ ok: boolean; msg: string } | null>(null);
  const [busy, setBusy] = useState(false);

  async function send(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    try {
      const r = await api.report(place.id, text.trim());
      setText("");
      setStatus({ ok: true, msg: r.urgente ? "Recebido e marcado como urgente." : "Recebido. Obrigado por avisar." });
      onSent();
    } catch (err) {
      setStatus({ ok: false, msg: (err as Error).message });
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="card">
      <h3>
        <MessageCircle size={18} aria-hidden="true" /> Quem está lá conta
      </h3>
      {place.relatos.length === 0 ? (
        <p className="muted">Ninguém relatou nada perto de {place.nome} ainda.</p>
      ) : (
        <ul className="reports">
          {place.relatos.map((r) => (
            <li key={r.id}>
              <p>{r.texto}</p>
              <small>
                {r.urgente && (
                  <span className="urgent">
                    <AlertTriangle size={12} aria-hidden="true" /> urgente
                  </span>
                )}
                {ago(r.criado_em)}
              </small>
            </li>
          ))}
        </ul>
      )}
      <form onSubmit={send} className="report-form">
        <label htmlFor="relato">Viu fumaça ou sentiu cheiro forte?</label>
        <textarea id="relato" value={text} onChange={(e) => setText(e.target.value)} maxLength={300} rows={2} placeholder="Ex.: cheiro de queimada no portão da escola" />
        <div className="row">
          <small className="muted">Sem nome, sem localização sua. Só o texto.</small>
          <button disabled={busy || text.trim().length < 3}>{busy ? "Enviando…" : "Enviar"}</button>
        </div>
        {status && <p className={status.ok ? "ok" : "err"} role="status">{status.msg}</p>}
      </form>
    </section>
  );
}
