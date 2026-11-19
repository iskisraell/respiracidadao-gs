# 03 — Cognitive Cybersecurity (`Protótipo CitizenTech com Dados e IA`)

- **Portal ID:** `codigoTrabalho=28360`, `codigoTrabalhoGrupo=729138`
- **Prazo:** `19/11/2026 23:55:00` *(não entregue)*
- **Formação:** Individual ou em grupo de até 3 participantes
- **Entrega:** Portal do Aluno
- **Enunciado original:** [`GS - 2026.2 - Cybersecurity - 1TIAPZ(1).pdf`](./enunciado/GS%20-%202026.2%20-%20Cybersecurity%20-%201TIAPZ(1).pdf)

---

## Objetivo

Atuar como uma **consultoria de segurança** responsável por avaliar os riscos do protótipo CitizenTech desenvolvido pelo grupo, identificando vulnerabilidades, ameaças, conformidade LGPD e implementando controles reais de proteção para usuários, dados, modelos de IA, infraestrutura e privacidade.

> Escolher **apenas um público-alvo e um problema principal** (o mesmo das demais disciplinas CitizenTech).

---

## Requisitos Técnicos Obrigatórios (7 Seções)

### 1. Descrição da Solução CitizenTech
- Problema escolhido, público-alvo, uso de IA, dados utilizados e arquitetura simplificada (`Usuário | Aplicação | Banco de Dados | Modelo de IA`).

### 2. Mapeamento de Superfície de Ataque
Identificar ameaças em **pelo menos 5 camadas**:
- **Usuários** (ex.: acesso indevido, senha fraca)
- **Aplicação** (ex.: SQL Injection, XSS, falha de autenticação)
- **API** (ex.: abuso de requisições)
- **Banco de Dados** (ex.: vazamento, exposição indevida)
- **Modelo de IA** (ex.: manipulação de dados, *model poisoning*)

### 3. Matriz de Riscos
Apresentar **no mínimo 5 riscos** com Impacto e Probabilidade (ex.: roubo de credenciais, vazamento de dados, ataque à API, engenharia social, alteração do modelo de IA).

### 4. Controles de Segurança
Propor controles para os riscos identificados:
- Autenticação (MFA, política de senhas)
- Firewall / WAF
- Backup e recuperação de incidentes
- Criptografia (dados em trânsito e em repouso)
- Monitoramento (logs, alertas)

### 5. Demonstração Obrigatória (>= 1 Proteção Funcionando)
> *"Não basta propor. É necessário demonstrar com evidências."*

Implementar **pelo menos UMA proteção funcional** (exemplos aceitos):
1. Proxy com bloqueio de categorias
2. Firewall / UFW bloqueando acesso
3. Rate Limiting *(fácil de demonstrar na API Python/Lambda!)*
4. Validação de login
5. Registro de logs
6. Criptografia de dados
7. Hash de integridade
8. Controle de acesso baseado em perfil (RBAC)

### 6. LGPD
Responder objetivamente:
- Quais dados pessoais são tratados?
- Quais dados sensíveis podem existir?
- Quais proteções serão aplicadas?
- Como o usuário será informado?

### 7. Engenharia Social
Apresentar:
- **Cenário de ataque** (ex.: phishing, WhatsApp falso, e-mail falso)
- **Contramedidas** (ex.: treinamento, conscientização, MFA)

---

## Entregáveis

- [ ] **PDF (máximo 15 páginas)** contendo: Solução CitizenTech, Arquitetura, Riscos, Controles, LGPD e Demonstração (com capa/integrantes).
- [ ] **Vídeo Pitch (máximo 5 minutos)** demonstrando: problema, solução, riscos e a proteção implementada funcionando.

---

## Critérios de Avaliação (10 pontos)

| Critério | Pontos |
|---|---:|
| Identificação de ameaças e vulnerabilidades | 2,0 |
| Qualidade da análise de riscos | 2,0 |
| Implementação de proteção funcional | 3,0 |
| Privacidade e LGPD | 1,0 |
| Justificativa técnica das escolhas | 1,0 |
| Apresentação / Pitch | 1,0 |
| **Total** | **10,0** |

---

## Workspace / Notas de Trabalho

- **Proteção funcional escolhida para implementar + evidenciar:** `TODO`
- **Link do Vídeo Pitch (<=5 min):** `TODO`
