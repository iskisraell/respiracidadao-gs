import { useState } from "react";
import { api } from "../api";
import type { Level, Place } from "../types";
import { LEVEL_NAME } from "../format";

/** Gera uma leitura típica de um nível, como se viesse do sensor do lugar. Para apresentações e testes. */
export function DemoPanel({ places, onDone }: { places: Place[]; onDone: () => void }) {
  const [open, setOpen] = useState(false);
  const [place, setPlace] = useState("escola-jardim-primavera");
  const [msg, setMsg] = useState("");

  async function run(level: Level) {
    try {
      await api.demo(place, level);
      setMsg(`Leitura "${LEVEL_NAME[level]}" enviada.`);
      onDone();
    } catch (e) {
      setMsg((e as Error).message);
    }
  }

  if (!open) {
    return (
      <button className="link" onClick={() => setOpen(true)}>
        Modo demonstração
      </button>
    );
  }
  return (
    <div className="demo">
      <label>
        Simular leitura em{" "}
        <select value={place} onChange={(e) => setPlace(e.target.value)}>
          {places.map((p) => (
            <option key={p.id} value={p.id}>
              {p.nome}
            </option>
          ))}
        </select>
      </label>
      {(["normal", "atencao", "critico"] as Level[]).map((l) => (
        <button key={l} className={`chip ${l}`} onClick={() => run(l)}>
          {LEVEL_NAME[l]}
        </button>
      ))}
      <button className="link" onClick={() => setOpen(false)}>Fechar</button>
      {msg && <span role="status">{msg}</span>}
    </div>
  );
}
