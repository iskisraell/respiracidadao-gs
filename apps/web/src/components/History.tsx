import type { Level } from "../types";
import { LEVEL_NAME } from "../format";

const LEVEL_Y: Record<Level, number> = { normal: 2, atencao: 1, critico: 0 };

/** Últimas leituras do lugar: um ponto por medida, na faixa do nível. */
export function History({ points }: { points: { nivel: Level; criado_em: string }[] }) {
  const w = 100 / Math.max(points.length, 1);
  return (
    <figure className="history">
      <figcaption>Últimas {points.length} medidas</figcaption>
      <div className="history-row" role="img" aria-label={points.map((p) => LEVEL_NAME[p.nivel]).join(", ")}>
        {points.map((p, i) => (
          <span key={i} className={`tick ${p.nivel}`} style={{ width: `${w}%`, height: `${34 + (2 - LEVEL_Y[p.nivel]) * 33}%` }} title={`${LEVEL_NAME[p.nivel]} às ${new Date(p.criado_em).toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" })}`} />
        ))}
      </div>
    </figure>
  );
}
