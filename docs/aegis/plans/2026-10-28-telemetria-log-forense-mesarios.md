# Plano de Implementação: Telemetria Forense de Cabine, Log e Conduta de Mesários

**Data:** 2026-10-28  
**Spec de Referência:** `docs/superpowers/specs/2026-10-28-telemetria-log-forense-mesarios-design.md`  
**Objetivo:** Decodificar os arquivos de log da urna eletrônica (`log.jez` $\to$ `logd.dat`) para extrair evidências materiais de flagrante de biometria de mesário em eleitores (`CHK121`), votação em esteira rápida/robótica (`CHK122`), surto manual no almoço (`CHK123`) e concentração desproporcional de liberações por mesário específico (`CHK124`), integrando gráficos de telemetria de cabine ao relatório HTML multi-estadual.

---

## Cabeçalho de Governança

```text
TDD Route:
- Mode: off
- Decision: skipped
- Strict authority: not applicable
- Test posture: post-change regression
- Reason: Desenvolvimento modular sobre parsers ASN.1/Log existentes, com testes unitários e de integração via pytest.
- Verification: pytest tests/test_logd.py tests/test_comparison.py
```

```text
Change Necessity:
- User-visible need: Evidenciar flagrantes materiais gravados no log (digital de mesário em eleitores, votação relâmpago e responsabilização nominal de mesários).
- No-change / non-code option: Insuficiente, pois o BU não discrimina o tempo individual de cada voto na cabine nem quem foi o mesário autorizador.
- Why code change is necessary: Requer decodificação em memória do container log.jez e análise de sequências de eventos no logd.dat.
- Minimum change boundary: src/urna_forense/parsers/logd.py, src/urna_forense/comparison.py, build_multistate_consolidated_report.py e tests/.
- Decision: code-change
```

---

## Mapeamento de Arquivos

| Arquivo | Ação | Responsabilidade |
|---|:---:|---|
| `src/urna_forense/parsers/logd.py` | Modificar | Adicionar função `extract_cabin_telemetry(events)` para mapear duração da cabine por voto, intervalos de troca e flagrantes de mesário. |
| `src/urna_forense/comparison.py` | Modificar | Adicionar detectores `CHK121`, `CHK122`, `CHK123`, `CHK124` no catálogo, worker de extração de log em lote e cards de telemetria no HTML. |
| `build_multistate_consolidated_report.py` | Modificar | Integrar métricas de telemetria de cabine e mesários ao gerador consolidado multi-estadual (SC + MG). |
| `tests/test_logd.py` | Modificar | Testes unitários para extração de tempo de cabine e flagrantes de biometria de mesário. |
| `tests/test_comparison.py` | Modificar | Testes para disparo das regras `CHK121` a `CHK124` em fixtures sintéticas. |
| `README.md` | Modificar | Documentar os novos detectores no catálogo de 124 regras e adicionar estatísticas consolidadas de cabine. |

---

## Tarefas de Implementação

### Tarefa 1: Extrator de Telemetria de Cabine e Eventos de Mesário em `logd.py`
- **Arquivos:** `src/urna_forense/parsers/logd.py`
- **O que faz:**
  1. Implementa a função `extract_cabin_telemetry(events: list[LogEvent]) -> dict[str, Any]` que percorre ordenadamente os eventos de votação:
     - Detecta cada ciclo `Urna pronta para receber votos` $\to$ `O voto do eleitor foi computado`, calculando `duracao_cabine_segundos`.
     - Detecta `VOTE.HABILITATION` determinando se o voto foi `BIOMETRICA` ou `MANUAL` (ano de nascimento).
     - Captura o identificador do mesário autorizador (`Mesário [ID] habilitou o eleitor`).
     - Detecta eventos de alerta: `Biometria do mesário .* encontrada em eleitores`.
     - Calcula histograma de tempos de cabine (< 10s, 10-20s, 20-45s, > 45s).
- **Verificação:** Executar teste focado com log sintético contendo 3 eleitores (um biométrico, um manual e um flagrante de mesário).

### Tarefa 2: Implementação dos Detectores `CHK121`, `CHK122`, `CHK123` e `CHK124` em `comparison.py`
- **Arquivos:** `src/urna_forense/comparison.py`
- **O que faz:**
  1. Expande `RULE_HUMAN_TITLES` e `GLOSSARY_DATA` para incluir os 4 novos códigos com títulos didáticos e justificativas periciais.
  2. Implementa a lógica de avaliação das anomalias:
     - `CHK121`: Se `len(flagrantes_mesario) > 0`.
     - `CHK122`: Se `votos_sub10s_contagem >= 3` consecutivos ou `pct_sub10s > 10%`.
     - `CHK123`: Se `pct_manuais_almoco > 30%` e taxa do almoço > 2x a taxa média.
     - `CHK124`: Se um único mesário autorizou > 80% das liberações manuais da seção.
- **Verificação:** `pytest tests/test_comparison.py`

### Tarefa 3: Pipeline de Extração Multithread do Log em Urnas Relevantes
- **Arquivos:** `src/urna_forense/comparison.py`
- **O que faz:**
  1. Durante a fase de processamento, identifica o arquivo `*-log.jez` correspondente a cada seção do 2º turno.
  2. Para as urnas que apresentaram anomalias preliminares de hardware/biometria ou fechamento tardio, abre o container `log.jez` em memória e extrai a telemetria via `extract_cabin_telemetry`.
  3. Anexa o objeto `telemetria_log` ao dicionário da seção no relatório JSON.
- **Verificação:** Testar sobre uma amostra de 10 seções de SC e MG verificando preenchimento de `telemetria_log`.

### Tarefa 4: Atualização da Interface Visual e Gráficos no Relatório HTML
- **Arquivos:** `src/urna_forense/comparison.py` e `build_multistate_consolidated_report.py`
- **O que faz:**
  1. Adiciona o painel visual **`AUDITORIA DE TELEMETRIA DE CABINE E CONDUTA DE MESÁRIOS`** com:
     - Histograma em barras das faixas de tempo de cabine.
     - Card de flagrantes `CHK121` e concentração `CHK124`.
     - Curva horária comparando horário de almoço vs restante do dia.
  2. No modal da seção (`detailsModal`):
     - Exibe a velocidade média de cabine da urna e alertas em vermelho se < 10s.
     - Tabela nominal com o Título/CPF dos mesários e a contagem de liberações manuais.
     - Linha literal do log caso haja flagrante de digital de mesário.
- **Verificação:** Abrir o HTML gerado e validar visualmente os cards, gráficos e modais.

### Tarefa 5: Suíte de Testes Automatizados
- **Arquivos:** `tests/test_logd.py` e `tests/test_comparison.py`
- **O que faz:**
  1. Cria testes para `extract_cabin_telemetry` cobrindo cálculo de tempo e eventos de mesário.
  2. Adiciona asserções para o disparo correto de `CHK121`, `CHK122`, `CHK123` e `CHK124`.
- **Verificação:** `pytest` (assegurar que todos os testes passem com 100% de sucesso).

### Tarefa 6: Execução sobre os Dados Reais de SC e MG e Atualização do README
- **Arquivos:** `README.md`, `comparison_consolidado_sc_mg/`
- **O que faz:**
  1. Executa o enriquecimento de telemetria sobre o conjunto de seções anômalas de SC e MG.
  2. Regenera os relatórios HTML e JSON consolidados.
  3. Atualiza o `README.md` documentando o catálogo de 124 regras e as evidências de cabine.
  4. Comita e sincroniza com o repositório no GitHub.
- **Verificação:** Conferência visual do relatório regenerado e validação do git status.
