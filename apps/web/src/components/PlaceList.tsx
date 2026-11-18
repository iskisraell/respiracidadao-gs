import { School, Stethoscope, Trees } from "lucide-react";
import type { Place } from "../types";
import { LEVEL_NAME, minutesSince } from "../format";

export const PLACE_ICON = { escola: School, ubs: Stethoscope, praca: Trees };

export function PlaceList({ places, selected, onSelect }: { places: Place[]; selected?: string; onSelect: (id: string) => void }) {
  return (
    <section aria-label="Lugares monitorados">
      <h1 className="question">Como está o ar agora?</h1>
      <div className="places" role="tablist">
        {places.map((p) => {
          const Icon = PLACE_ICON[p.tipo];
          const r = p.ultima_leitura;
          const stale = !!r && r.tipo !== "demo" && minutesSince(r.medido_em ?? r.criado_em) > 30;
          const nivel = stale ? undefined : p.nivel;
          const word = nivel ? LEVEL_NAME[nivel] : r ? "Sem leitura recente" : "Sem leitura";
          return (
            <button key={p.id} role="tab" aria-selected={p.id === selected} className="place" onClick={() => onSelect(p.id)}>
              <Icon size={18} aria-hidden="true" />
              <span className="place-name">
                {p.nome}
                <small>{p.bairro}</small>
              </span>
              <span className={`level-pill ${nivel ?? "vazio"}`}>
                <span className={`dot ${nivel ?? "vazio"}`} aria-hidden="true" />
                {word}
                {nivel && p.sensor_simulado && r?.tipo !== "demo" && <small> · teste</small>}
              </span>
            </button>
          );
        })}
      </div>
    </section>
  );
}
