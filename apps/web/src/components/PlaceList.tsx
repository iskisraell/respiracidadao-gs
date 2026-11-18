import { School, Stethoscope, Trees } from "lucide-react";
import type { Place } from "../types";
import { LEVEL_NAME } from "../format";

export const PLACE_ICON = { escola: School, ubs: Stethoscope, praca: Trees };

export function PlaceList({ places, selected, onSelect }: { places: Place[]; selected?: string; onSelect: (id: string) => void }) {
  return (
    <section aria-label="Lugares monitorados">
      <h1 className="question">Como está o ar agora?</h1>
      <div className="places" role="tablist">
        {places.map((p) => {
          const Icon = PLACE_ICON[p.tipo];
          return (
            <button key={p.id} role="tab" aria-selected={p.id === selected} className="place" onClick={() => onSelect(p.id)}>
              <Icon size={18} aria-hidden="true" />
              <span className="place-name">
                {p.nome}
                <small>{p.bairro}</small>
              </span>
              <span className={`dot ${p.nivel ?? "vazio"}`} title={p.nivel ? LEVEL_NAME[p.nivel] : "Sem leitura"} />
            </button>
          );
        })}
      </div>
    </section>
  );
}
