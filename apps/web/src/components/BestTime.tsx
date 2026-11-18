import { Sun } from "lucide-react";
import type { HourPattern } from "../types";

/** Quando o ar costuma estar ruim: fração de horas críticas em cada hora do dia. */
export function BestTime({ pattern }: { pattern: HourPattern }) {
  const { inicio, fim, critico_medio, pior_hora, pior_critico } = pattern.melhor_janela;
  const now = new Date().getHours();
  const max = Math.max(...pattern.horas.map((h) => h.critico + h.atencao));
  const vezes = (pior_critico / critico_medio).toFixed(1).replace(".", ",");

  return (
    <section className="card">
      <h3>
        <Sun size={18} aria-hidden="true" /> Horário que costuma ter ar melhor
      </h3>
      <p className="big">
        {inicio}h às {fim}h
      </p>
      <p className="muted">
        Às {pior_hora}h, o ar ruim foi {vezes} vezes mais comum. Média de 6.941 horas medidas numa cidade italiana em 2004 e 2005; vale como ponto de partida até o sensor deste lugar juntar o próprio histórico.
      </p>
      <div className="hours" role="img" aria-label={`Ar ruim é mais comum às ${pior_hora}h e menos comum entre ${inicio}h e ${fim}h`}>
        {pattern.horas.map((h) => (
          <div key={h.hora} className={`hour ${h.hora >= inicio && h.hora < fim ? "best" : ""} ${h.hora === now ? "now" : ""}`}>
            <span className="bar atencao" style={{ height: `${(h.atencao / max) * 100}%` }} />
            <span className="bar critico" style={{ height: `${(h.critico / max) * 100}%` }} />
            {h.hora % 6 === 0 && <small>{h.hora}h</small>}
          </div>
        ))}
      </div>
      <p className="legend">
        <i className="sq critico" /> ar ruim <i className="sq atencao" /> ar carregado <i className="sq now" /> agora
      </p>
    </section>
  );
}
