# Especificação Técnica de Design: Telemetria Forense de Cabine, Log e Conduta de Mesários

**Data:** 2026-10-28  
**Status:** Aprovado para Implementação  
**Escopo:** Módulo de Análise Forense de Logs (`log.jez` $\to$ `logd.dat`), Velocidade de Cabine, Flagrante de Mesários e Integração ao Relatório Comparativo Multi-Estadual.

---

## 1. Visão Geral e Objetivos

O sistema atual de auditoria comparativa entre turnos audita 120 regras técnicas baseadas majoritariamente nos metadados dos Boletins de Urna (`bu.dat`) e registros de votos.

Esta especificação define a extensão do motor pericial para decodificar e processar os arquivos de log da urna eletrônica (`log.jez` $\to$ `logd.dat`), extraindo evidências de **comportamento humano e intervenção física direta na máquina**:
1. **Flagrante de Digital do Mesário:** Detecção de eventos oficiais registrados pela urna onde a digital coletada em tentativas de eleitores pertenceu ao mesário cadastrado.
2. **Votação em Esteira / Ritmo Desumano:** Medição do tempo em segundos que cada eleitor permaneceu na cabine (`VOTE.READY` $\to$ `VOTE.COMPUTED`), identificando votos sucessivos em menos de 10 segundos.
3. **Individualização de Conduta por Mesário:** Mapeamento de qual mesário (identificado pelo título/CPF no log) realizou e autenticou cada liberação manual por ano de nascimento.
4. **Surtos de Votação em Horários Desertos:** Identificação de explosões de votos manuais durante o intervalo de almoço (12h00 às 13h30).
5. **Integração Visual no Dashboard:** Gráficos de histograma de tempo de cabine, detalhamento nominal de mesários no modal da seção e expansão do catálogo oficial para **124 regras técnicas** (`CHK121` a `CHK124`).

---

## 2. Arquitetura e Pipeline de Execução

### 2.1 Varredura e Extração Multithread
- **Alvo de Processamento:** Para manter alta performance (sem decodificar desnecessariamente logs de 70 mil urnas normais), o módulo de telemetria processa o `log.jez` de:
  - Todas as urnas com inconsistências relevantes (`worst_severity` em `ALTA` ou `MÉDIA`).
  - Todas as urnas com encerramento após as 17:05:00.
  - Qualquer urna específica inspecionada diretamente pelo usuário.
- **Concorrência:** Descompactação ZIP em memória do `logd.dat` executada via `ThreadPoolExecutor(max_workers=32)`.

### 2.2 Ciclo de Eventos por Eleitor no `logd.dat`
Para cada voto computado, o parser mapeia o ciclo completo:
```text
[Aguardando digitação do identificador] (Início da chamada)
   ├── [Identificador digitado pelo mesário]
   ├── [Solicita digital / Capturada a digital / Batimento]
   │     ├── Ramo A: [Tipo de habilitação do eleitor: biométrica] -> VOTO BIOMÉTRICO
   │     └── Ramo B: [Dado digitado confere (ano de nascimento)] + [Mesário X habilitou] -> VOTO MANUAL
   ├── [Urna pronta para receber votos] (timestamp T_inicio_cabine)
   ├── [Voto confirmado para Presidente]
   └── [O voto do eleitor foi computado] (timestamp T_fim_cabine)
```
- **Duração da Cabine:** $\Delta T_{\text{cabine}} = T_{\text{fim\_cabine}} - T_{\text{inicio\_cabine}}$.
- **Intervalo de Troca:** $\Delta T_{\text{troca}} = T_{\text{inicio\_proximo}} - T_{\text{fim\_anterior}}$.

---

## 3. Catálogo dos 4 Novos Detectores Forenses (`CHK121` a `CHK124`)

### `CHK121_DIGITAL_MESARIO_DETECTADA_EM_ELEITOR`
- **Severidade:** `ALTA` (Crítica).
- **Gatilho:** Presença de evento casando com os padrões oficiais:
  - `Biometria do mesário .* encontrada em eleitores`
  - `Digital coletada bate com uma digital gravada após o registro inicial de mesário`
- **Evidência Pericial:** Flagrante material gerado pelo próprio algoritmo biométrico da urna, indicando que o mesário encostou o dedo no leitor óptico durante a tentativa de habilitação de um eleitor.

### `CHK122_VOTACAO_ESTEIRA_TEMPO_INFERIOR_10S`
- **Severidade:** `ALTA` (Crítica).
- **Gatilho:** Urna com **3 ou mais votos consecutivos** com $\Delta T_{\text{cabine}} < 10\text{ segundos}$ OU onde mais de **10% de todos os votos da seção** foram computados em menos de 10 segundos.
- **Evidência Pericial:** Impossibilidade ergonômica para um eleitor humano real entrar na cabine, ouvir os bipes sonoros, digitar os números, conferir foto e apertar "Confirma". Indica operador operando a urna em esteira mecânica contínua.

### `CHK123_SURTO_MANUAL_HORARIO_DESERTO`
- **Severidade:** `MÉDIA` (Relevante).
- **Gatilho:** Seção onde mais de **30% de todas as liberações manuais por ano de nascimento** ocorreram concentradas entre **12h00 e 13h30**, com taxa de liberação manual nesse horário pelo menos 2 vezes maior que no restante do dia.
- **Evidência Pericial:** Aproveitamento de janela de baixa vigilância (horário de almoço de fiscais de partidos e eleitores) para inserção de votos no lugar de ausentes.

### `CHK124_CONCENTRACAO_DESPROPORCIONAL_POR_MESARIO`
- **Severidade:** `ALTA` (Crítica).
- **Gatilho:** Em seções com 2 ou mais mesários cadastrados, um único mesário foi o autorizador de **mais de 80% de todas as liberações manuais** da seção (mínimo de 30 liberações manuais por aquele mesário).
- **Evidência Pericial:** Individualização de conduta funcional ilícita, descartando erro genérico da mesa e apontando ação deliberada de um mesário específico.

---

## 4. Estrutura de Dados da Telemetria no JSON (`telemetria_log`)

Cada seção enriquecida com a análise do log conterá:

```json
{
  "telemetria_log": {
    "log_disponivel": true,
    "total_votos_log": 340,
    "tempo_medio_cabine_seg": 24.6,
    "votos_sub10s_contagem": 18,
    "votos_sub10s_pct": 5.29,
    "votos_apos_17h": 12,
    "bio_apos_17h": 10,
    "manual_apos_17h": 2,
    "flagrantes_biometria_mesario": [
      {
        "timestamp": "2026-10-25T14:22:18",
        "mesario_id": "002473100906",
        "mensagem": "Biometria do mesário 002473100906 encontrada em eleitores"
      }
    ],
    "mesarios_habilitacao_manual": [
      {
        "mesario_id": "002473100906",
        "liberacoes_manuais": 98,
        "pct_total_manuais": 89.1
      },
      {
        "mesario_id": "031592870922",
        "liberacoes_manuais": 12,
        "pct_total_manuais": 10.9
      }
    ],
    "distribuicao_tempo_cabine": {
      "sub_10s": 18,
      "de_10s_a_20s": 85,
      "de_20s_a_45s": 192,
      "acima_45s": 45
    },
    "votos_por_faixa_horaria": {
      "manha_08_12": {"total": 160, "bio": 142, "manual": 18},
      "almoco_12_14": {"total": 85, "bio": 42, "manual": 43},
      "tarde_14_17": {"total": 83, "bio": 72, "manual": 11},
      "noite_apos_17": {"total": 12, "bio": 10, "manual": 2}
    }
  }
}
```

---

## 5. Interface Visual no Relatório HTML

### 5.1 Bloco Geral: Telemetria de Cabine e Conduta de Mesários
Inserido no dashboard do relatório com:
- **Card Histograma de Cabine:** Visualização em barras das faixas de tempo de votação.
- **Card de Flagrantes `CHK121`:** Total de ocorrências de digital de mesário em eleitores.
- **Card de Concentração `CHK124`:** Urnas com mesário hiper-concentrador de liberações.

### 5.2 Aba de Telemetria no Modal de Inspeção (`detailsModal`)
No modal da seção:
- Velocímetro / indicador de tempo médio de cabine com alerta em vermelho para seções com esteira (< 10s).
- Tabela de Mesários com identificador e contagem de liberações manuais.
- Alerta visual com caixa em vermelho caso haja flagrante de digital de mesário (`CHK121`).

---

## 6. Plano de Testes Automatizados

1. **Teste Unitário do Parser de Log:** Testar extração de tempos de cabine com timestamps sintéticos e cálculo de $\Delta T$.
2. **Teste dos Detectores `CHK121` a `CHK124`:** Validar que `CHK121` dispara na presença da mensagem de mesário em eleitores, `CHK122` na sequência de sub-10s, `CHK123` no surto de almoço e `CHK124` na concentração > 80%.
3. **Teste de Integração de Performance:** Garantir que o processamento em lote dos logs não trave a suíte e execute com estabilidade em 32 threads.
