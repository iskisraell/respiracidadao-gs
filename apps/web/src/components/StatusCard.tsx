import { CheckCircle2, CloudOff, ShieldCheck } from "lucide-react";
import type { Place, Reading } from "../types";
import { LEVEL_NAME, LIMITS, ago, minutesSince, pct, sensorLevel } from "../format";
import { History } from "./History";

const STALE_MIN = 30;

export function StatusCard({ place }: { place: Place }) {
  const r = place.ultima_leitura;

  if (!r || !place.nivel || !place.orientacao) {
    return (
      <section className="status vazio">
        <p className="status-place">{place.nome}</p>
        <h2>Ainda sem leitura</h2>
        <p>O sensor deste lugar ainda não mandou nenhuma medida. Para ver como fica, use o modo demonstração no fim da página.</p>
      </section>
    );
  }

  const stale = minutesSince(r.criado_em) > STALE_MIN;
  const { titulo, frase, acoes } = place.orientacao;

  return (
    <section className={`status ${place.nivel}`} aria-live="polite">
      <div className="status-head">
        <div>
          <p className="status-place">{place.nome} · {place.bairro}</p>
          <h2>{titulo}</h2>
          <p className="status-lead">{frase}</p>
        </div>
        <span className="badge">{LEVEL_NAME[place.nivel]}</span>
      </div>

      {stale && (
        <p className="note warn">
          <CloudOff size={16} aria-hidden="true" /> A última medida chegou {ago(r.criado_em)}. O sensor pode estar sem internet; a luz dele continua funcionando no local.
        </p>
      )}

      <div className="status-body">
        <div>
          <h3>O que fazer</h3>
          <ul className="actions">
            {acoes.map((a) => (
              <li key={a}>
                <CheckCircle2 size={18} aria-hidden="true" />
                {a}
              </li>
            ))}
          </ul>
        </div>
        <div>
          <h3>O que o sensor mediu {ago(r.criado_em)}</h3>
          <Sensors r={r} />
          <SecondOpinion r={r} />
        </div>
      </div>

      {place.historico.length > 1 && <History points={place.historico} />}
    </section>
  );
}

function Sensors({ r }: { r: Reading }) {
  const voc = r.metrica === "gas_voc" ? r.valor : null;
  const rows: [string, string, string][] = [];
  if (voc != null) rows.push(["Fumaça e gases", sensorWord(sensorLevel(voc, LIMITS.gas_voc)), sensorLevel(voc, LIMITS.gas_voc)]);
  if (r.gas_co != null) rows.push(["Monóxido de carbono", sensorWord(sensorLevel(r.gas_co, LIMITS.gas_co)), sensorLevel(r.gas_co, LIMITS.gas_co)]);
  if (r.temperatura_c != null) rows.push(["Temperatura", `${Math.round(r.temperatura_c)} °C`, ""]);
  if (r.umidade_pct != null) rows.push(["Umidade do ar", `${Math.round(r.umidade_pct)}%`, r.umidade_pct < 30 ? "atencao" : ""]);
  return (
    <dl className="sensors">
      {rows.map(([k, v, lvl]) => (
        <div key={k}>
          <dt>{k}</dt>
          <dd className={lvl}>{v}</dd>
        </div>
      ))}
    </dl>
  );
}

const sensorWord = (l: string) => ({ normal: "baixo", atencao: "elevado", critico: "alto" })[l] ?? l;

function SecondOpinion({ r }: { r: Reading }) {
  if (!r.ia_risco || r.ia_risco_prob == null) return null;
  const agrees = r.ia_risco === r.nivel_risco;
  return (
    <p className="note">
      <ShieldCheck size={16} aria-hidden="true" />
      {agrees
        ? `A central conferiu e concorda: ${LEVEL_NAME[r.ia_risco]}, com ${pct(r.ia_risco_prob)} de certeza.`
        : `A central acha que está ${LEVEL_NAME[r.ia_risco]} (${pct(r.ia_risco_prob)} de certeza). Na dúvida, siga o nível mais cuidadoso.`}
    </p>
  );
}
