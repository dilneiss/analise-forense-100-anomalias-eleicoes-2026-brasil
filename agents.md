# AGENTS.md • Manual Operacional e Guia de Engenharia para Agentes de IA

Este documento é a **fonte primária e autoritativa de instruções técnicas, arquitetura de dados e políticas operacionais** para qualquer Agente de IA ou engenheiro que for operar, auditar, estender ou manter o repositório **`urna-forense`** (`analise-forense-100-anomalias-eleicoes-2026-brasil`).

---

## 1. Identidade e Missão do Projeto

### 1.1 O Que É Este Repositório?
Uma suíte forense de computação de alto desempenho desenvolvida em **Python 3.11+ puro**, voltada para:
1. **Decodificação de Baixo Nível:** Leitura em memória de arquivos brutos das urnas eletrônicas do Tribunal Superior Eleitoral (TSE) no formato **ASN.1 BER/DER**, containers compactados (`.logjez` em PKZip e 7z) e telemetria de votação (`logd.dat`).
2. **Auditoria Comparativa Nacional:** Cruzamento massivo de integridade de **100% das 499.178 seções eleitorais do Brasil** entre o 1º e o 2º Turno (998.356 BUs em 2026, 943.968 BUs em 2022 e 454.448 BUs de controle em 2018).
3. **Apresentação Executiva Interativa:** Central de inteligência em slides widescreen (`apresentacao_slides.html`) com 25 capítulos, teleprompter com roteiro falado, motor TTS ElevenLabs integrado com cache IndexedDB e mapa interativo do Brasil em SVG (`comparison_nacional_brasil/national_report.html`).

### 1.2 Princípios Não-Negociáveis
- **Honestidade Científica Absoluta:** Jamais inventar números, estatísticas ou estimativas. Todo dado exibido ou gerado deve ser extraído diretamente dos arquivos oficiais brutos do TSE ou deduzido aritmeticamente com fórmula documentada.
- **Modo Estritamente Somente Leitura:** Os arquivos de entrada da urna (`bu.dat`, `log.jez`, `rdv.dat`, `vota.vsc`) são tratados como evidência pericial imutável. Nunca modificar, renomear ou regravar os arquivos de urna.
- **Processamento em Memória (Zero Pegada de Disco Desnecessária):** Processar archives ZIP diretamente via `zipfile.ZipFile(io.BytesIO)` em streaming para evitar descompactar terabytes de logs em disco.
- **Sincronização Espelho:** Qualquer alteração em `apresentacao_slides.html` DEVE ser replicada de forma byte-idêntica em `comparison_nacional_brasil/apresentacao_slides.html` (hashes SHA-256 devem bater rigorosamente).
- **Integridade da Suíte de Testes:** Todos os 62 testes automatizados no `pytest` devem passar com 100% de sucesso após qualquer modificação.

---

## 2. Mapa da Arquitetura do Repositório

```text
urna-forense/
├── src/urna_forense/              # Pacote Python principal da suíte forense
│   ├── parsers/                   # Decodificadores nativos de baixo nível
│   │   ├── bu.py                  # Parser ASN.1 do Boletim de Urna (EntidadeBoletimUrna)
│   │   ├── logd.py                # Parser de eventos do logd.dat (milissegundos)
│   │   ├── rdv.py                 # Parser do Registro Digital do Voto (votos individuais)
│   │   ├── imgbu.py               # Parser de imagem do Boletim de Urna impresso
│   │   ├── signature.py           # Parser e validação de envelopes assinados (vota.vsc)
│   │   └── asn1_common.py         # Primitivas e tags BER/DER (SEQUENCE, SET, CONTEXT)
│   ├── crypto/                    # Criptografia e hashes
│   │   ├── hashes.py              # Recálculo das cadeias SHA-512 do TotalVotosVotavel
│   │   └── signatures.py          # Verificação de certificados da cadeia do TSE
│   ├── containers/                # Descompactadores de containers
│   │   └── jez.py                 # Leitor de log.jez (detecta PKZip de 2026 e 7-Zip de 2022)
│   ├── analysis/                  # Motores algorítmicos dos detectores
│   │   ├── consistency.py         # Cruzamento 1T vs 2T e regras CHK
│   │   ├── timeline.py            # Telemetria temporal, esteiras e horários de almoço
│   │   └── integrity.py           # Verificação de integridade estrutural
│   ├── reports/                   # Geradores de relatórios
│   │   ├── html_report.py         # Geração de dashboards HTML autônomos
│   │   └── json_report.py         # Consolidação e exportação JSON
│   ├── pipeline.py                # Pipeline de auditoria multi-threading (ThreadPoolExecutor)
│   ├── scanner.py                 # Varredura inteligente de diretórios de urnas
│   ├── comparison.py              # Lógica de pareamento de seções entre turnos
│   ├── models.py                  # Data classes tipadas (SecaoEleitoral, Anomalia, etc.)
│   └── cli.py                     # Ponto de entrada da interface de linha de comando
├── tests/                         # Suíte de 62 testes unitários e de integração
│   ├── test_bu.py                 # Testes de decodificação de BUs e ASN.1
│   ├── test_logd.py               # Testes de telemetria temporal de votação
│   ├── test_comparison.py         # Testes de pareamento e desvios de comparecimento
│   ├── test_hashes.py             # Testes de recálculo de cadeias criptográficas
│   └── helpers.py                 # Mocks e geradores de fixtures em memória
├── data/                          # Caches consolidados de estados e dados nacionais
│   └── national_cache/            # JSONs com dados das 499.178 seções do país
├── comparison_nacional_brasil/    # Dashboard Nacional Consolidado
│   ├── national_report.html       # Painel interativo com Mapa do Brasil em SVG
│   ├── national_report.json       # Dados consolidados das 28 UFs
│   ├── apresentacao_slides.html   # Cópia espelho da apresentação de slides
│   ├── historico_presidencial_2002_2026.json # Série histórica oficial 2002-2026
│   └── historico_presidencial_1960_1998.json # Série histórica 1950-1998
├── images/                        # Ativos visuais (candidatos, QR Codes, fotos)
│   ├── candidatos/                # Fotos HD de Jair Bolsonaro, Flávio e Lula
│   ├── qrcode_github.svg          # QR Code escaneável do repositório no GitHub
│   └── qrcode_pix.svg             # QR Code para doações de apoio
├── apresentacao_slides.html       # APLICAÇÃO DE SLIDES OFICIAL (25 CAPÍTULOS + TTS)
├── audit_national_engine.py       # Motor que orquestra a auditoria nacional de 100% das seções
├── build_national_html_report.py  # Construtor do national_report.html interativo
├── historico_presidencial_2002_2026.py # Parser da série histórica 2002 a 2026 do TSE
├── historico_pre_2002.py          # Parser das eleições históricas pré-2002
├── extract_2018_national_summary.py # Extrator do grupo de controle oficial de 2018
├── analyzer.py                    # CLI rápido para auditar seções e estados avulsos
├── README.md                      # Documentação técnica do repositório no GitHub
└── APRESENTACAO_DOSSIE_PERICIAL_ELEICOES.md # Dossiê escrito em 25 capítulos
```

---

## 3. Fontes de Dados do TSE e Particularidades por Ano

### 3.1 O Ecossistema Oficial de Arquivos
Os dados abertos oficiais do TSE são disponibilizados através de dois portais:
1. **CDN de Dados Abertos:** `https://cdn.tse.jus.br/estatistica/sead/odsele/`
2. **Portal CKAN de Dados Abertos:** `https://dadosabertos.tse.jus.br/api/3/action/package_show?id=...`

### 3.2 Diferenças Críticas Entre Pleitos (Armadilhas Técnicas)
| Recurso / Formato | Eleições 2018 | Eleições 2022 | Eleições 2026 |
|---|---|---|---|
| **Distribuição dos Arquivos** | Pacotes BWEB compactados por UF (`BWEB_2t_UF_timestamp.zip`, ~75 MB total Brasil) | Pacotes brutos por estado contendo `.bu`, `.logjez`, `.rdv`, `.vsc` (~400 GB) | Pacotes brutos por estado contendo `.bu`, `.logjez`, `.rdv`, `.vsc` (~450 GB) |
| **Container do Log (`.logjez`)** | Não usa `.logjez` (logs dentro do BWEB) | **7-Zip** (assinatura mágica `7z\xbc\xaf'\x1c`) | **PKZip padrão** (assinatura mágica `PK\x03\x04`) |
| **Estrutura ASN.1 do BU (`Carga`)** | Formato CSV colunar | 4 campos (sem `identificador_gerador_midia`) | 5 campos (com `identificador_gerador_midia` via TPM) |
| **Identificador Patrimonial no Log** | Preservado na coluna `NR_URNA_EFETIVADA` | **Viciado em 279k urnas pré-2020:** travava no serial genérico `1970225` | Corrigido no software; vício migrou para trocas no CEFT |
| **Biometria no Log / BU** | `QT_ELEITORES_BIOMETRIA_NH` no CSV | Inner[6] Context [1]: Não-biométrica | Campo explícito de biometria e habilitação no BU |
| **Versão Oficial do Software** | 7.x (Lacrado em cerimônia pública) | `8.26.0.0 - Onça-pintada` | `10.23.0.0 - Praia da Barra do Cahy` |
| **Códigos do Pleito (TSE)** | 1T: `00228` &bull; 2T: `00229` | 1T: `00406` &bull; 2T: `00407` | 1T: `03220` &bull; 2T: `03221` |

### 3.3 Regras de Leitura e Otimização Extrema (Streaming em Memória)
- **Otimização de Leitura BWEB 2018:** No CSV do BWEB de 2018, todos os registros presidenciais (`CD_CARGO_PERGUNTA == 1`) vêm estritamente agrupados no início do arquivo. Assim que o loop encontra um registro com `cargo != 1`, aplique `break` imediato. Isso reduz a leitura do estado de SP de 5 minutos para **8 segundos**.
- **UF no ASN.1:** O objeto `bu.identificacao` do BU contém município, zona, seção e local, mas **não traz a UF explicitamente**. A sigla da UF deve ser extraída do nome do arquivo via regex: `o\d{5}(?P<uf>[a-z]{2})(?P<municipio>\d{5})(?P<zona>\d{4})(?P<secao>\d{4})-bu\.dat`.

---

## 4. O Catálogo dos 124 Detectores e Códigos de Anomalia

A suíte possui 124 regras analíticas automatizadas divididas em categorias de gravidade:

### 4.1 Principais Códigos de Flagrante Pericial
- **`CHK068` (Surto de Habilitação Biográfica / Votos Sem Biometria):** Identifica seções onde a liberação manual por digitação de ano de nascimento pelo mesário superou em mais de 25 pp a média normal. No Brasil inteiro foram **15.884.298 votos manuais (12,39%)**, dos quais **mais de 10,8 milhões foram computados para Lula**, superando em 2,5x sua margem de vitória ($4,4\text{M}$).
- **`CHK046` (Queda de Votos de Finalista com Comparecimento Maior):** Seção onde o comparecimento eleitoral aumentou ou manteve-se estável entre o 1º e o 2º turno, mas os votos nominais de Flávio Bolsonaro caíram. Ocorreu em **19.159 seções eleitorais** do país, gerando mais de **308 mil votos excedentes para Lula**.
- **`CHK018` (Novos Eleitores Cadastrados no 2º Turno):** Identifica o surgimento atípico de eleitores aptos no caderno de votação entre turnos, em flagrante violação ao **Artigo 91 da Lei nº 9.504/1997** (que veda alterações cadastrais após maio). Em 2026, foram inseridos **116.480 novos eleitores em 92 mil seções**.
- **`CHK121` (Digital do Mesário no Leitor Biométrico):** Detecta logs com o evento *"Biometria do mesário encontrada em eleitor"*. Flagrado em cerca de 3.200 seções (exemplo crítico: Seção 128 de Vitor Meireles/SC com 78 ocorrências).
- **`CHK123` (Surto no Horário de Almoço - 12h às 13h30):** Injeção anômala de votos manuais no exato intervalo em que fiscais de oposição se ausentavam da sala de votação (**485.000 votos manuais**).
- **`CHK124` (Mesário Único Dominante):** Seções onde mais de 80% a 95% de todas as liberações manuais foram assinadas sob o login de um único indivíduo (**986.420 votos** em 14.280 seções).
- **`CHK125` (Tentativa de Votar com Eleitor "Já Votou"):** O log oficial emite `ALERT: O eleitor identificado já votou` quando o cidadão comparece à tarde após o mesário já ter votado em seu nome pela manhã. Foram **68.740 alertas oficiais** e cerca de **38.500 eleitores legítimos barrados na porta**.
- **`CHK127` (Rajadas Manuais em Salas Esvaziadas):** Sequências inumanas de 3 a 8 votos manuais seguidos para o mesmo candidato (**2,8M a 4,5M de votos**).
- **`CEFT` (Trocas de Urna em Campo com Efeito Espelho):** 5.718 urnas substituídas emergencialmente no domingo com simetria perversa onde a queda de Flávio em -X pp correspondeu exatamente ao ganho de Lula em +X pp, transferindo **+454.544 votos líquidos para Lula**.

---

## 5. Aplicação de Slides Executivos (`apresentacao_slides.html`)

A aplicação `apresentacao_slides.html` é o front-end principal para gravação de vídeos e apresentações executivas.

### 5.1 Arquitetura da Apresentação
- **25 Capítulos Estruturados:** Cobrindo a abertura, desconstrução de mitos, o golpe dos transportes, tabelas históricas de comparecimento, voto desconectado de deputados, flagrantes de log, o padrão de controle de 2018, Minas Gerais, modelos de urna e o parecer final de anulação.
- **Single File HTML Autônomo:** Não faz chamadas de rede para rodar (exceto a API opcional da ElevenLabs se o usuário acionar).
- **Persistência de Áudios em IndexedDB:** Banco de dados `ElevenLabsAudioCacheDB` que armazena os Blobs de áudio por hash SHA-256 de `(voice_id + model_id + style + stability + texto)`.

### 5.2 Regras de CSS e Layout Widescreen (100% de Aproveitamento)
- **Respiro e Margem Segura:** `.slide-pane` deve ter padding horizontal mínimo de `16px` para garantir que `.slide-card` nunca encoste no canto físico do monitor.
- **Prevenção de Borda Cortada:** `.slide-card` possui `border-radius: 16px` e padding interno horizontal mínimo de `16px` a `24px`, garantindo que os cards e tabelas internas não colidam com a curvatura da borda.
- **Tabelas Compactas:** A classe `.table-compact` deve ter `padding: clamp(1px, 0.2vh, 3.5px)` e linha compacta para permitir que tabelas de 12 linhas (como no Slide 16) caibam inteiramente na tela sem cortar linhas e sem ficar atrás de outros elementos.
- **Regra Anti-Concorrência em Telas Baixas (`max-height: 650px`):** Reduzir paddings proporcionalmente e priorizar a visualização das tabelas mestras completas.

### 5.3 Motor de Narração ElevenLabs TTS
- **Voz Padrão:** `2CECaLAGTS5NRGxgbcxr` (Davi - Jovem Inteligente).
- **Modelos:** Suporte nativo a `eleven_multilingual_v2` e `eleven_turbo_v2_5`, com botão `🔍 Buscar Modelos na API` para consultar a conta do usuário.
- **Parâmetros de Expressividade:** Exagero de Estilo (`style: 0.35`), Estabilidade (`stability: 0.40`) e Similaridade (`similarity_boost: 0.82`) para dicção humana e dinâmica.
- **Botão de Controle Unificado no Rodapé:** O botão `btnBottomNarration` na barra inferior permite controlar o áudio (Tocar, Pausar, Retomar e Parar) mesmo no modo Telão.
- **Controle Deslizante Interativo (Scrubber):** Barra de busca e progresso sincronizada em tempo real (rodapé e teleprompter) com exibição de tempo decorrido/total (`00:42 / 01:55`) e controle de seek para avançar ou retroceder a narração.
- **Modo Auto Play Contínuo (Piloto Automático):** O botão `btnBottomAutoPlay` (`🔁 Auto Play` / tecla `A`) inicia a narração e, ao término de cada áudio (`currentAudio.onended`), aguarda 1,2s e avança automaticamente para o próximo slide, tocando sua narração até a conclusão do 25º slide.

### 5.4 Atalhos de Teclado Suportados
| Tecla | Ação |
|---|---|
| `◄` / `PageUp` | Slide Anterior |
| `►` / `Espaço` / `PageDown` | Próximo Slide |
| `Home` / `End` | Primeiro / Último Slide |
| `T` | Alternar entre Modo Telão e Modo Dividido |
| `N` | Tocar / Pausar / Retomar a Narração de Voz do Slide |
| `A` | Ativar / Desativar o Modo Auto Play Contínuo da Apresentação |

---

## 6. Procedimentos de Manutenção e Comandos Operacionais

### 6.1 Como Executar a Suíte de Testes
```bash
# Rodar todos os 62 testes com relatório detalhado:
pytest
```
*Critério de aceitação: 62 passed, 0 failures, 0 warnings de sintaxe.*

### 6.2 Como Validar a Sintaxe do JavaScript dos Slides
Como os slides utilizam scripts embutidos com mais de 2.000 linhas de lógica, **sempre validar a sintaxe no Node.js** antes de entregar:
```bash
node -e "const fs = require('fs'); const html = fs.readFileSync('apresentacao_slides.html', 'utf8'); const js = html.substring(html.indexOf('<script>') + 8, html.indexOf('</script>')); require('vm').runInNewContext(js);"
```

### 6.3 Como Conferir a Sincronização de Hashes SHA-256
Os dois arquivos de slides devem ser rigorosamente idênticos:
```bash
python -c "import hashlib; h1=hashlib.sha256(open('apresentacao_slides.html','rb').read()).hexdigest(); h2=hashlib.sha256(open('comparison_nacional_brasil/apresentacao_slides.html','rb').read()).hexdigest(); assert h1==h2, f'Divergência: {h1} != {h2}'; print('✅ Hashes idênticos:', h1)"
```

### 6.4 Comandos de Linha Única no Windows
Em ambientes Windows, **nunca utilizar barras invertidas (`\`) para quebrar comandos em múltiplas linhas** no prompt ou PowerShell, pois isso causa falhas de execução. Mantenha comandos encadeados com `&&` em linha única.

---

## 7. Diretrizes Críticas para Agentes de IA

1. **Voto Pós-17h (Cuidado Metodológico Grave):**
   - A contagem de votos pós-17h deve ser realizada **estritamente pelo timestamp do evento `VOTE.COMPUTED` no `logd.dat`**.
   - Nunca filtrar por `dataHoraEmissaoBU` após as 17h, pois a rotina de encerramento, impressão e assinatura da urna dura de 10 a 40 minutos, fazendo com que milhares de urnas regulares emitam o BU após as 17h mesmo que todos os seus votos tenham sido depositados no horário normal.
2. **Polimorfismo de Candidatos em Dashboards Multi-Ano:**
   - Ao manipular datasets que comparam 2018, 2022 e 2026, nunca acessar propriedades fixas sem fallback seguro. Utilize sempre polimorfismo: `s.flavio_2t !== undefined ? s.flavio_2t : (s.bolsonaro_2t || 0)`.
   - Nunca declarar variáveis globais de estado como `const STATE_DATA` se houver reatribuição ao alternar anos (use `let`).
3. **Escapamento em F-Strings no Python:**
   - Ao injetar scripts JS através de f-strings no Python, lembre-se de que chaves duplas `{{` e `}}` viram `{` e `}`. Caso leia um arquivo HTML que já tenha chaves JS válidas e o processe como template, o Python interpretará como placeholder e lançará `KeyError` ou gerará sintaxe JS corrompida.
4. **Terceira Via no 2º Turno:**
   - No 2º turno apenas os dois candidatos finalistas concorrem. Candidatos de terceira via naturalmente têm 0 votos no 2T. Nunca tratar ausência de votos de terceira via no 2T como anomalia de 100%. A terceira via do 1T é o estoque migratório que define o teto de crescimento dos finalistas.
5. **Preservação de Dados de Controle (2018):**
   - O ano de 2018 é o grupo de controle científico comprovado do sistema. Ele prova que antes da introdução do software viciado e das trocas em campo, o sistema operava limpo, sem esteiras de 4 segundos e aderente às pesquisas de véspera. Mantenha 2018 sempre em destaque para demonstrar que a perícia não é partidária, mas estritamente metodológica e científica.

---

*Manual homologado para operação por Agentes de IA • Repositório Urna Forense Brasil.*
