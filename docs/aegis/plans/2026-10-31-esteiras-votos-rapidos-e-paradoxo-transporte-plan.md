# Plano de Implementação • A Física dos Intervalos (3s a 10s), Biometria, Rajadas e o Paradoxo do Transporte

**Data:** 31 de Outubro de 2026  
**Autor:** Dilnei Soethe Spancerski  
**Spec de Referência:** `docs/superpowers/specs/2026-10-31-esteiras-votos-rapidos-e-paradoxo-transporte-design.md`  
**Arquivos de Destino:** `apresentacao_slides.html` e `comparison_nacional_brasil/apresentacao_slides.html`

---

## 1. Contexto e Objetivos

Este plano define as etapas de implementação para adicionar **dois novos capítulos/slides investigativos** na apresentação oficial de slides:
1. **Slide A (A Física dos Intervalos 3s a 10s, Decomposição Biométrica e Rajadas):**
   - Volume de votos computados em 3s, 4s, 5s, 6s, 7s, 8s, 9s e 10s de intervalo;
   - Proporção de votos com e sem biometria em cada patamar temporal e a taxa percentual sem biometria;
   - Volume atribuível ao 13 vs 22 e a contagem de rajadas sequenciais ininterruptas;
   - Comparativo com a urna de controle científico de Braço do Norte / SC (Zona 44, Seção 144), onde o menor intervalo foi de 25s e a média de 96,7s.
2. **Slide B (O Paradoxo do Transporte e o Salto de Comparecimento: 2026 vs 2018):**
   - Análise das cidades com retenção de frotas e colapso de transporte que registraram aumento atípico de eleitores no 2º turno;
   - Confronto histórico direto com 2018 nas mesmas cidades (onde o comparecimento caiu normalmente);
   - A conexão causal com as esteiras de mesa no horário de almoço.

---

## 2. TDD Route Guard

```text
TDD Route:
- Mode: off
- Decision: skipped
- Strict authority: not applicable
- Test posture: post-change regression
- Reason: O projeto utiliza pipelines analíticos em Python e geração determinística de apresentações HTML/JS autônomas com testes de regressão no pytest e validação de sintaxe no Node.js.
- Verification: pytest e node --check
```

---

## 3. Arquitetura e Mapeamento de Arquivos

### Arquivos Criados:
- `scripts/extract_fast_votes_and_transport.py`: Script analítico de extração de telemetria dos zips em `D:\urnas2026`, processando intervalos de 3s a 10s, biometria e dados de transporte.
- `data/fast_votes_and_transport_summary.json`: Arquivo JSON consolidado com os números exatos e séries históricas para injeção nos slides.

### Arquivos Modificados:
- `apresentacao_slides.html`: Inserção dos 2 novos slides e reindexação para 27 capítulos no array `const SLIDES`.
- `comparison_nacional_brasil/apresentacao_slides.html`: Cópia espelho perfeitamente sincronizada (mesmo hash SHA-256).
- `README.md`: Atualização da contagem e descrição dos capítulos da apresentação.

---

## 4. Tarefas de Implementação

### Tarefa 1: Script de Extração de Intervalos e Biometria em `D:\urnas2026`
- **Arquivo:** `scripts/extract_fast_votes_and_transport.py`
- **Ação:**
  - Ler os pacotes `.zip` de `D:\urnas2026`;
  - Extrair os timestamps dos eventos `Eleitor foi habilitado` e `O voto do eleitor foi computado`;
  - Calcular os intervalos de 3s a 10s e quantificar votos `COM_BIOMETRIA` vs `SEM_BIOMETRIA`;
  - Extrair os dados da seção de controle de Braço do Norte / SC (Zona 44, Seção 144) em `SC_2t.zip`;
  - Extrair dados das cidades de transporte (Salvador, etc.) em 2026 e confrontar com 2018;
  - Gravar `data/fast_votes_and_transport_summary.json`.
- **Verificação:** Executar `python scripts/extract_fast_votes_and_transport.py` e inspecionar a saída gerada.

### Tarefa 2: Construção e Estilização do Slide A
- **Arquivo:** `apresentacao_slides.html`
- **Ação:**
  - Criar o objeto de dados do Slide A com título, subtítulo, tag, tempo estimado e roteiro de fala completo no teleprompter;
  - Desenvolver o HTML/SVG dos gráficos:
    1. Histograma de barras empilhadas para 3s, 4s, 5s, 6s, 7s, 8s, 9s, 10s com fração biométrica e etiqueta de `% Sem Biometria`;
    2. Curva comparativa de densidade: Esteiras anômalas vs Braço do Norte / SC;
    3. Painel de rajadas sequenciais e divisão 13 vs 22.
- **Verificação:** Renderizar o slide no navegador headless e conferir visualização.

### Tarefa 3: Construção e Estilização do Slide B
- **Arquivo:** `apresentacao_slides.html`
- **Ação:**
  - Criar o objeto de dados do Slide B com título, subtítulo, tag, tempo estimado e roteiro de fala completo no teleprompter;
  - Desenvolver o HTML/SVG dos gráficos:
    1. Tabela e gráfico de barras comparativo de cidades-chave (2018 queda vs 2026 aumento);
    2. Painel explicativo da conexão pericial (transporte retido $\rightarrow$ salas vazias $\rightarrow$ esteiras de 4s $\rightarrow$ alerta CHK125);
- **Verificação:** Renderizar o slide no navegador headless e conferir visualização.

### Tarefa 4: Reindexação dos Slides e Sincronização Espelho
- **Arquivos:** `apresentacao_slides.html` e `comparison_nacional_brasil/apresentacao_slides.html`
- **Ação:**
  - Reindexar todos os slides de 1 a 27 garantindo sequência contínua;
  - Copiar para `comparison_nacional_brasil/apresentacao_slides.html`;
  - Validar equivalência de hash SHA-256.
- **Verificação:** Script Python de hash check conferindo igualdade estrita.

### Tarefa 5: Validação de Sintaxe, QA Visual Headless e Testes
- **Ação:**
  - Validar JavaScript com `node --check`;
  - Capturar screenshots em 1568x861, 1920x1080 (Modo Telão) e 1568x576 (baixa altura);
  - Executar suíte de testes automatizados com `pytest`.
- **Verificação:** 100% dos testes aprovados e 0 erros de sintaxe.
