# Documentação de Formatos dos Arquivos da Urna Eletrônica (2026)

Este documento atende ao **Requisito 18**, distinguindo rigorosamente entre o que é **FORMATO DOCUMENTADO** (especificações e notas públicas oficiais da Justiça Eleitoral e repositórios de referência) e **FORMATO INFERIDO** (observações empíricas feitas nos bytes dos arquivos disponíveis).

---

## 1. Classificação Geral dos Arquivos

| Arquivo | Descrição | Formato Real | Status da Especificação |
|---|---|---|---|
| `-bu.dat` | Boletim de Urna | DER/BER em envelope ASN.1 | **FORMATO DOCUMENTADO** (v2) |
| `-rdv.dat` | Registro Digital do Voto | DER/BER (sem envelope genérico) | **FORMATO DOCUMENTADO** (v2) |
| `-vota.vsc` | Assinatura digital dos arquivos | DER/BER com modelo no final | **FORMATO DOCUMENTADO** com desvios observados |
| `-log.jez` | Pacote de logs da urna | Container ZIP (PK\x03\x04) | **FORMATO INFERIDO / CONFLITO** com LEIA-ME |
| `-imgbu.dat` | Spool de impressão do BU | Envelope DER com texto ESC/POS | **FORMATO DOCUMENTADO** (envelope) + **INFERIDO** (spool) |
| `logd.dat` | Conteúdo interno do log | Texto TSV em Latin-1 (6 colunas) | **FORMATO INFERIDO** (conhecido publicamente) |

---

## 2. Padrão de Nomenclatura dos Arquivos

### [FORMATO DOCUMENTADO]
Os arquivos distribuídos pelo Tribunal Superior Eleitoral seguem o padrão::

```text
o<5 dígitos do pleito><UF><5 dígitos município><4 dígitos zona><4 dígitos seção>-<tipo>.<extensão>
```

Exemplo para a urna analisada:
- `o03220`: pleito `3220` (Eleições Gerais 2026 — 1º Turno);
- `sc`: Unidade da Federação (Santa Catarina);
- `80535`: Código do município no cadastro do TSE (Braço do Norte/SC);
- `0044`: Zona eleitoral (44ª Zona de SC);
- `0144`: Seção eleitoral (Seção 144);
- `-bu.dat`: Boletim de Urna estruturado;
- `-imgbu.dat`: Cópia do boletim impresso;
- `-log.jez`: Container compactado do log;
- `-rdv.dat`: Registro Digital do Voto;
- `-vota.vsc`: Arquivo de assinatura digital.

---

## 3. Arquivo de Log (`-log.jez` e `logd.dat`)

### [FORMATO DOCUMENTADO vs INFERIDO: CONFLITO NO CONTAINER]
- **Documentado no LEIA-ME oficial (`leiame.pdf`):**  
  > *"Ao ser extraído da urna, ele é empacotado num arquivo em formato 7z e identificado de acordo com a carga realizada."*
- **Observado empiricamente nos bytes de 2026:**  
  Todos os arquivos `-log.jez` iniciam com os magic bytes `PK\x03\x04` (ZIP padrão PKWARE), com compressão deflate (método 8). Não são arquivos 7-Zip. A ferramenta identifica pelo conteúdo e processa ZIP nativamente, suportando 7z como fallback.

### [FORMATO DOCUMENTADO: LOG DE CONTINGÊNCIA]
Quando há substituição de urna na seção, o `-log.jez` contém, além do `logd.dat` da urna que encerrou, pacotes `.jez` aninhados nomeados com o número da urna e data/hora da urna substituída. A ferramenta descompacta os logs em memória de forma recursiva (até 3 níveis) e ordena as urnas cronologicamente.

### [FORMATO INFERIDO: ESTRUTURA DO `logd.dat`]
O arquivo é texto codificado em Latin-1 com linhas separadas por CRLF ou LF, contendo 6 campos delimitados por caractere TAB (`\t`):

```text
<DATA HORA>\t<SEVERIDADE>\t<ID_URNA>\t<APLICATIVO>\t<MENSAGEM>\t<CODIGO_64BITS>
```

1. **DATA E HORA:** `DD/MM/AAAA HH:MM:SS` em horário local da urna (SC segue UTC-03:00).
2. **SEVERIDADE:** `INFO` ou `ALERTA`.
3. **ID_URNA:** Número interno da urna com 8 dígitos (`02191040`).
4. **APLICATIVO:** Módulo do ecossistema da urna (`LOGD`, `SCUE`, `GAP`, `ATUE`, `VOTA`, `INITJE`).
5. **MENSAGEM:** Texto livre do evento, frequentemente contendo parâmetros entre colchetes (`[bu.dat]`, `[Início]`).
6. **CÓDIGO DE 64 BITS (16 hexadecimais):**  
   *Classificação:* **NÃO FOI POSSÍVEL VERIFICAR**. O algoritmo de cálculo desse código não é público. Linhas idênticas repetidas geram códigos diferentes, demonstrando que não se trata de uma função pura do texto visível da linha (pode envolver HMAC com chave secreta em hardware, contador interno ou encadeamento). A ferramenta registra e preserva os códigos, sem pretender atestar sua validade matemática.

---

## 4. Boletim de Urna (`-bu.dat`)

### [FORMATO DOCUMENTADO: ESPECIFICAÇÃO ASN.1 v2]
O arquivo é codificado em ASN.1 BER/DER conforme o módulo `ModuloBU` do TSE:

1. **Envelope externo (`EntidadeEnvelopeGenerico`):**
   - `cabecalho` (`CabecalhoEntidade`): `dataGeracao` (DataHoraJE `YYYYMMDDThhmmss`) e `idEleitoral` (`[2] IDPleito 3220`);
   - `fase`: `ENUMERATED { oficial(2) }`;
   - `urna`: `OPTIONAL` (omitido no BU de seção);
   - `identificacao`: `[0] IdentificacaoSecaoEleitoral` (município, zona, local, seção);
   - `tipoEnvelope`: `ENUMERATED { envelopeBoletimUrna(1) }`;
   - `conteudo`: `OCTET STRING` contendo a `EntidadeBoletimUrna`.

2. **Entidade interna (`EntidadeBoletimUrna`):**
   - `cabecalho`: `dataGeracao` e `idEleitoral`;
   - `fase`: `oficial(2)`;
   - `urna`: Dados de hardware, software (`10.23.0.0 - Praia da Barra do Cahy`) e correspondência de carga;
   - `identificacaoSecao`: Município `80535`, Zona `44`, Local `1236`, Seção `144`;
   - `dataHoraEmissao`: Data/hora em que o BU foi emitido na tela/memória;
   - `dadosSecaoSA`: `[0] DadosSecao` contendo `dataHoraAbertura` (`08:00:01`) e `dataHoraEncerramento` (`17:01:17`);
   - `qtdEleitoresCompareceram`: Quantidade total de eleitores que votaram (`324`);
   - `detalhamentoComparecimento`: `[1]` com `semBiometria`, `porBiometria`, `porBiografia`;
   - `resultadosVotacaoPorEleicao`: Lista de eleições (`6257` para Presidente; `6259` para cargos estaduais);
   - `historicoCodigosCarga`: Sequência com os códigos de carga utilizados.

### [FORMATO DOCUMENTADO: CADEIA DE HASHES DO BU]
Cada votável possui um hash SHA-512 encadeado conforme especificado no comentário oficial do arquivo `bu.asn1`:

- **Cabeçalho:**  
  `idPleito(5)|idEleicao(5)|municipio(5)|zona(4)|secao(4)|codigoCarga(24)`  
  Hash inicial: `H0 = SHA512(cabeçalho)`.
- **Blocos subsequentes (ordenados por `ordemImpressao` e `ordemGeracaoHash`):**  
  `Hi = SHA512(Hi-1_HEX_UPPER | ordemGeracaoHash | codigoCargo | tipoVoto | quantidade [| codigo | partido])`.
- **Último hash:**  
  O hash final deve ser idêntico ao campo `ultimoHashVotosVotavel` de cada eleição.

*Resultado da verificação na Seção 144:* **100% VALIDADO** para todas as eleições e votáveis, utilizando a fórmula oficial documentada.

---

## 5. Registro Digital do Voto (`-rdv.dat`)

### [FORMATO DOCUMENTADO: ESPECIFICAÇÃO ASN.1 v2]
Entidade raiz `EntidadeResultadoRDV`:
- Não utiliza o envelope genérico (diferente do BU);
- `cabecalho` e `urna` idênticos aos do BU;
- `rdv`: `EntidadeRegistroDigitalVoto` com `pleito`, `fase`, `identificacao`, `historicoCodigosCarga` e `eleicoes`;
- Em `eleicoesVota`: para cada eleição, lista de `VotosCargo`. Cada cargo possui `quantidadeEscolhas` e `votos` (`tipoVoto` e `digitacao`).

### [PROTEÇÃO DE SIGILO DO VOTO]
O RDV embaralha os votos gravados de modo a impedir correlação com a ordem de chegada dos eleitores. Esta ferramenta processa **apenas agregados quantitativos** por cargo e número, sem nunca expor ou serializar listas ordenadas de registros individuais.

---

## 6. Arquivo de Assinatura Digital (`-vota.vsc`)

### [FORMATO DOCUMENTADO com DESVIOS OBSERVADOS]
O arquivo `-vota.vsc` é uma estrutura ASN.1 contendo:

1. **Assinatura de Software (`assinaturaSW`):**  
   Usuário `SEVIN`, algoritmo de governo `CEPESC` (código 3). Não possui algoritmo público de verificação; a ferramenta confere o hash SHA-512 do conteúdo autoassinado.
2. **Assinatura de Hardware (`assinaturaHW`):**  
   Usuário `UEAO<número_interno_urna>`, algoritmo `EdDSA Ed521` (código 4) ou `ECDSA P-521` (código 2).
3. **Lista de Arquivos Assinados (`conteudoAutoAssinado`):**  
   Sequência de entradas `(nomeArquivo, tamanho, hash_sha512, assinatura)`.

### [DESVIOS DO MODELO EM RELAÇÃO À MINUTA ASN.1 PUBLICADA]
- Na especificação publicada, o `modeloEquipamento` é o primeiro campo da SEQUENCE raiz. Nos arquivos de 2026 observados, o modelo vem em uma SEQUENCE pequena ao final do arquivo: `SEQUENCE { ENUMERATED modelo, ENUMERATED algoritmo }`.
- Os campos opcionais `conjuntoChave` e `certificadoDigital` utilizam tags de contexto implícitas `[0]` e `[1]`.
- O certificado digital da urna vem embutido em formato PEM na assinatura de hardware.

---

## 7. Spool de Impressão do BU (`-imgbu.dat`)

### [FORMATO INFERIDO: NATUREZA DO CONTEÚDO]
Embora denominado "imagem do BU" no LEIA-ME, o conteúdo do envelope não é PNG, JPEG nem BMP. Trata-se do fluxo textual do spool de impressão enviado à impressora térmica da urna:
- Codificação Latin-1 com quebras de linha padrão;
- Bytes de controle ASCII (como `\x15` NAK) usados para formatação e quebras de página;
- Tabelas completas com número de candidatos, votos e códigos verificadores de linha.

A ferramenta decodifica o texto preservando a integridade da evidência, permitindo conferência independente sem necessidade de OCR.
