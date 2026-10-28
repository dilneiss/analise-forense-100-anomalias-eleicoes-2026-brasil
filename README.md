# Ferramenta Forense de Auditoria da Urna Eletrônica (TSE)

[![Python 3.11+](https://img.shields.io/badge/python-3.11%20%7C%203.12-blue.svg)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/tests-59%20passed-success.svg)](tests/)
[![Security: Read-Only](https://img.shields.io/badge/custodia-read--only%20imutavel-emerald.svg)](#1-princípios-de-segurança-e-custódia-forense)
[![Auditoria: 1T vs 2T](https://img.shields.io/badge/auditoria-1T%20vs%202T%20(100%20regras)-purple.svg)](#5-auditoria-comparativa-de-inconsistências-1º-vs-2º-turno)
[![Offline & Zero CDN](https://img.shields.io/badge/relatorios-100%25%20offline-orange.svg)](#6-relatórios-gerados-e-painel-interativo)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Suíte forense de alta performance para auditoria técnica, decodificação ASN.1 em baixo nível, conferência criptográfica e análise comparativa de integridade entre turnos eleitorais (1º vs 2º Turno) dos arquivos oficiais gerados pelas urnas eletrônicas brasileiras do Tribunal Superior Eleitoral (TSE).

Projetada com rigor científico, matemático e neutralidade pericial, em estrita conformidade com a norma **ISO/IEC 27037 (Diretrizes para identificação, coleta, aquisição e preservação de evidência digital)** e com a garantia irrevogável do **sigilo constitucional do voto**.

---

## Sumário

1. [Princípios de Segurança e Custódia Forense](#1-princípios-de-segurança-e-custódia-forense)
2. [Arquivos Oficiais Auditados e Estrutura Técnica](#2-arquivos-oficiais-auditados-e-estrutura-técnica)
3. [Requisitos e Instalação](#3-requisitos-e-instalação)
4. [Como Usar (Comandos em Linha Única)](#4-como-usar-comandos-em-linha-única)
   - [4.1 Auditoria Completa de uma Urna Específica](#41-auditoria-completa-de-uma-urna-específica)
   - [4.2 Modo Rápido (`--fast`) em Menos de 1 Segundo](#42-modo-rápido---fast-em-menos-de-1-segundo)
   - [4.3 Listagem e Diagnóstico de Arquivos](#43-listagem-e-diagnóstico-de-arquivos)
   - [4.4 Totalização Geral do Estado (`--all`)](#44-totalização-geral-do-estado---all)
5. [Auditoria Comparativa 1º vs 2º Turno (100 Regras Forenses)](#5-auditoria-comparativa-1º-vs-2º-turno-100-regras-forenses)
   - [5.1 Como Executar a Comparação](#51-como-executar-a-comparação)
   - [5.2 Vetores de Ataque, Fraude e Formas de Burlar Mapeadas](#52-vetores-de-ataque-fraude-e-formas-de-burlar-mapeadas)
   - [5.3 Catálogo das 100 Regras Automatizadas de Inconsistência](#53-catálogo-das-100-regras-automatizadas-de-inconsistência)
   - [5.4 Resultados Reais Auditados (17.326 seções de SC)](#54-resultados-reais-auditados-17326-seções-de-sc)
6. [Relatórios Gerados e Painel Interativo](#6-relatórios-gerados-e-painel-interativo)
7. [Vocabulário Controlado de Auditoria](#7-vocabulário-controlado-de-auditoria)
8. [Testes Automatizados](#8-testes-automatizados)

---

## 1. Princípios de Segurança e Custódia Forense

- **Modo Estritamente Somente Leitura:** Os arquivos de evidência oficial nunca são abertos com permissão de escrita e jamais sofrem qualquer modificação (`open(path, 'rb')`).
- **Análise Não Destrutiva:** Nenhuma descompactação ou escrita temporária ocorre dentro do diretório de entrada. Todas as saídas são gravadas em pasta isolada de análise (`analysis/`, `comparison_analysis/`, etc.).
- **Conferência Pré e Pós-Execução (Integridade Provada):**
  1. Todos os arquivos são inventariados e recebem hashes **SHA-256** e **SHA-512** gravados em `manifest.json`.
  2. Ao final da análise, os hashes dos arquivos originais são recalculados para provar matematicamente que nenhum byte da evidência foi violado durante a auditoria (`post_run_verification.ok = true`).
- **Preservação do Sigilo do Voto:** O Registro Digital do Voto (RDV) é processado exclusivamente para conferência quantitativa e integridade de apuração cruzada com o Boletim de Urna (BU). A ferramenta **não** exporta nem correlaciona votantes individuais.
- **Neutralidade Científica:** Os detectores aplicam regras técnicas e lógicas objetivas. Não são feitas suposições inferenciais sem embasamento matemático ou documental.

---

## 2. Arquivos Oficiais Auditados e Estrutura Técnica

A ferramenta processa o conjunto oficial de arquivos distribuídos pelo TSE, identificados pela nomenclatura padrão `o<pleito_5d><uf_2><municipio_5d><zona_4d><secao_4d>-<tipo>.<ext>`:

| Arquivo | Formato / Especificação | Função Pericial no Processo de Auditoria |
|---|---|---|
| `-bu.dat` | **ASN.1 DER v2** (`EntidadeEnvelopeGenerico` + `EntidadeBoletimUrna`) | Boletim de Urna com eleitores aptos (seção e TTE), comparecimento, detalhamento de biometria, votos por candidato e cadeia de hashes SHA-512 recursiva. |
| `-rdv.dat` | **ASN.1 BER** (`EntidadeResultadoRDV`) | Registro Digital do Voto com tabelas desidentificadas para conferência aritmética exata e cruzamento com o BU. |
| `-log.jez` | **Container ZIP Deflate** contendo `logd.dat` | Log operacional completo da urna (TSV em Latin-1 com data/hora precisa, severidade, módulo interno, ID da urna, mensagem do evento e MAC de 64 bits). |
| `-vota.vsc` | **Envelope Criptográfico** ASN.1 | Assinatura digital de software (CEPESC), hardware (Ed521/ECDSA), lista de hashes SHA-512 de todos os arquivos gerados e certificado digital X.509 da urna. |
| `-imgbu.dat` | **Spool de Impressão Térmica** (ESC/P Latin-1) | Espelho binário/textual exato do Boletim de Urna físico impresso na seção às 17h, lido sem dependência de OCR. |

---

## 3. Requisitos e Instalação

### Requisitos
- **Python 3.11 ou 3.12+**
- Sistemas Operacionais suportados: **Windows 10/11**, **Linux (Ubuntu/Debian/RHEL/CentOS)** ou **macOS**
- Espaço em disco compatível com a base oficial do TSE

### Instalação

```bash
git clone https://github.com/dilneiss/urna-forense.git
cd urna-forense
python -m venv .venv
```

Ative o ambiente virtual:
- No Linux/macOS: `source .venv/bin/activate`
- No Windows: `.venv\Scripts\activate`

Instale as dependências:
```bash
pip install -r requirements.txt
```

---

## 4. Como Usar (Comandos em Linha Única)

*Todos os comandos abaixo estão formatados em uma única linha contínua, permitindo cópia e execução direta sem quebra de linha.*

### 4.1 Auditoria Completa de uma Urna Específica

Para auditar detalhadamente uma urna (timeline milissegundo a milissegundo, conferência cruzada BU ↔ RDV ↔ LOG ↔ Spool e cadeia de hashes):

```bash
python analyzer.py --input "C:/dados/bu_imgbu_logjez_rdv_vscmr_2026_1t_SC" --output "analysis_secao" --uf SC --municipio 80535 --zona 44 --secao 144 --turno 1 --data-eleicao 2026-10-04 --municipios-csv data/municipio_tse_ibge.csv
```

### 4.2 Modo Rápido (`--fast`) em Menos de 1 Segundo

Localiza diretamente a urna na pasta com mais de 80.000 arquivos sem precisar ler o diretório inteiro:

```bash
python analyzer.py --input "C:/dados/bu_imgbu_logjez_rdv_vscmr_2026_1t_SC" --output "analysis_rapida" --uf SC --municipio 80535 --zona 44 --secao 144 --fast
```

### 4.3 Listagem e Diagnóstico de Arquivos

Para listar as urnas disponíveis e inspecionar a presença dos 5 arquivos essenciais:

```bash
python analyzer.py --input "C:/dados/pasta_eleicoes" --list --limit 30
```

### 4.4 Totalização Geral do Estado (`--all`)

Processa todos os Boletins de Urna de uma UF completa concorrentemente em segundos:

```bash
python analyzer.py --input "C:/dados/bu_imgbu_logjez_rdv_vscmr_2026_1t_SC" --output "analysis_geral" --all --hash-scope target --municipios-csv data/municipio_tse_ibge.csv
```

---

## 5. Auditoria Comparativa 1º vs 2º Turno (100 Regras Forenses)

O motor comparativo confronta par a par todas as seções eleitorais entre o 1º e o 2º Turno, analisando eleitorado, biometria, fluxo de votação, dinâmica presidencial e integridade criptográfica.

### 5.1 Como Executar a Comparação

#### Comparando um Estado Inteiro (Ex.: Todas as 17.326 seções de SC):
```bash
python analyzer.py --compare-1t "C:\Users\dilne\Downloads\bu_imgbu_logjez_rdv_vscmr_2026_1t_SC" --compare-2t "C:\Users\dilne\Downloads\bu_imgbu_logjez_rdv_vscmr_2026_2t_SC" --output "comparison_sc_geral" --municipios-csv data/municipio_tse_ibge.csv --max-workers 32
```

#### Comparando Apenas um Município:
```bash
python analyzer.py --compare-1t "C:\Users\dilne\Downloads\bu_imgbu_logjez_rdv_vscmr_2026_1t_SC" --compare-2t "C:\Users\dilne\Downloads\bu_imgbu_logjez_rdv_vscmr_2026_2t_SC" --municipio 80004 --output "comparison_monte_carlo" --municipios-csv data/municipio_tse_ibge.csv
```

#### Comparando Apenas uma Seção Específica:
```bash
python analyzer.py --compare-1t "C:\Users\dilne\Downloads\bu_imgbu_logjez_rdv_vscmr_2026_1t_SC" --compare-2t "C:\Users\dilne\Downloads\bu_imgbu_logjez_rdv_vscmr_2026_2t_SC" --uf SC --municipio 80535 --zona 44 --secao 144 --output "comparison_secao_144"
```

---

### 5.2 Vetores de Ataque, Fraude e Formas de Burlar Mapeadas

Para estruturar as 100 regras de detecção, a ferramenta modela os principais vetores de vulnerabilidade física, lógica, procedimental e matemática do sistema eleitoral:

1. **Enchimento de Urna (*Ballot Stuffing*) e Voto Fantasma:**
   - *Mecanismo:* Inserção de votos após as 17h para eleitores faltosos (abstenção convertida em votos artificiais).
   - *Detecção:* Salto anômalo de comparecimento no 2T (`CHK036`), tempo médio por voto humanamente impossível (`CHK083`), encerramentos tardios após 20h (`CHK079`, `CHK080`) e correlação com salto de habilitação manual biográfica (`CHK075`).
2. **Substituição e Troca Não Autorizada de Urnas / Cargas:**
   - *Mecanismo:* Troca de urna física ou flash de votação por equipamento de contingência não auditado.
   - *Detecção:* `CHK001` (troca de urna), `CHK002` (troca de FV), `CHK003` (troca de FC), `CHK004` (modelo divergente), `CHK012` (serial TPM divergente) e `CHK014` (carga em outro município).
3. **Bypass e Burlar Leitor Biométrico:**
   - *Mecanismo:* Mesário libera eleitores sem presença física digitando o ano de nascimento repetidas vezes.
   - *Detecção:* `CHK066` e `CHK067` (queda abrupta de validação biométrica), `CHK068` e `CHK069` (surto de liberação por ano de nascimento) e `CHK070` (seção com biometria no 1T zerando no 2T).
4. **Manipulação e Desvio de Votos de Terceira Via:**
   - *Mecanismo:* Desvio direcionado de votos de candidatos não finalistas (Renan Santos, Cury, Caiado) integralmente para um único concorrente.
   - *Detecção:* `CHK053` (absorção de 100% da 3ª via por um só candidato), `CHK054` (crescimento excedendo o teto matemático disponível) e `CHK055` (crescimento com comparecimento caindo além do estoque da 3ª via).
5. **Queda Anômala de Votos de Finalistas:**
   - *Mecanismo:* Redução forçada de votos nominais de um candidato finalista em relação à sua própria base do 1º turno.
   - *Detecção:* `CHK046` (queda de votos de finalista mesmo quando o comparecimento total à seção aumentou), `CHK047` (queda com comparecimento igual), `CHK048` (queda desproporcional à redução de votantes) e `CHK050` (desaparecimento total de votos).
6. **Violação do Caderno Eleitoral Congelado:**
   - *Mecanismo:* Adição ou supressão arbitrária de eleitores originais da seção após o fechamento do cadastro.
   - *Detecção:* `CHK016`, `CHK017` e `CHK018` (variação de `aptos_secao`), `CHK019` e `CHK020` (picos anômalos de transferência temporária TTE).
7. **Manipulação de Votos Brancos e Nulos:**
   - *Mecanismo:* Conversão forçada de votos nominais em brancos/nulos ou vice-versa.
   - *Detecção:* `CHK086` e `CHK087` (explosão de brancos/nulos acima de 30%), `CHK088` (extinção total de brancos/nulos em seção grande) e `CHK092` (100% de votos inválidos).
8. **Violações Criptográficas e Hashes:**
   - *Mecanismo:* Modificação de dados gravados no BU quebrando a integridade de assinatura.
   - *Detecção:* `CHK093` e `CHK094` (soma divergente do comparecimento), `CHK098` e `CHK099` (quebra da cadeia recursiva SHA-512 do BU) e `CHK100` (divergência com o envelope `vota.vsc`).

---

### 5.3 Catálogo das 100 Regras Automatizadas de Inconsistência

#### Grupo 1: Hardware, Equipamento, Carga e Mídia (`HARDWARE_E_CARGA` - 15 Regras)
- `CHK001_TROCA_URNA_FISICA` (MÉDIA): Número interno da urna alterado entre turnos.
- `CHK002_TROCA_FLASH_VOTACAO` (MÉDIA): Serial da Flash de Votação (FV) alterado no 2T.
- `CHK003_TROCA_FLASH_CARGA` (MÉDIA): Serial da Flash de Carga (FC) alterado no 2T.
- `CHK004_MODELO_URNA_DIVERGENTE` (ALTA): Modelo de urna divergente entre turnos (ex: UE2020 vs UE2015).
- `CHK005_VERSAO_SOFTWARE_ALTERADA` (ALTA): Versão do binário oficial de votação alterada.
- `CHK006_MUDANCA_LOCAL_VOTACAO` (BAIXA): Local físico de votação remanejado entre turnos.
- `CHK007_CODIGO_CARGA_ALTERADO` (BAIXA): Código de carga recarregado na mesma urna física.
- `CHK008_DATA_CARGA_ANOMALA_2T` (MÉDIA): Data de carga do 2T anterior à data da eleição do 1T.
- `CHK009_DATA_CARGA_TARDIA_2T` (MÉDIA): Urna carregada no próprio dia da votação do 2T após 07:00.
- `CHK010_CORRESPONDENCIA_INVALIDA_2T` (ALTA): Identificação de seção na correspondência diverge da identificação do BU.
- `CHK011_GERADOR_MIDIA_DIVERGENTE` (BAIXA): Nome da estação geradora de mídia difere entre turnos.
- `CHK012_TPM_SERIAL_DIVERGENTE` (ALTA): Serial do chip de segurança TPM alterado na mesma urna física declarada.
- `CHK013_SERIAL_INSTALACAO_REINICIADO` (MÉDIA): Serial de instalação da urna recuou para valor inferior no 2T.
- `CHK014_CARGA_URNA_EM_OUTRO_MUNICIPIO` (ALTA): Município da correspondência diverge do município da seção.
- `CHK015_TIPO_ARQUIVO_NAO_VOTACAO_UE` (ALTA): Tipo de arquivo do BU não é de votação oficial de urna (1).

#### Grupo 2: Cadastro, Eleitorado e Aptos (`CADASTRO_E_ELEITORADO` - 15 Regras)
- `CHK016_VARIACAO_APTOS_SECAO` (ALTA): Variação de eleitores originais (`aptos_secao` 1T != 2T).
- `CHK017_REDUCAO_APTOS_SECAO` (ALTA): Número de eleitores originais diminuiu no 2T.
- `CHK018_AUMENTO_APTOS_SECAO` (ALTA): Número de eleitores originais aumentou no 2T.
- `CHK019_PICO_TTE_ABSOLUTO` (MÉDIA): Variação de eleitores em trânsito (TTE) superior a 20 eleitores.
- `CHK020_PICO_TTE_PERCENTUAL` (MÉDIA): Variação de TTE superior a 10% do total de aptos da seção.
- `CHK021_EXTINCAO_TTE_2T` (BAIXA): Seção com mais de 15 TTEs no 1T zera completamente no 2T.
- `CHK022_SURGIMENTO_TTE_MASSIVO_2T` (MÉDIA): Seção sem TTE no 1T recebe mais de 25 temporários no 2T.
- `CHK023_APTOS_TOTAL_DIVERGENTE_SOMA` (ALTA): `aptos_total != aptos_secao + aptos_tte` no BU.
- `CHK024_SECAO_MINIMA_ANOMALA` (BAIXA): Seção ativa com menos de 15 eleitores aptos.
- `CHK025_SECAO_HIPERTROFICA` (BAIXA): Seção eleitoral com mais de 500 aptos.
- `CHK026_SECAO_SEM_APTOS` (ALTA): Boletim de Urna gerado com zero eleitores aptos registrados.
- `CHK027_OSCILACAO_APTOS_TOTAL_MAIOR_10PCT` (ALTA): Eleitorado total da seção oscilou mais de 10% entre turnos.
- `CHK028_DIVERGENCIA_APTOS_ENTRE_ELEICOES` (ALTA): Total de aptos divergiu sem alteração nas parcelas secao/tte.
- `CHK029_TRANSFERENCIA_TEMPORARIA_SUPERIOR_A_50PCT` (ALTA): Mais da metade dos eleitores da seção são temporários.
- `CHK030_ZONA_SECAO_FORA_PADRAO_CADASTRO` (BAIXA): Seção com numeração atípica (> 3000).

#### Grupo 3: Comparecimento e Abstenção (`COMPARECIMENTO_E_ABSTENCAO` - 15 Regras)
- `CHK031_COMPARECIMENTO_EXCEDE_APTOS_2T` (ALTA): Comparecimento no 2T superior ao total de eleitores aptos.
- `CHK032_COMPARECIMENTO_EXCEDE_APTOS_1T` (ALTA): Comparecimento no 1T superior ao total de eleitores aptos.
- `CHK033_COMPARECIMENTO_100_PCT_2T` (MÉDIA): Comparecimento integral de 100% (zero abstenção) em seção com $\ge 50$ eleitores.
- `CHK034_ABSTENCAO_SUPERIOR_50PCT_2T` (MÉDIA): Abstenção superior a 50% no 2T em seção com $\ge 50$ eleitores.
- `CHK035_ABSTENCAO_SUPERIOR_70PCT_2T` (ALTA): Abstenção crítica superior a 70% no 2T.
- `CHK036_SALTO_COMPARECIMENTO_MAIOR_25PP` (ALTA): Presença no 2T subiu mais de 25 pp em relação ao 1T.
- `CHK037_QUEDA_COMPARECIMENTO_MAIOR_25PP` (ALTA): Presença no 2T caiu mais de 25 pp em relação ao 1T.
- `CHK038_COMPARECIMENTO_IDENTICO_COM_APTOS_DIFERENTES` (ALTA): Comparecimento exatamente igual ao 1T mesmo com eleitorado alterado.
- `CHK039_COMPARECIMENTO_ZERO_2T` (ALTA): Zero comparecimento em seção com aptos regulares.
- `CHK040_COMPARECIMENTO_UNITARIO_2T` (ALTA): Apenas 1 eleitor compareceu no 2T em seção com $>50$ aptos.
- `CHK041_ABSTENCAO_ZERO_AMBOS_TURNOS` (MÉDIA): Zero abstenção registrada no 1T e no 2T.
- `CHK042_QUEDA_COMPARECIMENTO_MAIOR_30PCT` (MÉDIA): Comparecimento absoluto caiu mais de 30% no 2T.
- `CHK043_EXPLOSAO_COMPARECIMENTO_MAIOR_40PCT` (MÉDIA): Comparecimento absoluto subiu mais de 40% no 2T.
- `CHK044_COMPARECIMENTO_DISCREPANTE_DO_MUNICIPIO` (ALTA): Variação de presença da seção desvia mais de 20 pp da média municipal.
- `CHK045_COMPARECIMENTO_PRESIDENCIAL_MENOR_QUE_CARGO_ESTADUAL` (ALTA): Votos apurados para presidente menores que o comparecimento.

#### Grupo 4: Votação Presidencial e Terceira Via (`VOTACAO_E_MIGRACAO_TERCEIRA_VIA` - 20 Regras)
*(Nota metodológica: Votação zero no 2T para candidatos de 3ª via NUNCA é tratada como anomalia, pois eles não concorrem no 2T. O foco pericial é exclusivamente o comportamento dos finalistas 22 e 13 e o fluxo migratório da 3ª via).*
- `CHK046_QUEDA_FINALISTA_COM_COMPARECIMENTO_MAIOR` (ALTA): Candidato finalista tem menos votos no 2T com comparecimento MAIOR na seção ($C_{2T} > C_{1T}$ e $V_{2T} < V_{1T}$).
- `CHK047_QUEDA_FINALISTA_COM_COMPARECIMENTO_IGUAL` (ALTA): Candidato finalista perde votos nominais no 2T com comparecimento exatamente igual ($C_{2T} = C_{1T}$ e $V_{2T} < V_{1T}$).
- `CHK048_QUEDA_DESPROPORCIONAL_AO_COMPARECIMENTO` (ALTA): Comparecimento caiu $X\%$, mas o candidato perdeu $> 2.5 \times X\%$ dos seus votos no 2T.
- `CHK049_PERDA_BRUSCA_MAIOR_30PCT_FINALISTA` (MÉDIA): Finalista perde mais de 30% dos votos com presença estável ($\pm 5\%$).
- `CHK050_DESAPARECIMENTO_FINALISTA_NO_2T` (ALTA): Finalista tinha $\ge 15$ votos no 1T e zera (0 votos) no 2T.
- `CHK051_ZERO_VOTOS_FINALISTA_SECAO_GRANDE` (MÉDIA): Finalista recebe 0 votos em seção com $>50$ votos válidos no 2T.
- `CHK052_UNANIMIDADE_100PCT_FINALISTA_2T` (MÉDIA): 100% dos votos válidos para um único finalista no 2T em seção com $\ge 50$ votos válidos.
- `CHK053_ABSORCAO_100PCT_TERCEIRA_VIA_POR_UM_CANDIDATO` (MÉDIA): Mais de 95% do saldo líquido da 3ª via migrou exclusivamente para um único candidato, com o outro tendo migração $\le 0$.
- `CHK054_CRESCIMENTO_EXCEDE_TETO_MIGRACAO_E_COMPARECIMENTO` (ALTA): Ganho do candidato supera todo o estoque de 3ª via 1T + brancos 1T + nulos 1T + novos eleitores no 2T.
- `CHK055_CRESCIMENTO_COM_QUEDA_DE_COMPARECIMENTO_ACIMA_DA_TERCEIRA_VIA` (ALTA): Comparecimento caiu, mas o candidato cresceu além do total existente de votos de terceira via no 1T.
- `CHK056_INVERSAO_ABRUPTA_SWING_MAIOR_50PP` (ALTA): Inversão política radical entre turnos com swing líquido $> 50$ pp.
- `CHK057_INVERSAO_ABRUPTA_SWING_MAIOR_40PP` (MÉDIA): Swing líquido superior a 40 pp entre os finalistas.
- `CHK058_MIGRACAO_TOTALMENTE_ASSIMETRICA_CONTRA_MEDIA_MUNICIPAL` (ALTA): A seção divergiu em mais de 40 votos do padrão médio de crescimento do candidato no município.
- `CHK059_VOTO_CANDIDATO_NAO_CONCORRENTE_NO_2T` (ALTA): Votos nominais registrados para candidatos que não concorriam no 2T.
- `CHK060_FINALISTA_COM_VOTACAO_MENOR_QUE_BRANCOS_E_NULOS` (MÉDIA): Finalista tem menos votos nominais que a soma de brancos e nulos em seção com $>100$ eleitores.
- `CHK061_VOTOS_VALIDOS_ZERO_NO_2T` (ALTA): Zero votos válidos para presidente em seção com comparecimento ativo.
- `CHK062_DESVIO_PADRAO_VOTOS_EXTREMO_NO_MUNICIPIO` (MÉDIA): Percentual de votos do candidato desvia mais de 3.5 desvios-padrão da média municipal.
- `CHK063_AMBOS_FINALISTAS_PERDERAM_VOTOS_COM_MAIOR_COMPARECIMENTO` (ALTA): Comparecimento aumentou, mas ambos os finalistas tiveram redução de votos nominais.
- `CHK064_CONCENTRACAO_DE_VOTOS_SUPERIOR_A_95PCT` (MÉDIA): Candidato finalista atinge mais de 95% dos votos válidos no 2T em seção grande.
- `CHK065_VOTOS_NOMINAIS_SUPERIORES_AO_COMPARECIMENTO` (ALTA): Soma dos votos nominais ultrapassa o comparecimento declarado no BU.

#### Grupo 5: Biometria e Habilitação do Eleitor (`BIOMETRIA_E_HABILITACAO` - 10 Regras)
- `CHK066_QUEDA_ABRUPTA_BIOMETRIA_MAIOR_30PP` (ALTA): Taxa de validação biométrica caiu mais de 30 pp entre 1T e 2T.
- `CHK067_QUEDA_ABRUPTA_BIOMETRIA_MAIOR_20PP` (MÉDIA): Taxa de biometria caiu mais de 20 pp entre 1T e 2T.
- `CHK068_SURTO_HABILITACAO_BIOGRAFICA_MAIOR_25PP` (ALTA): Habilitação manual por ano de nascimento subiu mais de 25 pp no 2T.
- `CHK069_SURTO_HABILITACAO_BIOGRAFICA_MAIOR_15PP` (MÉDIA): Habilitação manual por ano de nascimento subiu mais de 15 pp no 2T.
- `CHK070_ZERO_BIOMETRIA_EM_SECAO_BIOMETRIZADA` (MÉDIA): Zero validações biométricas no 2T em seção com $>60\%$ no 1T (leitor desligado).
- `CHK071_EXPLOSAO_SEM_BIOMETRIA_MAIOR_30PP` (MÉDIA): Eleitores sem biometria aumentaram mais de 30 pp no 2T.
- `CHK072_SOMA_DETALHAMENTO_COMPARECIMENTO_DIVERGENTE` (ALTA): `biometria + biografia + sem_biometria != comparecimento`.
- `CHK073_BIOMETRIA_100PCT_COM_HABILITACAO_MANUAL_ZERO` (INFO): 100% de biometria sem nenhuma verificação manual em seção grande.
- `CHK074_BIOMETRIA_SUPERIOR_AOS_APTOS` (ALTA): Habilitações biométricas superam os eleitores aptos da seção.
- `CHK075_CORRELACAO_BIOGRAFICA_E_VOTO_UNANIME` (ALTA): Salto em liberações manuais por ano de nascimento acompanhado de votação $>90\%$ para um candidato.

#### Grupo 6: Tempo e Ritmo de Votação (`TEMPO_E_COMPORTAMENTO` - 10 Regras)
- `CHK076_ABERTURA_PRECOCE_2T` (MÉDIA): Votação iniciada antes das 07:00 no 2T.
- `CHK077_ABERTURA_TARDIA_2T` (MÉDIA): Votação iniciada após as 08:30 no 2T.
- `CHK078_ENCERRAMENTO_PRECOCE_2T` (ALTA): Votação encerrada antes das 17:00 no 2T.
- `CHK079_ENCERRAMENTO_MUITO_TARDIO_2T` (MÉDIA): Votação encerrada após as 20:00 no 2T.
- `CHK080_ENCERRAMENTO_MADRUGADA_2T` (ALTA): Votação encerrada após as 22:00 no 2T.
- `CHK081_DURACAO_VOTACAO_INFERIOR_A_4_HORAS` (ALTA): Seção encerrou com menos de 4 horas de funcionamento e eleitores faltosos.
- `CHK082_DURACAO_2T_SUPERIOR_AO_1T_EM_MAIS_DE_60MIN` (BAIXA): Votação no 2T demorou $>60$ min além do 1T (mesmo votando em 1 só cargo).
- `CHK083_TEMPO_MEDIO_POR_VOTO_IMPOSSIVEL_INFERIOR_15S` (ALTA): Tempo médio por eleitor $< 15$ segundos (ritmo humanamente inviável).
- `CHK084_EMISSAO_BU_ANTERIOR_AO_ENCERRAMENTO` (ALTA): Data/hora de emissão do BU anterior ao encerramento oficial registrado.
- `CHK085_HORARIO_ABERTURA_DIVERGENTE_MAIOR_60MIN` (BAIXA): Abertura no 2T diferiu em mais de 60 minutos do horário do 1T.

#### Grupo 7: Votos Brancos e Nulos (`BRANCOS_E_NULOS` - 7 Regras)
- `CHK086_EXPLOSAO_BRANCOS_NULOS_MAIOR_15PP` (MÉDIA): Proporção de brancos e nulos saltou mais de 15 pp em relação ao 1T.
- `CHK087_BRANCOS_NULOS_SUPERIOR_A_30PCT` (ALTA): Brancos e nulos superam 30% dos votos totais apurados no 2T.
- `CHK088_EXTINCAO_BRANCOS_NULOS_SECAO_GRANDE` (BAIXA): Zero brancos e zero nulos no 2T em seção com $>150$ votantes.
- `CHK089_QUEDA_BRANCOS_NULOS_MAIOR_20PP` (MÉDIA): Brancos e nulos caíram mais de 20 pp no 2T.
- `CHK090_NULOS_SUPERIORES_A_BRANCOS_EM_10X` (MÉDIA): Votos nulos superam votos brancos em mais de 10 vezes em seção grande.
- `CHK091_BRANCOS_SUPERIORES_A_NULOS_EM_10X` (MÉDIA): Votos brancos superam votos nulos em mais de 10 vezes em seção grande.
- `CHK092_100PCT_VOTOS_INVALIDOS_NO_2T` (ALTA): 100% dos votos apurados na urna foram brancos ou nulos.

#### Grupo 8: Integridade Criptográfica e Pareamento (`INTEGRIDADE_E_PAREAMENTO` - 8 Regras)
- `CHK093_DIVERGENCIA_SOMA_VOTOS_E_COMPARECIMENTO_2T` (ALTA): Votos nominais + brancos + nulos != comparecimento registrado no BU do 2T.
- `CHK094_DIVERGENCIA_SOMA_VOTOS_E_COMPARECIMENTO_1T` (ALTA): Votos nominais + brancos + nulos != comparecimento registrado no BU do 1T.
- `CHK095_SECAO_DESEMPARELHADA_PRESENTE_APENAS_NO_1T` (MÉDIA): Seção presente no 1T mas sem correspondente no 2T.
- `CHK096_SECAO_DESEMPARELHADA_PRESENTE_APENAS_NO_2T` (MÉDIA): Seção presente no 2T mas sem correspondente no 1T.
- `CHK097_TOTAL_VOTOS_CARGO_NAO_E_MULTIPLO_COMPARECIMENTO` (ALTA): Total de votos apurados no cargo presidencial diverge do comparecimento.
- `CHK098_FALHA_CADEIA_HASH_SHA512_2T` (ALTA): Hash recursivo recalculado dos votáveis não confere com `ultimoHashVotosVotavel` no 2T.
- `CHK099_FALHA_CADEIA_HASH_SHA512_1T` (ALTA): Hash recursivo recalculado dos votáveis não confere com `ultimoHashVotosVotavel` no 1T.
- `CHK100_HASH_ASSINADO_VSC_DIVERGENTE` (ALTA): Hash SHA-512 do arquivo `bu.dat` diverge do hash assinado no envelope `vota.vsc`.

---

### 5.4 Resultados Reais Auditados (17.326 seções de SC)

Ao processar todas as seções de Santa Catarina (Eleições 2026), **34.652 Boletins de Urna oficiais foram decodificados e auditados em 129 segundos**:

```text
================================================================================
AUDITORIA FORENSE COMPARATIVA: 1º TURNO vs 2º TURNO (100 VERIFICAÇÕES TÉCNICAS)
================================================================================
Tempo de processamento: 129.06s | Seções analisadas: 17,326
Seções com alguma inconsistência: 2,438 (14.07%)
Total de ocorrências de anomalias: 4,626
--------------------------------------------------------------------------------
DISTRIBUIÇÃO POR SEVERIDADE:
  - ALTA (Crítica):    4,084
  - MÉDIA (Relevante): 470
  - BAIXA / INFO:      72
--------------------------------------------------------------------------------
AUDITORIA BIOMÉTRICA:
  - Com Biometria: 1T=4,058,005 (87.3%) │ 2T=4,152,006 (87.18%)
  - Sem Biometria: 1T=590,154 │ 2T=610,297
  - Terceira Via no 1T: 373,893 votos (8.31% dos válidos)
--------------------------------------------------------------------------------
PRINCIPAIS TIPOS DE INCONSISTÊNCIAS IDENTIFICADAS:
  • CHK016_VARIACAO_APTOS_SECAO                        :  1,743 seções
  • CHK018_AUMENTO_APTOS_SECAO                         :  1,110 seções
  • CHK017_REDUCAO_APTOS_SECAO                         :    633 seções
  • CHK046_QUEDA_FINALISTA_COM_COMPARECIMENTO_MAIOR    :    292 seções
  • CHK001_TROCA_URNA_FISICA                           :    189 seções
  • CHK003_TROCA_FLASH_CARGA                           :    115 seções
  • CHK004_MODELO_URNA_DIVERGENTE                      :    109 seções
  • CHK014_CARGA_URNA_EM_OUTRO_MUNICIPIO               :     90 seções
  • CHK002_TROCA_FLASH_VOTACAO                         :     61 seções
  • CHK088_EXTINCAO_BRANCOS_NULOS_SECAO_GRANDE         :     57 seções
  • CHK047_QUEDA_FINALISTA_COM_COMPARECIMENTO_IGUAL    :     44 seções
  • CHK062_DESVIO_PADRAO_VOTOS_EXTREMO_NO_MUNICIPIO    :     40 seções
--------------------------------------------------------------------------------
TOTALIZAÇÃO COMPARATIVA PRESIDENCIAL:
  FLAVIO BOLSONARO       │ 1T:  3,000,020 │ 2T:  3,220,071 │ Dif:  +220,051 (+7.33%)
  LULA                   │ 1T:  1,127,168 │ 2T:  1,418,314 │ Dif:  +291,146 (+25.83%)
  ESCRITOR AUGUSTO CURY  │ 1T:    134,273 │ 2T: [Não concorre] │ (3ª via 1T)
  RENAN SANTOS           │ 1T:    132,795 │ 2T: [Não concorre] │ (3ª via 1T)
  RONALDO CAIADO         │ 1T:     79,911 │ 2T: [Não concorre] │ (3ª via 1T)
  COMPARECIMENTO TOTAL   │ 1T:  4,648,159 │ 2T:  4,762,303 │ Dif:  +114,144 eleitores
================================================================================
```

---

## 6. Relatórios Gerados e Painel Interativo

A pasta de saída contém relatórios estruturados e visuais:

```text
comparison_sc_geral/
├── comparison_report.html  # Painel HTML responsivo, 100% offline, com busca e ordenação avançada
└── comparison_report.json  # Base de dados estruturada JSON de todas as seções (50 MB)
```

### Funcionalidades do Painel HTML (`comparison_report.html`)
- **Aptos por Seção:** Exibe `Aptos (1T -> 2T)` em coluna dedicada, destacando em amarelo seções com variação cadastral.
- **Auditoria Biométrica:** Colunas dedicadas para `Com Biometria` e `Sem Biometria` no 1T e 2T.
- **Terceira Via 1T:** Exibe o total de votos de terceira via que existiam na seção no 1º turno para análise de migração.
- **Ordenação Completa por Severidade:** Ordene com 1 clique de forma crescente ou decrescente pela coluna **Severidade** (`ALTA` &rarr; `MÉDIA` &rarr; `BAIXA` &rarr; `NORMAL`), por maior queda de Flávio, maior queda de Lula, maior variação de comparecimento ou por município.
- **Busca em Tempo Real:** Pesquise simultaneamente por nome da cidade, zona, seção ou código da anomalia.
- **100% Offline (Zero CDN):** Funciona sem conexão de internet, em conformidade com salas de situação seguras e ambientes isolados.

---

## 7. Vocabulário Controlado de Auditoria

Em estrita observância às normas forenses digitais, a ferramenta nunca emprega termos opinativos (como *"fraude"* ou *"adulteração presumida"*):

| Classificação Técnica | Critério Documental |
|---|---|
| **`VALIDADO`** | Verificação executada com sucesso e comprovada matematicamente ou por referência cruzada direta. |
| **`NÃO VALIDADO`** | Teste criptográfico formal executado com falha (ex.: assinatura inválida ou hash assinado divergente). |
| **`INCONSISTENTE`** | Fontes oficiais divergem entre si (ex.: BU difere do RDV, ou contagem de votos diverge do 1T). |
| **`NÃO FOI POSSÍVEL VERIFICAR`** | Chaves, certificados intermediários ou algoritmos proprietários não estão publicamente acessíveis. |
| **`SEM EVIDÊNCIA DE ALTERAÇÃO`** | Todos os hashes assinados e cadeias internas conferem integralmente byte a byte. |

---

## 8. Testes Automatizados

A suíte de testes unitários e de integração cobre todos os componentes da ferramenta:

```bash
pytest
```

Saída:
```text
============================== 59 passed in 1.35s ===============================
```

---

## Licença

Distribuído sob a licença **MIT**. Consulte `LICENSE` para mais detalhes.

*Este software é uma iniciativa de auditoria técnica independente, transparente e de código aberto destinada a pesquisadores, peritos e cidadãos comprometidos com a integridade democrática e a transparência pública dos dados eleitorais.*
