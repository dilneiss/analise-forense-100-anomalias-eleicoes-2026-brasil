/**
 * FONTE ÚNICA DE VERDADE DO VÍDEO.
 *
 * Toda cifra abaixo vem dos arquivos públicos do TSE (caderno de votação,
 * boletins de urna e logs de urna). Nenhum componente calcula número:
 * todos apenas animam o que está aqui.
 *
 * CLASSIFICAÇÃO DE CADA CAMPO (obrigatória manter):
 *  - CONTAGEM DIRETA  -> obtido por contagem de registros, sem inferência
 *  - ESTIMATIVA       -> projeção por boletim de urna; o log da urna NÃO
 *                        registra candidato (sigilo do voto, Art. 14 CF/88)
 */
export const DADOS = {
  /** CONTAGEM DIRETA — diff do caderno de votação entre 1º e 2º turno (CHK018) */
  novosEleitores: 116480,

  /** CONTAGEM DIRETA — seções com inserção de aptos entre os dois turnos */
  secoesAfetadas: 92000,

  /** CONTAGEM DIRETA — mesmo cálculo em 2018: nenhum novo apto entre turnos */
  controle2018: 0,

  /** ESTIMATIVA por boletim de urna das mesmas seções (o log não traz candidato) */
  pctLula: 80,
  /** ESTIMATIVA por boletim de urna das mesmas seções */
  pctFlavio: 20,

  /** CONTAGEM DIRETA — prazo legal de congelamento do cadastro */
  prazoLegalDias: 150,

  /** CONTAGEM DIRETA — eleitorado apto do pleito */
  aptosTotal: 156455871,

  /** CONTAGEM DIRETA — comparecimento apurado em cada turno */
  comparecimento1T: 125274487,
  comparecimento2T: 128235243,
  saltoComparecimento: 2960756,
} as const;

const nf = new Intl.NumberFormat("pt-BR");

export const fmt = (n: number) => nf.format(Math.round(n));

/** Percentual de 2 casas, com vírgula (padrão pt-BR) */
export const fmtPct = (n: number) =>
  n.toLocaleString("pt-BR", { minimumFractionDigits: 1, maximumFractionDigits: 1 }) + "%";
