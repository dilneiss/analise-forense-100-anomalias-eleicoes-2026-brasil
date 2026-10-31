# scripts/en_builder/apply_exact_residuals.py
import json

with open("presentation_slides_en.html", "r", encoding="utf-8") as f:
    text = f.read()

start_str = "const SLIDES = "
start_idx = text.find(start_str) + len(start_str)
end_idx = text.find(";\n\n        let currentSlideIdx", start_idx)

slides_en = json.loads(text[start_idx:end_idx].strip())

EXACT_REPLACEMENTS = [
    # Slide 01
    ("maioria sociológica e o voto legítimo das urnas, Flávio Bolsonaro é o legítimo Presidente", "sociological majority and legitimate ballot votes, Flávio Bolsonaro is the true President"),
    
    # Slide 02
    ("PLEITO 2018 (CONTROLE)", "2018 ELECTION (CONTROL)"),
    ("PLEITO 2022 (LOG DEFECT)", "2022 ELECTION (LOG DEFECT)"),
    ("PLEITO 2026 (TABLE FRAUD)", "2026 ELECTION (TABLE FRAUD)"),
    ("48 official ballot reports audited from Pleito 229;", "48 official ballot reports audited from Election 229;"),
    ("FAIXA INFERIOR DE CONCLUSÃO TÉCNICA (100% LARGURA)", "BOTTOM BANNER: TECHNICAL CONCLUSION (100% WIDTH)"),
    
    # Slide 03
    ("TODOS OS VOTOS DO DIA INTEIRO (das 8h às 17h)", "ALL VOTES OF THE ENTIRE DAY (from 8 AM to 5 PM)"),
    ("de urnas cujo Boletim de Urna (BU) foi impresso", "of machines whose Ballot Report (BU) was printed"),
    ("alegando falsamente que todos aqueles votos haviam sido digitados após o horário legal!", "falsely claiming that all those votes had been cast after legal closing hours!"),
    ("SALDO LÍQUIDO DE APENAS +2.747 VOTOS: NENHUM IMPACTO NA ELEIÇÃO!", "NET MARGIN OF MERELY +2,747 VOTES: ZERO IMPACT ON THE ELECTION!"),
    ("FAIXA INFERIOR DE CONCLUSÃO FORENSE (100% LARGURA)", "BOTTOM BANNER: FORENSIC CONCLUSION (100% WIDTH)"),
    ("🔬 <strong>A Conclusão Científica:</strong> Mesmo se 100% dos 34.393 votos após as 17h fossem anulados ou transferidos para Flávio, Lula ainda venceria nacionalmente por mais de <strong>4,36 milhões de votos</strong>. A prorrogação das 17h não teve nenhum impacto material no resultado!", "🔬 <strong>The Scientific Conclusion:</strong> Even if 100% of the 34,393 votes cast after 5 PM were annulled or transferred to Flávio, Lula would still lead nationally by more than <strong>4.36 million votes</strong>. The post-5 PM extension had zero material impact on the election outcome!"),
    
    # Slide 05
    ("2º TURNO • 25/10/2026 (APURAÇÃO AO VIVO)", "2ND ROUND • 10/25/2026 (LIVE VOTE TALLY)"),
    ("Transmissão Oficial da Apuração do 2º Turno", "Official 2nd Round Tally Broadcast"),
    ("o salto atípico de quase 11 milhões de votos atrairia a perícia.", "the atypical surge of nearly 11 million votes would trigger forensic scrutiny."),
    ("oficiais do TSE</strong> para que cada cidadão tire as suas próprias conclusões.", "official TSE records</strong> so every citizen can draw their own conclusions."),
    
    # Slide 06
    ("Impõe Anulação Total!", "Mandates Complete Annulment!"),
    ("de todo o crescimento</strong> (+2,95M votos), viabilizado pelo desabamento da biometria no Nordeste.", "of all vote growth</strong> (+2.95M votes), enabled by the collapse of biometrics in the Northeast."),
    ("CHK125: Eleitor já votou! (Cidadão Barrado)", "CHK125: Voter has already voted! (Citizen Barred)"),
    ("FAIXA INFERIOR DE CONCLUSÃO JURÍDICA VINCULANTE (100% LARGURA)", "BOTTOM BANNER: BINDING LEGAL VERDICT (100% WIDTH)"),
    ("A soma dos votos sob vício comprovado nos logs apenas no Nordeste (3.269.379 sem biometria + 1.420.000 em esteira robótica = 4.689.379 votos</strong>) é <strong>MAIOR do que toda a margem nacional de Lula no Brasil (4.401.534 votos)</strong>! Pelo Artigo 219 (Prejudice Principle) e Artigo 222 do Código Eleitoral, <strong>basta este achado factual para impor a ANULAÇÃO INTEGRAL DA ELEIÇÃO PRESIDENCIAL NACIONAL!</strong>", "The total votes with proven forensic defects in the logs within the Northeast alone (3,269,379 non-biometric + 1,420,000 in robotic queues = 4,689,379 votes</strong>) is <strong>LARGER than Lula's entire national margin across Brazil (4,401,534 votes)</strong>! Under Article 219 (Prejudice Principle) and Article 222 of the Electoral Code, <strong>this factual finding alone compels the COMPLETE ANNULMENT OF THE NATIONAL PRESIDENTIAL ELECTION!</strong>"),
    
    # Slide 07
    ("PLEITO OFICIAL 2018", "2018 OFFICIAL ELECTION"),
    ("PLEITO OFICIAL 2022", "2022 OFFICIAL ELECTION"),
    ("PLEITO OFICIAL 2026", "2026 OFFICIAL ELECTION"),
    ("Haddad: 44,87% &bull; 47.040.906 votos", "Haddad: 44.87% &bull; 47,040,906 votes"),
    ("+10.756.941 votos", "+10,756,941 votes"),
    ("• <strong>Pesquisas:</strong> Ibope e Datafolha cravaram exatamente 55% x 45% na véspera.", "• <strong>Polls:</strong> Ibope and Datafolha projected exactly 55% x 45% on election eve."),
    ("Bolsonaro: 49,10% &bull; 58.206.354 votos", "Bolsonaro: 49.10% &bull; 58,206,354 votes"),
    ("+2.139.645 votos", "+2,139,645 votes"),
    ("• <strong>Urnas UE2020:</strong> <strong>Jair Bolsonaro venceu com 51,05% (+1,07M votos)</strong>.", "• <strong>UE2020 EVMs:</strong> <strong>Jair Bolsonaro won with 51.05% (+1.07M votes)</strong>."),
    ("+4.430.099 votos", "+4,430,099 votes"),
    ("• <strong>A Ruptura Inédita:</strong> Comparecimento inflou em <strong>+2.960.756 votantes no 2T</strong>;", "• <strong>The Unprecedented Rupture:</strong> Turnout surged by <strong>+2,960,756 voters in 2nd round</strong>;"),
    ("Bolsonaro cresceu <strong>+8.520.837</strong> votos;<br>             • Haddad absorveu +15.698.855 votos da 3ª via;<br>             • Bolsonaro manteve folga líquida de +10,75M.", "Bolsonaro grew by <strong>+8,520,837</strong> votes;<br>             • Haddad absorbed +15,698,855 third-party votes;<br>             • Bolsonaro maintained a net lead of +10.75M."),
    ("Bolsonaro cresceu <strong>+7.134.009</strong> votos;<br>             • Lula cresceu apenas +3.086.495 votos;<br>             • Bolsonaro cresceu o dobro, mas urnas velhas viraram.", "Bolsonaro grew by <strong>+7,134,009</strong> votes;<br>             • Lula grew by only +3,086,495 votes;<br>             • Bolsonaro grew twice as much, but legacy machines flipped."),
    ("muito menores do que o volume total de votos sob vício comprovado nas urnas anômalas</strong>, provando que o resultado foi inteiramente fabricado nas máquinas com vício de hardware e fraude operacional!", "far smaller than the total volume of proven defective votes in anomalous machines</strong>, proving that the official outcome was entirely manufactured through hardware defects and operational fraud!"),
    
    # Slide 08
    ("Year & Pleito Presidencial", "Year & Presidential Election"),
    ("Comparecimento 1º Turno", "1st Round Turnout"),
    ("Comparecimento 2º Turno", "2nd Round Turnout"),
    ("Variação Real (1T &rarr; 2T)", "Net Variation (1T &rarr; 2T)"),
    ("Forensic Diagnostic Oficial", "Official Forensic Assessment"),
    ("NORMAL:</span> Desmobilização natural e biológica do eleitorado (-1,81M).", "NORMAL:</span> Natural biological demobilization of the electorate (-1.81M)."),
    ("NORMAL:</span> Desidratação habitual de comparecimento (-2,83M de eleitores).", "NORMAL:</span> Habitual voter turnout contraction (-2.83M voters)."),
    ("NORMAL:</span> Mesmo na eleição mais acirrada, quase 3M a menos votaram.", "NORMAL:</span> Even in the tightest election, nearly 3M fewer voted."),
    ("PADRÃO DE CONTROLE:</span> Comparecimento caiu 1,43M; Bolsonaro +10,75M de folga.", "CONTROL STANDARD:</span> Turnout dropped 1.43M; Bolsonaro kept +10.75M lead."),
    ("CARDS DE SÍNTESE COMPARATIVA E CONCLUSÃO PERICIAL (100% LARGURA)", "SUMMARY CARDS & FORENSIC CONCLUSION (100% WIDTH)"),
    ("s consecutivos</strong> e em todas as 6 eleições normais com segundo turno, o comparecimento sempre caiu entre <strong>-1,4M e -4,6M</strong>.", "s consecutive years</strong> and across all 6 normal elections with a second round, turnout always declined between <strong>-1.4M and -4.6M</strong>."),
    
    # Slide 09
    ("+8,52 Milhões de Votos", "+8.52 Million Votes"),
    ("INVERTE A ELEIÇÃO NACIONAL", "REVERSES NATIONAL ELECTION"),
    ("nas para <strong>disfarçar o despejo de votos anômalos de mesa</strong>!", "tice to <strong>disguise the injection of anomalous table votes</strong>!"),
    
    # Slide 10
    ("🛡️ <strong>Exército de Fiscais Partidários no 1T:</strong>", "🛡️ <strong>Army of Party Poll Watchers in 1st Round:</strong>"),
    ("O mesário não tinha como apertar branco 4 vezes para acelerar sem gerar divergência estatística absurda nas atas locais.", "Poll workers could not press blank 4 times to speed up without creating glaring statistical discrepancies on local tally sheets."),
    ("e nulos of Brazil somam apenas 4,15M de votos. Mesmo se 100% deles fossem sem digital, sobram <strong>mais de 11,73 milhões de votos nominais válidos</strong>!", "and null votes across Brazil total only 4.15M. Even if 100% were non-biometric, <strong>over 11.73 million valid candidate votes remain</strong>!"),
    ("📊 <strong>96,4% de Votos Válidos Nominais:</strong> Nas seções com surto manual, brancos e nulos foram de apenas 2,5% a 3,6%. Mais de <strong>76% a 93% dos votos nominais foram computados para Lula (13)</strong>!", "📊 <strong>96.4% Valid Candidate Votes:</strong> In sections with manual surges, blank and null were only 2.5% to 3.6%. Over <strong>76% to 93% of candidate votes were recorded for Lula (13)</strong>!"),
    ("ic Diagnostic Incontestável:</strong> A eleição da maior bancada do PL e de governadores no 1º turno prova a força da maioria sociológica real. A aparente virada de Lula no 2º turno decorreu exclusivamente da desmobilização de fiscais e da injeção de mais de 10,8 milhões de votos nominais sem biometria nas salas sem fiscalização!", "ic Assessment:</strong> The election of the largest conservative Congressional bloc and governors in the 1st round proves the true sociological majority. Lula's apparent 2nd round reversal resulted solely from watcher demobilization and the injection of over 10.8 million candidate votes without biometrics in unmonitored rooms!"),
    
    # Slide 11
    ("validação digital consistente no sensor; exceções manuais apenas em idosos/lavradores.", "consistent biometric verification on the sensor; manual overrides only for elderly/agricultural workers."),
    ("RESULTADO LIMPO: CONFIRMOU AS PESQUISAS E A VONTADE POPULAR", "CLEAN RESULT: CONFIRMED PRE-ELECTION POLLS AND THE POPULAR WILL"),
    ("Votos consecutivos em <strong>4 a 6 segundos", "Consecutive votes in <strong>4 to 6 seconds"),
    ("🚨 2. Desabamento Biométrico (&gt; 30-50%):", "🚨 2. Biometric Collapse (&gt; 30-50%):"),
    ("👤 3. Mesário Único Dominante (&gt; 80-95%):", "👤 3. Dominant Single Worker (&gt; 80-95%):"),
    ("Um único indivíduo na mesa assina todas as exceções manuais, afastando os colegas", "A single individual signs all manual overrides, sidelining colleagues"),
    ("485k votos inseridos entre 12h e 13h30 com salas vazias de fiscais e blocos de 3 a 8 votos seguidos.", "485k votes entered between 12:00 and 13:30 with empty rooms and consecutive blocks of 3 to 8 votes."),
    ("5.718 urnas trocadas onde 88% ocorreram cirurgicamente onde Flávio liderava.", "5,718 machines swapped where 88% occurred surgically where Flávio led."),
    ("FAIXA INFERIOR DE CONCLUSÃO FORENSE (100% LARGURA)", "BOTTOM BANNER: FORENSIC CONCLUSION (100% WIDTH)"),
    ("Nós não dizemos que 'toda a eleição foi uma fraude'. Mais de 80% das urnas of Brazil funcionaram perfeitamente e confirmaram a liderança conservadora. Toda a vitória oficial de Lula foi forjada dentro desse bolsão de 15% a 20% de urnas anômalas", "We do not state that 'the entire election was a fraud'. Over 80% of voting machines in Brazil operated cleanly and confirmed the conservative lead. Lula's entire official margin was manufactured inside this pocket of 15% to 20% anomalous machines"),
    
    # Slide 12
    ("ELEIÇÕES 2018 &bull; CONTROLE", "2018 ELECTIONS &bull; CONTROL"),
    ("Urnas Viciadas: ZERO", "Tainted Machines: ZERO"),
    ("Bolsonaro venceu com <strong>55,13% (+10,75M votos)</strong> cravando as pesquisas.", "Bolsonaro won with <strong>55.13% (+10.75M votes)</strong> matching polls exactly."),
    ("ELEIÇÕES 2022 &bull; HARDWARE", "2022 ELECTIONS &bull; HARDWARE"),
    ("Bolsonaro venceu com 51,05% (+1,07M votos)!", "Bolsonaro won with 51.05% (+1.07M votes)!"),
    ("ELEIÇÕES 2026 &bull; CEFT E MESA", "2026 ELECTIONS &bull; CEFT & TABLE"),
    ("1,42M de votos em &lt; 10s e 485k manuais no almoço em salas vazias.", "1.42M votes in &lt; 10s and 485k manual votes at lunch in empty rooms."),
    ("Quando Começaram a Surgir as Yearmalias nas Urnas Eletrônicas?", "When Did Anomalies Begin Appearing in Electronic Voting Machines?"),
    ("Bolsonaro venceu por +10,75M confirmando pesquisas.", "Bolsonaro won by +10.75M confirming pre-election polls."),
    ("Barroso na Câmara solta a frase: <em>"Eleição não se ganha, se toma"</em> (ecoando José Dirceu).", "Barroso in Congress uttered: <em>"Elections are not won, they are taken"</em> (echoing José Dirceu)."),
    ("<strong style="color: #fbbf24;">3. Eleições 2022:</strong><br>                 Surgem as 279k urnas velhas sem código individual no log (+4,35M pró-Lula).", "<strong style="color: #fbbf24;">3. 2022 Elections:</strong><br>                 279k legacy machines appear without unique log IDs (+4.35M for Lula)."),
    ("<strong style="color: #7dd3fc;">4. Eleições 2026:</strong><br>                 O vício migra para as 5.718 trocas de urna no CEFT e esteiras de mesários.", "<strong style="color: #7dd3fc;">4. 2026 Elections:</strong><br>                 Fraud migrates to 5,718 CEFT machine swaps and poll worker queues."),
    ("Em 2018 a eleição foi ganha no voto limpo. Em 2022 e 2026, o vício foi plantado no hardware e depois na esteira de mesa para que a eleição fosse <strong>tomada na marra contra a vontade das urnas limpas!</strong>", "In 2018 the election was won in clean voting. In 2022 and 2026, defects were embedded in hardware and then table queues so the election was <strong>taken by force against the will of clean voting machines!</strong>"),
    
    # Slide 13
    ("3.200 seções</strong> registraram mesários colocando a própria digital!", "3,200 sections</strong> logged poll workers placing their own fingerprint!"),
    ("FLAGRANTE 2 &bull; 106 URNAS DE VOTO ZERO", "FLAGRANT 2 &bull; 106 ZERO-VOTE MACHINES"),
    ("100% DOS VOTOS NOMINAIS", "100% OF CANDIDATE VOTES"),
    ("Flávio pontuou dezenas de votos no 1T, e no 2T teve <strong>rigorosamente ZERO</strong> votos;", "Flávio scored dozens of votes in 1T, and in 2T had <strong>strictly ZERO</strong> votes;"),
    ("114 Cidades com Mais Votos que Habitantes!", "114 Towns with More Votes than Inhabitants!"),
    ("(com bebês e crianças) e <strong>3.420 votos apurados</strong>!;", "(including infants and children) and <strong>3,420 votes counted</strong>!;"),
    ("38k habitantes e 39.850 votos válidos computados nas urnas;<br>", "38k inhabitants and 39,850 valid votes tallied in machines;<br>"),
    ("• <strong>732 Cidades Infladas:</strong> 4,28M de votos válidos gerando <strong>+1.420.000 votos de frente para Lula</strong>.", "• <strong>732 Inflated Towns:</strong> 4.28M valid votes generating <strong>+1,420,000 lead for Lula</strong>."),
    ("O mesário já havia computado o voto pelo faltoso de manhã; quando o cidadão real chegou à tarde, a urna travou com o alerta CHK125!", "The poll worker had already cast the vote for the absent citizen in the morning; when the real citizen arrived in the afternoon, the machine locked with alert CHK125!"),
    ("114 cidades onde os votos apurados superaram toda a população viva do município e quase <strong>38.500 cidadãos barrados na porta da seção</strong>", "114 towns where tallied votes exceeded the total living population and nearly <strong>38,500 citizens were barred at the polling station door</strong>"),
    
    # Slide 14
    ("FLAGRANTE 5 &bull; MESÁRIO ÚNICO DOMINANTE", "FLAGRANT 5 &bull; DOMINANT SINGLE WORKER"),
    ("Somando de <strong>2,8M a 4,5M de votos</strong> gerados nesses momentos de calmaria;", "Totalling from <strong>2.8M to 4.5M votes</strong> generated during these quiet intervals;"),
    ("FLAGRANTE 7 &bull; URNAS TROCADAS EM CAMPO", "FLAGRANT 7 &bull; MACHINES SWAPPED IN FIELD"),
    ("9.833.696 Votos em 39.652 Urnas de Contingência!", "9,833,696 Votes in 39,652 Contingency Machines!"),
    ("5.718 urnas trocadas em campo e reposições de mídia que transferiram +454k votos a Lula com o Efeito Espelho;", "5,718 machines swapped in field and media replacements transferring +454k votes to Lula via Mirror Effect;"),
    ("4.751.432 Votos em 19.159 Urnas com Queda Nominal!", "4,751,432 Votes in 19,159 Machines with Candidate Vote Drop!"),
    ("O comparecimento da seção subiu no 2T, mas Flávio perdeu votos nominais próprios do 1T!;<br>                     • <strong>Casos Extremos:</strong> Quedas em RR (-11.647 votos), TO (-1.405) e MT (-12,48 pp);<br>                     • <strong>Canibalização:</strong> Lula absorveu 100% dos novos votantes e ainda canibalizou votos consolidados do adversário.", "Turnout in the precinct grew in 2T, yet Flávio lost his own candidate votes from 1T!;<br>                     • <strong>Extreme Cases:</strong> Drops in RR (-11,647 votes), TO (-1,405) and MT (-12.48 pp);<br>                     • <strong>Cannibalization:</strong> Lula absorbed 100% of new voters and cannibalized verified opponent votes."),
    ("VOTOS PRÓPRIOS DO 1T SUMIRAM ENQUANTO A SEÇÃO CRESCEU!", "CANDIDATE VOTES FROM 1T DISAPPEARED WHILE TURNOUT GREW!"),
    ("Entre <strong>6,4 milhões e 15,8 milhões de votos sob vício comprovado</strong> &mdash; um volume de 1,5x a 3,6x MAIOR do que toda a margem nacional de 4,4 milhões de votos de Lula", "Between <strong>6.4 million and 15.8 million votes with proven defects</strong> &mdash; a volume 1.5x to 3.6x LARGER than Lula's entire national margin of 4.4 million votes"),
    
    # Slide 15
    ("1.428.650 votos", "1,428,650 votes"),
    ("30.010.000 votos", "30,010,000 votes"),
    ("75.275.000 votos", "75,275,000 votes"),
    ("19.700.000 votos", "19,700,000 votes"),
    ("Em 2 segundos um eleitor não consegue nem dar dois passos para sair da cabine e o outro entrar!;                     <br>• <strong>A Conclusão Inegável:</strong> <strong>A cabine estava vazia</strong>: era o mesário operando em lote na velocidade máxima do teclado!", "In 2 seconds a voter cannot even take two steps to leave the booth for the next to enter!;                     <br>• <strong>The Inescapable Conclusion:</strong> <strong>The booth was empty</strong>: it was the poll worker keying in votes in bulk at top speed!"),
    ("485 MIL VOTOS", "485k VOTES"),
    ("<strong>485.000 votos manuais</strong> concentraram-se exatamente no intervalo de almoço (12h-13h30)", "<strong>485,000 manual votes</strong> concentrated exactly during the lunch window (12:00-13:30)"),
    ("Em 2018, existiram menos de 180 mil votos em &lt; 10s no país todo (acidentais e dispersos). Em 2026, foram <strong>1.428.650 votos &mdash; 8x MAIOR!</strong>;<br>                     • <strong>Concentração no Nordeste:</strong> Mais de <strong>420.000 votos em esteira</strong> concentrados nas cidades do interior da BA, MA e PE!", "In 2018, there were fewer than 180,000 votes in &lt; 10s across the entire country (incidental and scattered). In 2026, there were <strong>1,428,650 votes &mdash; 8x GREATER!</strong>;<br>                     • <strong>Northeast Concentration:</strong> Over <strong>420,000 queue votes</strong> concentrated in rural municipalities of Bahia, Maranhão, and Pernambuco!"),
    ("8x MAIS VOTOS EM ESTEIRA QUE EM 2018 (SALAS ESVAZIADAS NO ALMOÇO)", "8x MORE QUEUE VOTES THAN 2018 (EMPTY ROOMS AT LUNCH)"),
    ("mais de <strong>1,42 milhão de votos foram teclados sem a presença física de eleitores na cabine</strong>", "over <strong>1.42 million votes were keyed in without the physical presence of voters in the booth</strong>"),
    
    # Slide 16
    ("CLAREZA TOTAL DE QUEM RECEBEU OS VOTOS", "TOTAL CLARITY ON WHO RECEIVED THE TAINTED VOTES"),
    ("15.884.298 Votos", "15,884,298 Votes"),
    ("1.428.650 Votos", "1,428,650 Votes"),
    ("Votos Pró-Lula em 2022", "Votes for Lula in 2022"),
    ("Votos Pró-Lula em 2026", "Votes for Lula in 2026"),
    ("~1.180.000 votos", "~1,180,000 votes"),
    ("1.428.650 votos", "1,428,650 votes"),
    ("~390.000 votos", "~390,000 votes"),
    ("485.000 votos", "485,000 votes"),
    ("2,5M a 3,8M votos", "2.5M to 3.8M votes"),
    ("2,8M a 4,5M votos", "2.8M to 4.5M votes"),
    ("~820.000 votos", "~820,000 votes"),
    ("986.420 votos", "986,420 votes"),
    ("Mesmo operador liberando &gt; 80% das exceções pró-Lula.", "Same worker approving &gt; 80% of overrides for Lula."),
    ("39.652 urnas trocadas (CEFT)", "39,652 swapped machines (CEFT)"),
    ("6. Cidades Votos &gt; Moradores", "6. Towns Votes &gt; Inhabitants"),
    ("106 urnas idênticas", "106 identical machines"),
    ("15.884.298 votos", "15,884,298 votes"),
    ("~4,35M Votos", "~4.35M Votes"),
    ("6,4M a 15,8M Votos", "6.4M to 15.8M Votes"),
    ("15.884.298 votos sem biometria (&gt; 10,8M para Lula) à margem de 4,4M", "15,884,298 non-biometric votes (&gt; 10.8M for Lula) vs 4.4M margin"),
    ("1.428.650 votos em 4 a 6s + 3,8M em rajadas", "1,428,650 votes in 4 to 6s + 3.8M in bursts"),
    
    # Slide 17
    ("5.718 Trocas de Urna em 2026 Decidiram as Eleições", "5,718 Machine Swaps in 2026 Decided the Elections"),
    ("279.336 URNAS ANTIGAS", "279,336 LEGACY MACHINES"),
    ("4,35M de vantagem exclusiva</strong> nessas urnas (o dobro da margem nacional!).", "4.35M exclusive lead</strong> in these machines (double the national margin!)."),
    ("Jair Bolsonaro venceu com 51,05% (+1.070.000 votos)</strong>!", "Jair Bolsonaro won with 51.05% (+1,070,000 votes)</strong>!"),
    ("as trocas de urna foram menores que 0,38% (1.740 urnas normais sem Efeito Espelho). Em 2022, <strong>74,15 milhões de votos</strong> passaram por urnas sem serial individual (+4,35M para Lula). Em 2026, <strong>9,83 milhões de votos</strong> passaram por seções com trocas de urna do CEFT onde o Efeito Espelho transferiu quase meio milhão de votos! Em ambos os pleitos, o vício de retaguarda decidiu a presidência da República!", "machine swaps were below 0.38% (1,740 normal units with zero Mirror Effect). In 2022, <strong>74.15 million votes</strong> passed through machines lacking unique serial IDs (+4.35M for Lula). In 2026, <strong>9.83 million votes</strong> passed through CEFT contingency sections where the Mirror Effect transferred nearly half a million votes! In both elections, backend registry defects decided the presidency!"),
    
    # Slide 18
    ("CONTROLE CIENTÍFICO DA AUDITORIA &bull; ELEIÇÕES PRESIDENCIAIS 2018", "FORENSIC SCIENTIFIC CONTROL GROUP &bull; 2018 PRESIDENTIAL ELECTION"),
    ("Como Opera uma Eleição Limpa: 454 Mil BUs Auditados Comprovando o Padrão de Normalidade", "How a Clean Election Operates: 454k Audited Ballot Reports Proving the Baseline of Normality"),
    ("PLEITO OFICIAL 2018 &bull; BRASIL", "2018 OFFICIAL ELECTION &bull; BRAZIL"),
    ("Fernando Haddad: 44,87% (47.040.906 votos) &bull; Margem: <strong>+10.756.941 votos</strong>", "Fernando Haddad: 44.87% (47,040,906 votes) &bull; Margin: <strong>+10,756,941 votes</strong>"),
    ("📊 <strong>Pesquisas Exatas:</strong> Ibope (54% x 46%) e Datafolha (55% x 45%) cravaram o resultado da urna com precisão cirúrgica.", "📊 <strong>Exact Polls:</strong> Ibope (54% x 46%) and Datafolha (55% x 45%) projected the ballot outcome with surgical accuracy."),
    ("📉 <strong>Comparecimento Natural:</strong> Voters dropped by <strong>-1,43 million voters</strong> in the 2nd round, strictly following historical rules.", "📉 <strong>Natural Turnout:</strong> Voters dropped by <strong>-1.43 million voters</strong> in the 2nd round, strictly following historical rules."),
    ("Bolsonaro: 5.865.357 votos x Haddad: 4.218.202 &bull; <strong>Margem: +1.717.155 votos</strong>", "Bolsonaro: 5,865,357 votes vs Haddad: 4,218,202 &bull; <strong>Margin: +1,717,155 votes</strong>"),
    ("Trocas Residuais:</strong> Menos de 0,35% de urnas trocadas em MG (280 urnas normais sem Efeito Espelho).", "Residual Swaps:</strong> Less than 0.35% machines swapped in MG (280 normal units with zero Mirror Effect)."),
    ("100% do Pleito 229 auditado", "100% of Election 229 audited"),
    ("100% DAS PESQUISAS", "100% OF POLLS"),
    ("comportamento eleitoral que vigorou em todas as eleições democráticas brasileiras (1989, 2002, 2006, 2010 e 2014). Em todas elas, o comparecimento caiu no 2º turno, as pesquisas de véspera foram aderentes e as trocas de urnas foram residuais (< 0,38%). O eleitorado of Brazil não mudou de biologia nem de comportamento em 2026: o que mudou foram as fraturas mecânicas forjadas pelo bolsão de urnas anômalas!", "electoral pattern that governed all Brazilian democratic elections (1989, 2002, 2006, 2010, and 2014). In all of them, 2nd round turnout dropped, pre-election polls were accurate, and machine swaps were residual (< 0.38%). Brazilian voters did not change biology or behavior in 2026: what changed were the mechanical fractures forged inside the anomalous machine pocket!"),
    
    # Slide 19
    ("Baixamos 6 Eleições do CDN Oficial do TSE: Apenas 1989 e 1960 São Plenamente Auditáveis!", "We Downloaded 6 Elections from Official TSE CDN: Only 1989 and 1960 Are Fully Auditable!"),
    ("TABELA DAS 6 ELEIÇÕES HISTÓRICAS E DIAGNÓSTICO DO DATASET", "TABLE OF 6 HISTORICAL ELECTIONS & DATASET AUDIT"),
    ("Pacote entrega só 481k linhas / 20,9M votos (~31% do eleitorado). Não há arquivo presidencial por UF; dados truncados!", "Package delivers only 481k lines / 20.9M votes (~31% of voters). No state-level presidential file; truncated data!"),
    ("Lula 31,08M (46,97%). Margem: 4.014.403 votos.", "Lula 31.08M (46.97%). Margin: 4,014,403 votes."),
    ("Lott 4,55M (44,65%). Margem: 1.089.613 votos.", "Lott 4.55M (44.65%). Margin: 1,089,613 votes."),
    ("AS DUAS ELEIÇÕES PLENAMENTE AUDITÁVEIS (1989 E 1960)", "THE TWO FULLY AUDITABLE ELECTIONS (1989 AND 1960)"),
    ("As Eleições Históricas com Dados Íntegros", "Historical Elections with Intact Data"),
    ("4.014.403 votos (6,06 pp)</strong>. Comparecimento caiu -1,81M de votantes no 2T!;", "4,014,403 votes (6.06 pp)</strong>. Turnout dropped -1.81M voters in 2nd round!;"),
    ("1.089.613 votos (10,70 pp)</strong>;", "1,089,613 votes (10.70 pp)</strong>;"),
    
    # Slide 20
    ("Da Contagem Manual de Cédulas de Papel aos Novos Vetores Digitais da Urna Eletrônica", "From Manual Paper Ballot Tallies to Digital Vectors in Electronic Voting Machines"),
    ("CÉDULA DE PAPEL", "PAPER BALLOT"),
    ("Cédulas pré-marcadas em sacos de lona e rasuras em mapas de apuração cartorária.", "Pre-marked ballots in canvas bags and erasures in registry tally sheets."),
    ("Apuração Lenta:</strong> Counting dragged on for days", "Slow Tallies:</strong> Counting dragged on for days"),
    ("Fraude de Mesa (2026):</strong> 15,88M votos sem biometria e 5.718 trocas CEFT com Efeito Espelho.", "Table Fraud (2026):</strong> 15.88M non-biometric votes and 5,718 CEFT swaps with Mirror Effect."),
    ("A fraude migrou da apuração para a liberação manual", "Fraud migrated from tally counting to manual biometric overrides"),
    ("Na cédula de papel, a fraude ocorria na contagem e nas atas; na urna eletrônica, a fraude migrou para a esteira de liberação de mesários sem biometria", "Under paper ballots, fraud occurred in tallies and sheets; under electronic voting, fraud migrated to non-biometric queues by poll workers"),
    
    # Slide 21
    ("Em 100% das Eleições Desde 1989, Quem Vence em Minas Vence o Brasil", "In 100% of Elections Since 1989, Whoever Wins Minas Wins Brazil"),
    ("49.650 VOTOS (0,40%)", "49,650 VOTES (0.40%)"),
    ("Revertendo o vício das urnas antigas, Bolsonaro vence Minas por <strong>+21.590 votos legítimos</strong>!", "Reversing legacy machine defects, Bolsonaro wins Minas by <strong>+21,590 legitimate votes</strong>!"),
    ("Jair Bolsonaro vence MG por +21.590 votos!", "Jair Bolsonaro wins MG by +21,590 votes!"),
    ("109.313 VOTOS (0,88%)", "109,313 VOTES (0.88%)"),
    ("O Golpe das 5.630 Urnas Trocadas:</strong> Gerou <strong>+96.370 votos para Lula</strong> com o Efeito Espelho;", "The Scam of 5,630 Swapped Machines:</strong> Generated <strong>+96,370 votes for Lula</strong> via Mirror Effect;"),
    ("Revertidas as urnas de contingência manipuladas, Flávio vence MG por <strong>+83.427 votos legítimos</strong>!", "Reversing manipulated contingency machines, Flávio wins MG by <strong>+83,427 legitimate votes</strong>!"),
    ("Flávio Bolsonaro vence MG por +83.427 votos!", "Flávio Bolsonaro wins MG by +83,427 votes!"),
    ("Bolsonaro venceu MG com <strong>58,19% (+1,71M votos)</strong>", "Bolsonaro won MG with <strong>58.19% (+1.71M votes)</strong>"),
    ("Lula venceu por meros <strong>49k (0,40%)</strong>. Nas urnas novas UE2020 de MG, Bolsonaro venceu com 51,81%.", "Lula won by merely <strong>49k (0.40%)</strong>. In modern UE2020 EVMs of MG, Bolsonaro won with 51.81%."),
    ("Lula venceu por <strong>109k (0,88%)</strong>, mas 88% dessa vitória veio das urnas trocadas em campo!", "Lula won by <strong>109k (0.88%)</strong>, but 88% of that margin came from swapped field machines!"),
    ("Aritmeticamente, anular apenas os 109k de Minas deixaria Lula na frente por +4,29M no resto do país (MG isolada não decide o Brasil sozinha). Porém, pericialmente, Minas Gerais é a prova material definitiva: comprovar que 88% da vitória em MG veio de urnas trocadas destrói a presunção de legitimidade da eleição e impõe a extensão da anulação em todo o país!", "Mathematically, annulling MG alone leaves Lula leading by +4.29M elsewhere (MG alone does not decide Brazil). However, forensically, Minas Gerais is definitive material proof: proving that 88% of victory in MG came from swapped machines destroys the presumption of legitimacy and compels nationwide annulment!"),
    
    # Slide 22
    ("O PARQUE DE URNAS DE 2022 (472 MIL EQUIPAMENTOS)", "THE 2022 EVM FLEET (472k MACHINES)"),
    ("Urnas Novas (UE2020) vs Urnas Antigas (Pré-2020) &bull; A Reeleição no Voto Seguro", "Modern EVMs (UE2020) vs Legacy EVMs (Pre-2020) &bull; Reelection in Secure Voting"),
    ("472.075 Urnas", "472,075 EVMs"),
    ("+4,35M votos no bug 1970225", "+4.35M votes in bug 1970225"),
    ("URNAS UE2020 (MODELO NOVO &bull; 193 MIL MÁQUINAS)", "UE2020 EVMs (NEW MODEL &bull; 193k MACHINES)"),
    ("URNAS PRÉ-2020 (MODELOS LEGADOS &bull; 279 MIL MÁQUINAS)", "PRE-2020 EVMs (LEGACY MODELS &bull; 279k MACHINES)"),
    ("3 a 5 pontos percentuais superior</strong> nas urnas UE2020 em comparação com as pré-2020", "3 to 5 percentage points higher</strong> in UE2020 machines compared to pre-2020"),
    ("A CONCLUSÃO INAPELÁVEL (100% LARGURA)", "THE INESCAPABLE CONCLUSION (100% WIDTH)"),
    
    # Slide 23
    ("ELEIÇÃO 2018 (CONTROLE)", "2018 ELECTION (CONTROL)"),
    ("+10.756.941 votos sobre Haddad", "+10,756,941 votes over Haddad"),
    ("com margens limpas aderentes a 100% das pesquisas de véspera.", "with clean margins matching 100% of pre-election polls."),
    ("ELEIÇÃO 2022 (RECALCULADA)", "2022 ELECTION (RECALCULATED)"),
    ("193k Urnas", "193k EVMs"),
    ("ELEIÇÃO 2026 (RECALCULADA)", "2026 ELECTION (RECALCULATED)"),
    ("O CONFRONTO COM AS PESQUISAS ELEITORAIS DE VÉSPERA (2 COLUNAS)", "CONFRONTATION WITH PRE-ELECTION POLLS (2 COLUMNS)"),
    
    # Slide 24
    ("Vício > margem impõe anulação", "Defect > margin compels annulment"),
    ("ELEIÇÃO 2022 (VÍCIO = 2,0x A MARGEM)", "2022 ELECTION (DEFECT = 2.0x MARGIN)"),
    ("ELEIÇÃO 2026 (VÍCIO = 1,5x A 3,6x A MARGEM)", "2026 ELECTION (DEFECT = 1.5x TO 3.6x MARGIN)"),
    ("A BALANÇA DA LEI E O DEVER DE NOVA ELEIÇÃO", "THE SCALES OF LAW & THE DUTY FOR NEW ELECTIONS"),
    ("6,4 milhões em urnas anômalas e 15,88 milhões sem biometria", "6.4 million in anomalous machines and 15.88 million without biometrics"),
    ("1,5x a 3,6x a margem de vitória (4,4 milhões), a eleição está juridicamente contaminada e perde toda a validade!", "1.5x to 3.6x the victory margin (4.4 million), the election is legally contaminated and void!")
]

for s in slides_en:
    vh = s["visual_html"]
    for pt, en in EXACT_REPLACEMENTS:
        vh = vh.replace(pt, en)
    s["visual_html"] = vh

full_json = json.dumps(slides_en, ensure_ascii=False)
full_html = text[:start_idx] + full_json + text[end_idx:]

with open("presentation_slides_en.html", "w", encoding="utf-8") as f:
    f.write(full_html)

with open("comparison_nacional_brasil/presentation_slides_en.html", "w", encoding="utf-8") as f:
    f.write(full_html)

print("Exact residuals replaced successfully!")
