import { useEffect, useState } from "react";
import { Cpu, Lightbulb, Server, Smartphone, Users } from "lucide-react";
import { api } from "../api";
import type { ModelSummary } from "../types";
import { TryReading } from "./TryReading";

const STEPS = [
  { icon: Cpu, title: "O sensor mede", text: "Uma caixinha na parede mede fumaça, monóxido, temperatura e umidade a cada poucos segundos." },
  { icon: Lightbulb, title: "A luz avisa na hora", text: "Verde, amarelo ou vermelho no próprio local. Funciona mesmo sem internet." },
  { icon: Server, title: "A central confere", text: "A medida chega à central, que compara com 6.941 horas de medição real e diz o nível com uma porcentagem de confiança." },
  { icon: Smartphone, title: "Você vê o que fazer", text: "No app, cada lugar mostra a cor, uma frase simples e as ações do momento." },
  { icon: Users, title: "Vizinhos completam", text: "Quem vê fumaça conta. O relato aparece no lugar e a central marca os urgentes." },
];

const outOf100 = (x: number) => Math.round(x * 100);

export function HowItWorks() {
  const [s, setS] = useState<ModelSummary["machine_learning"]>(null);
  useEffect(() => {
    api.summary().then((r) => setS(r.machine_learning)).catch(() => undefined);
  }, []);
  const regra = s?.comparacao_conjuntos[0];

  return (
    <main className="how">
      <section>
        <h1 className="question">Do sensor ao seu celular</h1>
        <ol className="steps">
          {STEPS.map(({ icon: Icon, title, text }, i) => (
            <li key={title}>
              <span className="step-n">{i + 1}</span>
              <Icon size={22} aria-hidden="true" />
              <h3>{title}</h3>
              <p>{text}</p>
            </li>
          ))}
        </ol>
      </section>

      <section className="card">
        <h3>Dá para confiar?</h3>
        {s && regra ? (
          <div className="trust">
            <p><strong>{outOf100(regra.accuracy)}</strong> de cada 100 horas da base de teste a luz do sensor acertou sozinha.</p>
            <p><strong>{outOf100(s.teste_accuracy)}</strong> de cada 100 horas da base de teste a central acertou.</p>
            <p><strong>{outOf100(s.split_temporal_accuracy)}</strong> de cada 100 horas quando testamos em meses que a central nunca tinha visto.</p>
          </div>
        ) : (
          <p className="muted">Carregando os números…</p>
        )}
        <p>Quando erra, erra para o nível vizinho. Nas 1.389 horas de teste, a central nunca chamou de "bom" uma hora que era "ruim", nem o contrário.</p>
        <p className="muted">
          Os níveis seguem o monóxido de carbono medido por um aparelho de referência: abaixo de 1,5 mg/m³ é bom, de 1,5 a 3 é carregado, acima de 3 é ruim.
        </p>
      </section>

      <TryReading />

      <section className="card">
        <h3>Seus dados</h3>
        <ul className="plain">
          <li>O relato não pede nome, telefone nem localização. Guardamos só o texto e o lugar escolhido.</li>
          <li>Cada medida recebe um selo digital na hora em que chega. Se alguém mudar a medida no banco sem a chave do selo, o selo deixa de bater.</li>
          <li>Ninguém consegue inundar a central: cada endereço pode mandar até 30 envios por minuto.</li>
        </ul>
      </section>

      <section className="card">
        <h3>O que ainda não resolvemos</h3>
        <ul className="plain">
          <li>Por enquanto o sensor roda num simulador. A placa física ainda precisa ser montada e comparada com um medidor oficial antes de valer como medida.</li>
          <li>A central aprendeu com dados de outra cidade. Em cada bairro novo, o sensor precisa ficar algumas semanas ao lado de uma estação oficial para calibrar.</li>
          <li>Sensores de gás perdem precisão com o tempo e precisam de troca ou recalibração.</li>
          <li>A dica de horário é uma média. Num dia de queimada, vale o que o sensor está medindo agora.</li>
        </ul>
      </section>
    </main>
  );
}
