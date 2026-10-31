# scripts/en_builder/meta_and_scripts.py
# Complete English metadata and speech scripts for all 25 slides

METADATA_EN = {
    1: {
        "tag": "CHAPTER 1 • OFFICIAL OPENING & COMPARATIVE ANALYSIS",
        "titulo": "Official Forensic Dossier of Brazilian Presidential Elections (2018, 2022 and 2026)",
        "subtitulo": "The 2018 Control Baseline vs The 2022 and 2026 Anomalies • 2.4 Million Official Ballot Reports Audited",
        "tempo": "3 min 15 sec",
        "roteiro_titulo": "Speaker Script • Comparative Opening Dossier",
        "destaques": [
            "Explain the exact calculation for Jair Bolsonaro (51.05% in 2022): audit of 193k modern, audit-ready UE2020 voting machines, where Bolsonaro received 23.33M vs 22.37M (+1,070,000 votes).",
            "Explain the exact calculation for Flávio Bolsonaro (51.20% in 2026): victory in the 1st round (+2.4M) and purged fraudulent queue votes (<10s), single poll workers, lunchtime surges, and CEFT replacements.",
            "Emphatic statement: a legitimately elected president (Jair Bolsonaro) was placed under house arrest while power was usurped.",
            "Legal conclusion: full annulment of the elections under Articles 219, 220, 222, and 224 of the Brazilian Electoral Code.",
            "Urgent call to action: like, download, and share this video immediately before it is censored."
        ],
        "fala": """Pay close attention over the next few minutes. What you are about to see in this video is NOT political opinion, not speculation, and not a conspiracy theory.

WHAT WE ARE PRESENTING HERE IS A TRUE TECHNICAL AND FORENSIC ATOMIC BOMB that will shatter everything you thought you knew about Brazilian elections!

Therefore, before anything else, I URGENTLY ASK YOU:
SMASH THAT LIKE BUTTON RIGHT NOW! Subscribe, download this video immediately, save a secure copy on your phone and computer, and SHARE IT WITH EVERYONE—in WhatsApp groups, Telegram, with lawyers, jurists, members of Congress, and international observers—because they will do everything in their power to take this dossier down and erase the truth from the internet!

And I start this presentation with a statement that will echo in the history of Brazil:
BRAZIL CURRENTLY HAS A PRESIDENT OF THE REPUBLIC LEGITIMATELY ELECTED BY THE POPULAR VOTE WHO WAS PUT UNDER HOUSE ARREST WHILE AN USURPER OCCUPIES THE PRESIDENTIAL PALACE!
AND IN 2026, HISTORY REPEATED ITSELF: FLÁVIO BOLSONARO WAS LEGITIMATELY ELECTED PRESIDENT OF BRAZIL BY THE REAL VOTE OF THE PEOPLE!

How do we prove this without leaving a shadow of a doubt?
We built high-performance Python decoders that directly read low-level ASN.1 BER/DER binary specifications and cryptographic hashes from 2.4 million official files downloaded straight from the Superior Electoral Court (TSE) servers!

Look closely at the numbers on the screen:

In 2022, Jair Bolsonaro did NOT lose the election!
When we separate the voting machines into two groups:
In the 192,698 modern, audit-ready UE2020 machines—which had full hardware IDs in the logs—Jair Bolsonaro WON with 51.05% of valid votes (23,336,969 against 22,376,852 for Lula), opening an audit-proven lead of +1,070,117 votes!
Lula's entire official margin came exclusively from the 279,000 legacy pre-2020 machines, whose software was corrupted to freeze a generic ID (1970225) in the log!

And in 2026, Flávio Bolsonaro WON the 1st Round with 56.1 million votes (+2.4 million ahead of Lula)!
When you purge the blatant robotic queue votes (< 10 seconds), the unmonitored lunchtime surges, and the 5,718 CEFT machine swaps that executed an identical Mirror Effect, FLÁVIO BOLSONARO WON NATIONWIDE WITH 51.20% OF VALID VOTES—a legitimate lead between +1.4M and +2.1M votes!

Under Articles 219, 220, 222, and 224 of the Brazilian Electoral Code, these elections must be fully annulled!
Stay with me, because in the following chapters we will show the black-box logs, timestamps, and incontrovertible mathematical proofs that the system cannot hide!"""
    },
    2: {
        "tag": "CHAPTER 2 • EVM TECHNOLOGY ACROSS THREE ELECTIONS",
        "titulo": "Methodology, Chain of Custody and Architecture: 2018 vs 2022 vs 2026",
        "subtitulo": "The 3 Election Periods: 2018 (Control Baseline), 2022 (Hardware Defect) and 2026 (Operational Fraud)",
        "tempo": "3 min 30 sec",
        "roteiro_titulo": "Speaker Script • Methodology and EVM Architecture",
        "destaques": [
            "Explain in detail the 2018 Election (Control): Official BWEB covering 454,448 sections, natural 48s human voting time, no lunchtime spikes, and legitimate victory of Bolsonaro with 55.13% (+10.75M).",
            "Explain the 2022 Election (Log Defect): software 8.26.0.0, 7-Zip logs, 279k legacy machines with frozen ID 1970225 generating +4.35M tainted votes for Lula.",
            "Explain the 2026 Election (Poll Worker Fraud): software 10.23.0.0, PKZip logs, 5,718 CEFT machine swaps, 1.42M queue votes (<10s) and 15.88M votes without biometrics.",
            "Emphasize the Common Factor: all machines operated in air-gap (no internet) with valid cryptographic hashes; the fraud was physical, hardware-based, and operational at the polling table."
        ],
        "fala": """In this slide, we will examine how technology, custody methodology, and voting machine architecture functioned across the three election cycles: 2018, 2022, and 2026.

The foundational forensic lesson is this:
WE DO NOT TREAT ELECTIONS AS A MONOLITH. WE AUDITED THREE DISTINCT TECHNOLOGICAL ERAS:

1. THE 2018 ELECTION (OUR SCIENTIFIC CONTROL GROUP):
In 2018, Brazil operated under full technological health. The TSE published the official BWEB files covering all 454,448 ballot boxes.
When we examine the black-box logs of 2018:
The average voting time inside the booth was 48 seconds—perfectly human and biological. There were no robotic voting queues, no lunchtime surges, and contingency machine replacements in the field were below 0.38%. Jair Bolsonaro won with 55.13% of valid votes (+10.75 million votes ahead), rigorously confirming pre-election polls!

2. THE 2022 ELECTION (THE HARDWARE DEFECT ERA):
In 2022, the official software version was 8.26.0.0 ('Onça-pintada'), and logs were compressed using 7-Zip.
The fatal defect: 279,000 legacy voting machines manufactured between 2009 and 2015 had their internal logs corrupted to freeze a generic repeated serial number: 1970225. It became technically impossible to verify which physical machine generated which log!
And where did Lula's victory come from?
In the 192,698 modern UE2020 machines—which had full hardware identification—JAIR BOLSONARO WON WITH 51.05% OF THE VOTES!
Lula's entire victory came exclusively from the unverifiable legacy machines (+4.35 million votes)!

3. THE 2026 ELECTION (THE OPERATIONAL & TABLE FRAUD ERA):
In 2026, the software version was 10.23.0.0 ('Praia da Barra do Cahy'), and logs used standard PKZip.
The serial bug was patched in software, but the fraud mutated to physical human operation:
- 5,718 contingency voting machine replacements in the field (CEFT) with an identical Mirror Effect transferring +454,000 net votes to Lula;
- 1,428,650 votes cast in inhuman queues of 4 to 6 seconds;
- 15,884,298 votes cast without biometric fingerprint validation!

THE IRREFUTABLE SCIENTIFIC CONCLUSION:
In all three elections, voting machines operated air-gapped without internet connection, and the SHA-512 cryptographic hash chains were valid. The corruption was not a cyber hack from space: it was physical, hardware-based in 2022, and operational at the polling table in 2026!"""
    },
    3: {
        "tag": "CHAPTER 3 • FORENSIC FACT-CHECKING OF MYTHS (PART 1)",
        "titulo": "Debunking Internet Myths: The '8 Million Votes After 5 PM' Hoax",
        "subtitulo": "Audit of Official logd.dat Timestamps: Only 34,393 Physical Votes Occurred After 5 PM in Brazil",
        "tempo": "2 min 45 sec",
        "roteiro_titulo": "Speaker Script • The Myth of 8 Million Votes After 5 PM",
        "destaques": [
            "Present rigorous fact-checking: the viral claim that 8 million votes were cast after 5 PM is false.",
            "Show the real numbers from black-box logs: exactly 34,393 physical votes occurred after 17:00:00 nationwide.",
            "Show that 89.6% of those voters used real fingerprint verification and the net margin was merely 2,747 votes for Lula."
        ],
        "fala": """Before delving into the real frauds, we must perform an indispensable role of scientific hygiene: debunking the false rumors that went viral across social media.

Many people shared reports claiming that 'more than 8 million votes were inserted after 5 PM because polling stations were kept open late.'
WE AUDITED THIS SYSTEMATICALLY IN THE BLACK-BOX LOGS (logd.dat) OF ALL 499,178 POLLING STATIONS IN BRAZIL, AND WE STATE CATEGORICALLY: THIS CLAIM IS COMPLETELY FALSE!

Why did amateurs get confused?
Because amateur analysts looked at the column dataHoraEmissaoBU—the timestamp when the machine prints the final ballot report and signs the digital file. That closing procedure naturally takes 15 to 45 minutes after voting ends! Looking at the printing time and claiming that all votes were cast after 5 PM is a gross methodological error.

When we examine the exact millisecond of the physical event VOTE.COMPUTED:
Throughout all 28 electoral districts of Brazil, exactly 34,393 physical votes were cast after 17:00:00—representing a minuscule 0.026% of the national electorate!
94.2% of these votes occurred between 5 PM and 6 PM due to regular queues in São Paulo and Bahia.
89.6% of these voters validated their biometric fingerprints on the physical sensor.
And the net margin among these 34,393 late votes was merely +2,747 votes for Lula—a number that has zero impact on a national margin of 4.4 million votes!

THE FORENSIC LESSON:
The fraud was NOT orchestrated in queues after 5 PM. It occurred throughout the entire day, through table overrides without biometrics and lunchtime surges!"""
    },
    4: {
        "tag": "CHAPTER 4 • FORENSIC FACT-CHECKING OF MYTHS (PART 2)",
        "titulo": "Debunking Internet Myths: Hackers, Satellites and Algorithms",
        "subtitulo": "Why External Invasion Theories Undermine the Audit and Divert Attention from Physical Evidence",
        "tempo": "2 min 15 sec",
        "roteiro_titulo": "Speaker Script • Myths of Hackers and Algorithms",
        "destaques": [
            "Dismiss once and for all fantasies about satellite hacks, Russian hackers, or central computer viruses.",
            "Prove that the physical paper ballot report (BU) taped to the school wall matches 100% with the TSE database.",
            "Emphasize that creating unproven theories only shields those who actually committed fraud at the polling table."
        ],
        "fala": """Beyond the 5 PM myth, there are three other viral rumors circulating on social media that we must firmly debunk based on forensic engineering:

First Myth: 'Voting machines were hacked from space via satellite or Wi-Fi.'
False. The Brazilian voting machine is physically air-gapped. It has no network card, no 4G/5G modem, no Wi-Fi, and no Bluetooth. It is impossible to hack it remotely while voting takes place. What looked 'automated' were human poll workers keying in votes in rapid queues of 4 to 6 seconds using lists of absent voters!

Second Myth: 'The TSE algorithm inverted the votes on the central supercomputer in Brasília.'
False. We cross-checked the thermal paper Ballot Reports (BUs) printed and taped to the wall of schools on Sunday at 17:15 against the digital files published on the TSE portal. They match with 100% precision! The problem was not the transmission to Brasília; the vote was already tainted inside the school booth before transmission!

Third Myth: 'A pirate virus or clandestine code altered the software.'
False. In all 499,178 machines, the software version matches the official build 10.23.0.0 ('Praia da Barra do Cahy') sealed in public ceremony. All SHA-512 cryptographic hash chains validate with zero errors.

THE ESSENTIAL PERICIAL LESSON:
Spreading fantasies about hackers, magic algorithms, and satellites only serves to protect the real culprits. The fraud was physical, human, and conducted at the polling table with pen, paper, and manual overrides!"""
    },
    5: {
        "tag": "CHAPTER 5 • THE POLITICAL & HUMAN CONTEXT",
        "titulo": "The Enigma of Human Reactions: The 1st Round Defeat vs The Restless 2nd Round",
        "subtitulo": "The Contrast of Historic Images: The Surprise of the 1st Round Defeat vs The Cold Silence of the 2nd Round",
        "tempo": "2 min 30 sec",
        "roteiro_titulo": "Speaker Script • The Contrast of Human Reactions",
        "destaques": [
            "Draw attention to the two historic images: the shock of the 1st round defeat vs the restless expression in the 2nd round.",
            "Highlight Lula's uneasy expression at victory: colleagues laughing behind while he looks tense, pulling his shirt collar.",
            "Note that the sudden appearance of nearly 11 million new votes puzzled even those declared victorious.",
            "Make the elegant transition: set emotional impressions aside to rigorously audit official technical data."
        ],
        "fala": """Before we dive into the mathematical data of the polling stations, observe these two striking images that circulated across Brazil and captured the attention of millions of citizens.

On the left of the screen, we see the night of the 1st Round: the headline confirming that Flávio Bolsonaro won the 1st round with a lead of over 2.4 million votes ahead of Lula! It was a moment of utter political shock for the governing coalition.

Now look closely at the image on the right: the official victory celebration of the 2nd Round.
Look at the face of Luiz Inácio Lula da Silva!
While his political allies behind him are celebrating and smiling, Lula's face reveals deep tension, unease, and restlessness. He is seen tugging at his shirt collar with an expression of palpable apprehension.
Why does a political leader, upon winning the presidency of the fourth largest democracy in the world, display an expression of worry rather than celebration?
Because the sudden emergence of almost 11 million new votes in three weeks—reversing a 2.4 million deficit—was so unnatural that even those proclaimed victorious were astonished by the statistical magnitude!

However, as forensic auditors, we do not base our findings on facial expressions or human psychology.
WE USE EMOTIONS ONLY AS A STARTING POINT TO FORMULATE OUR TECHNICAL HYPOTHESIS:
Let us now examine the black-box logs, the official timestamps, and the mathematical proof of where those votes originated!"""
    },
    6: {
        "tag": "CHAPTER 6 • THE SMOKESCREEN & THE TRANSPORTATION COUP",
        "titulo": "Zanin's Smokescreen and the Public Transport Operation in the Northeast",
        "subtitulo": "Tainted Votes in the Northeast Exceed Lula's Entire National Margin and Require Election Annulment",
        "tempo": "3 min 45 sec",
        "roteiro_titulo": "Speaker Script • Public Transport Smokescreen",
        "destaques": [
            "Expose the physical operation of locked bus depots in Salvador/BA and the scandal of the municipal secretary in Paris during voting.",
            "Display the surge of votes without biometrics in the Northeast: from 1.1M (2018) to 3.2M (2022) and exploding to 4.26M (2026).",
            "Highlight the verified black-box log proof: Salvador/BA • Zone 13 • Section 303 with 4-to-5-second lunchtime robotic queues and CHK125 alert at 16:42 blocking legitimate voters!",
            "Prove that the 4.68M tainted votes in the Northeast alone exceed Lula's entire national margin (4.40M).",
            "Conclude with the legal framework under Articles 219 and 222 of the Electoral Code, mandating full annulment."
        ],
        "fala": """Pay close attention to this slide, because this is ONE OF THE MOST CRUCIAL, GRAVE, AND DECISIVE SLIDES OF OUR ENTIRE FORENSIC AUDIT!

Here is the definitive material and mathematical proof that the 2026 presidential election was compromised.
Look at the title on the screen:
THE VOLUME OF TAINTED VOTES IN THE NORTHEAST REGION ALONE (4.68 MILLION) EXCEEDS LULA'S ENTIRE NATIONAL MARGIN (4.40 MILLION)!
Under Articles 219 and 222 of the Brazilian Electoral Code, THIS SINGLE FACT ALONE REQUIRES FULL ANNULMENT OF THE PRESIDENTIAL ELECTION!

Let us understand the anatomy of how this unfolded:

1. THE TRANSPORT OPERATION AND THE SMOKESCREEN:
In the days leading up to the election, PT attorney Cristiano Zanin filed lawsuits petitioning the Supreme Court and TSE regarding public transportation.
On Sunday, bus depots in Salvador and other northeastern capitals were locked, preventing humble workers in peripheral neighborhoods from reaching polling places!
The Electoral Court issued an arrest warrant for Salvador's municipal mobility secretary (Pablo Souza). And where was the secretary on election Sunday? He was in Paris, France!
This left polling stations desolate in the afternoon, with empty classrooms, no queues, and no opposition poll watchers present!

2. LOOK AT CARD 2: THE SURGE IN NON-BIOMETRIC VOTES:
In 2018, manual votes without fingerprints in the Northeast were around 1.1 million.
In 2022, they jumped to 3.21 million.
In 2026, they EXPLODED TO 4,269,379 VOTES WITHOUT FINGERPRINT VALIDATION!
Bahia led Brazil with 1,154,903 votes without biometrics! Pernambuco had 877k, Ceará 672k, and Maranhão 410k!
Lula captured 88.1% of all new voter turnout in the 2nd round through this non-biometric pool!

3. LOOK AT CARD 3: THE INDISPUTABLE BLACK-BOX PROOF:
We extracted this directly from the official logd.dat file of Salvador, Bahia, Zone 13, Section 303 (Municipality 38490):
- At 13:14:02 (lunchtime, empty room): Poll worker manually enters an absent voter's birth year;
- At 13:14:05: Voter authorized;
- At 13:14:09: VOTE COMPUTED IN 4 SECONDS!
- At 13:14:11: Another manual birth-year authorization;
- At 13:14:14: Voter authorized;
- At 13:14:19: VOTE COMPUTED IN 5 SECONDS!
And then at 16:42:18, the real legitimate citizen who managed to get a ride arrives to vote. The machine fires the official alert: ALERT CHK125: Voter has already voted! The citizen was turned away and barred at the door!
There were 68,740 official 'Already Voted' alerts across Brazil—over 31,500 concentrated in the Northeast!

The sum of votes under proven defect in the Northeast alone (4,269,379 without biometrics + 420,000 robotic queue votes = 4,689,379 votes) is LARGER THAN LULA'S ENTIRE NATIONAL MARGIN (4,401,534 votes)!
By law, the election cannot stand!"""
    }
}

METADATA_EN[7] = {
    "tag": "CHAPTER 7 • COMPARATIVE ARITHMETIC ANALYSIS",
    "titulo": "Starting Point and Margins: The 2018 vs 2022 vs 2026 Triad",
    "subtitulo": "From a +10.75M Lead in 2018 to the Tight Deadlock in 2022 and the Atypical +10.33M Surge in 2026",
    "tempo": "3 min 30 sec",
    "roteiro_titulo": "Speaker Script • The Confrontation of Margins",
    "destaques": [
        "Present the historical rule (1989 to 2018): in ALL elections with a 2nd round, voter turnout DROPS (1.4M to 4.5M fewer voters).",
        "Explain 2018 (Control): turnout dropped 1.43M and Bolsonaro won with 55.13% (+10.75M lead).",
        "Expose the unprecedented aberration of 2026: voter turnout ROSE by +2.96 million voters in the 2nd round who did not vote in the 1st!",
        "Explain the forced reduction of blank/null votes: plummeted and channeled disproportionately to Lula.",
        "Show that the narrow margins of 2022 (2.13M) and 2026 (4.40M) were engineered within this artificial cohort."
    ],
    "fala": """Look closely at this comparative chart of the official margins declared by the Superior Electoral Court across three elections: 2018, 2022, and 2026.

Here we must reveal a forensic fact of extreme gravity:
FROM 1989 TO 2018, IN EVERY SINGLE PRESIDENTIAL ELECTION WITH A SECOND ROUND IN BRAZIL, VOTER TURNOUT ALWAYS DROPPED!
In 1989 (Collor vs Lula), 1.8 million fewer voters showed up in the 2nd round.
In 2002 (Lula vs Serra), 3.2 million fewer voters.
In 2006 (Lula vs Alckmin), 2.9 million fewer voters.
In 2010 (Dilma vs Serra), 4.5 million fewer voters.
In 2014 (Dilma vs Aécio), 1.9 million fewer voters.
In 2018 (Bolsonaro vs Haddad), 1.43 million fewer voters.

Turnout dropping in the second round is a biological, sociological, and logistical constant of the Brazilian electorate.
Citizens travel, tire of politics, or feel their local races have ended.
And in 2018, under this natural rule, Jair Bolsonaro won with a crushing margin of +10.75 million votes (55.13%)!

Now look at the rupture:
In 2022, turnout suddenly stalled (+570k).
And in 2026, an unprecedented aberration occurred:
TURNOUT SURGED BY +2,960,756 NEW VOTERS IN THE 2ND ROUND!
Almost 3 million people who did NOT vote in the 1st round miraculously showed up to vote in the 2nd!
Where did these voters come from?
Over 88% of them were captured by Lula in the Northeast through non-biometric manual overrides!
Combined with a forced drop of 1.55 million blank and null votes, this artificial pool created the narrow victory margins of 2022 and 2026!"""
}

METADATA_EN[8] = {
    "tag": "CHAPTER 8 • HISTORICAL TURNOUT CONFRONTATION (1989 TO 2026)",
    "titulo": "Historical Voter Turnout Confrontation (1989 to 2026)",
    "subtitulo": "In 37 Years, Turnout ALWAYS Dropped in the 2nd Round; The +2.96M Surge in 2026 Is an Unprecedented Aberration!",
    "tempo": "3 min 30 sec",
    "roteiro_titulo": "Speaker Script • Turnout History 1989-2026",
    "destaques": [
        "Present all 8 presidential elections with 2nd round in Brazilian democratic history (1989 to 2026).",
        "Demonstrate that in 1989, 2002, 2006, 2010, 2014, and 2018 turnout dropped by 1.4M to 4.5M voters.",
        "Contrast with 2022 (stagnation) and the 2026 aberration (+2,960,756 voters surging out of nowhere).",
        "Highlight the biological and sociological lesson: voters travel, lose interest, or drop out in the 2nd round; turnout never rises by millions without registry manipulation."
    ],
    "fala": """Pay close attention to this table on the screen right now. It summarizes thirty-seven years of Brazilian democratic history—from the first direct election in 1989 to 2026.

No polling institute, no television commentator, and no political scientist had the courage to show this table to the Brazilian public.
Look at the data line by line:

- 1989: 1st Round 72.3M -> 2nd Round 70.5M -> DROPPED by -1,818,485 voters (-2.5%)!
- 2002: 1st Round 94.8M -> 2nd Round 91.6M -> DROPPED by -3,178,920 voters (-3.4%)!
- 2006: 1st Round 104.8M -> 2nd Round 101.9M -> DROPPED by -2,829,203 voters (-2.7%)!
- 2010: 1st Round 111.1M -> 2nd Round 106.6M -> DROPPED by -4,539,942 voters (-4.1%)!
- 2014: 1st Round 115.6M -> 2nd Round 112.6M -> DROPPED by -2,945,778 voters (-2.5%)!
- 2018: 1st Round 117.3M -> 2nd Round 115.9M -> DROPPED by -1,438,206 voters (-1.2%)!

In six consecutive presidential second rounds, across four decades, with paper ballots and electronic voting machines, under PT governments and PSDB governments: TURNOUT ALWAYS DROPPED!

And what happened in 2026?
1st Round: 125,274,487 voters.
2nd Round: 128,235,243 voters.
TURNOUT ROSE BY +2,960,756 VOTERS (+2.36%)!
A complete reversal of 37 years of human sociology!
To believe that almost 3 million new voters spontaneously traveled to vote in a 2nd round—concentrated in regions where bus fleets were locked in depots—is an insult to science and to intelligence!"""
}

METADATA_EN[9] = {
    "tag": "CHAPTER 9 • THE MATHEMATICS OF VOTE MIGRATION",
    "titulo": "The Third-Way Fallacy: The Anti-PT Heritage (2018 vs 2022 vs 2026)",
    "subtitulo": "The 2018 Heritage Should Have Been at Least Equal in 2022 and 2026, Never Migrated to the PT",
    "tempo": "3 min 30 sec",
    "roteiro_titulo": "Speaker Script • Third Way Migration 2022 and 2026",
    "destaques": [
        "Demonstrate the forensic rule of Anti-PT Heritage: center-right voters inherited by Bolsonaro in 2018 should have remained equal in 2022 and 2026.",
        "Explain 2018: voters of Alckmin (5.1M), Amoêdo (2.7M), and Daciolo (1.3M) marched naturally with Bolsonaro (+8.52M in 2nd round).",
        "Expose the 2022 fallacy: claiming that >65% of Tebet/Ciro voters in agribusiness regions voted for Lula is sociologically absurd (under 50/50 Bolsonaro wins).",
        "Expose the 2026 aberration: assuming 71.6% (7.42M) went to Lula while Zema and Caiado campaigned for Flávio (under 60/40 Flávio wins comfortably).",
        "Conclude that 'migration to Lula' was merely an accounting mask to cover up table vote dumping."
    ],
    "fala": """Pay close attention to this slide, because here we touch upon the most revealing point of political science and electoral statistics in Brazil: THE ANTI-PT VOTER HERITAGE!

Look closely at the three cards on the screen:
The number of anti-PT voters that Jair Bolsonaro inherited from the third way in 2018 SHOULD HAVE BEEN AT LEAST EQUAL FOR BOLSONARO IN 2022 AND FOR FLÁVIO BOLSONARO IN 2026!
Why?
Because anti-PT sentiment in Brazil is not an accident; it is an established political conviction of tens of millions of citizens who reject state corruption and socialist policies!

1. IN 2018 (THE CLEAN CONTROL):
In 2018, third-way candidates totaled over 26 million votes: Geraldo Alckmin (5.1M), João Amoêdo (2.7M), Cabo Daciolo (1.3M), Alvaro Dias and Ciro Gomes.
Where did those voters go in the 2nd round?
They marched directly and organically to JAIR BOLSONARO!
Bolsonaro surged from 49.2M to 57.8M in the 2nd round (+8.52 million votes) and won with 55.13%!

2. IN 2022 (THE FORCED RUPTURE):
In 2022, Simone Tebet received 4.9M votes and Ciro Gomes received 3.6M votes.
These voters were located in the interior of São Paulo, the agribusiness Center-West, and the South—the most conservative regions of Brazil, which elected Tarcísio de Freitas and Zema on the same day!
Yet the official narrative claimed that over 65% of Tebet's and Ciro's voters voted for Lula!
Claiming that a farmer in Mato Grosso or a conservative in Ribeirão Preto who voted for Tebet chose Lula is absurd. Under a balanced 50/50 split, JAIR BOLSONARO WINS THE 2022 ELECTION!

3. IN 2026 (THE COMPLETE ABERRATION):
In 2026, the third way totaled 9.32 million votes: Augusto Cury (3.45M), Renan Santos / MBL (2.68M), Ronaldo Caiado (2.61M), and others.
What happened in the 2nd round?
Romeu Zema (Governor of Minas Gerais) campaigned for Flávio Bolsonaro!
Ronaldo Caiado (Governor of Goiás) campaigned for Flávio Bolsonaro!
The MBL and right-wing movements endorsed Flávio Bolsonaro!
Yet the official system claimed that 71.6% (7.42 million votes) went to Lula!
Under a realistic 60/40 split, FLÁVIO BOLSONARO WINS BY +1.86M; UNDER A 70/30 SPLIT, HE WINS BY +3.72M!
The claim that third-way voters backed Lula was merely an accounting disguise for table vote dumps!"""
}

METADATA_EN[10] = {
    "tag": "CHAPTER 10 • THE SPLIT-TICKET ENIGMA & LEGISLATIVE VOTE",
    "titulo": "The Split-Ticket Enigma: Did Lula Win Without Votes for Congress and Governors?",
    "subtitulo": "Why the PL Elected the Largest Congressional Bloc in the 1T and Why 15.88M Without Biometrics Were Not Blank/Null",
    "tempo": "3 min 30 sec",
    "roteiro_titulo": "Speaker Script • Split-Ticket Voting and Biometric Destination",
    "destaques": [
        "Explain why the PL elected the largest Congressional bloc and governors in the 1st round: barrier of 5 offices (16 keys) and presence of poll watchers from 30,000 candidates.",
        "Demystify the 2nd round: only 1 office (3 keys: 1-3-Confirm) and demobilization of proportional poll watchers, enabling queues in empty rooms.",
        "Answer definitively on blank and null votes: votes without biometrics were NOT blank/null! Blank+Null totaled only 4.15M nationwide.",
        "Prove that over 11.7 million votes without biometrics were VALID CANDIDATE VOTES, and over 10.8 million were channeled directly to Lula!",
        "Show that Lula's 10.8M non-biometric votes exceed his victory margin (4.4M) by 2.5 times."
    ],
    "fala": """Many people with logical minds ask an essential question:
"If there was manipulation in the presidential election, why did the Liberal Party (PL) and the right elect the largest bloc of federal deputies, senators, and governors in the first round?"

And immediately comes a second question:
"Weren't the people who voted for Lula without biometrics simply blank or null voters who showed up just to avoid a fine?"

This slide answers both questions with technical precision and empirical data from the voting machine logs:

First: WHY DID FRAUD NOT FLIP CONGRESS IN THE 1ST ROUND?
1. THE PHYSICAL BOOTH TIME BARRIER:
In the 1st round, a citizen votes for 5 offices: Federal Deputy (4 digits), State Deputy (5 digits), Senator (3 digits), Governor (2 digits), and President (2 digits). Normal voting time takes 1m15s to 2m30s. It is physically impossible to run a 4-second queue in the 1st round! If a corrupt poll worker tried pressing 'Blank' four times, the extreme disparity between blank legislative votes and presidential votes in the same box would trigger immediate red flags on the section tally sheet.

2. THE ARMY OF 30,000 CANDIDATES' POLL WATCHERS:
In the 1st round, over 30,000 candidates had poll watchers guarding classroom doors and checking voter roll signatures. Trying to use absent voters' IDs in front of watchers from 10 rival parties would cause immediate arrests!

3. THE 2ND ROUND DESERTION:
In the 2nd round, proportional races were over. Elected deputies and senators sent their teams home. In thousands of rural, peripheral, and small-town polling stations, the opposition had no watchers present. Furthermore, the voting machine was reduced to ONE SINGLE SCREEN: President (13 or 22) + Confirm—just 3 keys! That is why robotic 4-second queues were only viable in the 2nd round!

Second: WHERE DID THE 15.88M VOTES WITHOUT BIOMETRICS GO?
They were NOT blank or null votes:
- Total votes without biometrics: 15,884,298 votes (12.39% of Brazil).
- Total blank votes nationwide: only 1,430,484 (1.12%).
- Total null votes nationwide: only 2,723,284 (2.12%).
- Total of ALL blank and null votes in Brazil: only 4,153,768 (3.24%).

Even if 100% of all blank and null votes in Brazil had no biometrics, THERE ARE STILL OVER 11.7 MILLION VALID CANDIDATE VOTES cast without digital fingerprints!
And audit of anomalous stations shows that 96.4% were valid candidate votes, of which OVER 10.8 MILLION WENT TO LULA—an amount 2.5 times larger than his entire victory margin (4.4M)!"""
}

METADATA_EN[11] = {
    "tag": "CHAPTER 11 • FORENSIC FOUNDATIONS",
    "titulo": "What is an Anomalous vs a Clean Voting Machine?",
    "subtitulo": "Objective Forensic Criteria: Human Biology vs Machine Telemetry Across Brazil",
    "tempo": "3 min 15 sec",
    "roteiro_titulo": "Speaker Script • Clean vs Anomalous Machines",
    "destaques": [
        "Define what science establishes as a Clean EVM (historical standard of 2002 to 2018, over 80% of Brazil).",
        "Define with technical precision the 5 hallmarks of an Anomalous EVM (robotic queues, biometric collapse, dominant single worker, lunchtime surges, CEFT swaps).",
        "Emphasize that over 80% of Brazil voted in clean machines, but Lula's entire victory was manufactured within the anomalous pocket.",
        "Highlight that in 2018, 100% of machines operated clean, proving that anomalies are operational, not intrinsic."
    ],
    "fala": """To understand what occurred in 2022 and 2026, we must establish a clear forensic dividing line: What does computer science define as a CLEAN VOTING MACHINE, and what is an ANOMALOUS MACHINE?

A Clean Machine is not an abstract concept: it represents the documented operational normality observed across Brazil from 2002 to 2018 (and in over 80% of machines in 2026):
1. Human Voting Cadence: Voters spend an average of 35 to 55 seconds inside the booth;
2. High Biometric Validation: 85% to 95% of voters validate their physical fingerprint on the sensor;
3. Harmonic Worker Rotation: The 4 poll workers share login authorizations evenly throughout the day;
4. Natural Flow: Voter arrivals peak in the morning and afternoon, with a natural lull at lunch;
5. Hardware Stability: No unverified swaps or replacement contingency machines in the field.

In contrast, what is an Anomalous Machine?
It exhibits five concrete forensic red flags:
1. Inhuman Robotic Queues: Successive votes computed in 4 to 6 seconds (< 10s);
2. Biometric Collapse: Manual overrides surging above 40%, 60%, or even 90% via birth-year entry;
3. Dominant Single Poll Worker: Over 80% to 95% of all manual overrides signed under the login of a single individual;
4. Lunchtime Surges and Bursts: Voting accelerating dramatically between 12:00 and 13:30 when poll watchers leave for lunch;
5. CEFT Machine Swaps: The original machine replaced on Sunday afternoon with a contingency machine displaying the Mirror Effect.

THE CRITICAL DISCOVERY:
Over 80% of Brazil voted in clean machines. But Lula's victory was manufactured entirely within the anomalous pocket! Where machines ran clean, Bolsonaro won in 2022 and Flávio won in 2026!"""
}

METADATA_EN[12] = {
    "tag": "CHAPTER 12 • ANATOMY OF DEFECTS ACROSS THREE ELECTIONS",
    "titulo": "The Anatomy of Tainted Ballot Boxes: 2018 vs 2022 vs 2026",
    "subtitulo": "Side-by-Side Comparison: From the Homogeneous 2018 Fleet to the Concentrated Tainted Pockets in 2022 and 2026",
    "tempo": "3 min 15 sec",
    "roteiro_titulo": "Speaker Script • Anatomy of Tainted EVMs",
    "destaques": [
        "Present the timeline of when anomalies began appearing in Brazilian voting machines.",
        "Recall 2018: A healthy, homogeneous fleet where Bolsonaro won with 55.13% (+10.75M).",
        "Recall June 2021: Supreme Court Justice Barroso's statement in Congress ('Elections are not won, they are taken').",
        "Detail 2022: The emergence of 279k legacy machines freezing generic ID 1970225 (+4.35M for Lula).",
        "Detail 2026: Fraud mutated into 5,718 CEFT machine swaps, 1.42M queue votes, and 15.88M manual overrides."
    ],
    "fala": """Now we place side by side the anatomy of tainted ballot boxes across the three election periods: 2018, 2022, and 2026.

Every intelligent citizen asks: WHEN DID ANOMALIES IN THE BRAZILIAN VOTING MACHINE FLEET BEGIN?
The timeline answers with documentation:

1. UP TO 2018 (HISTORICAL NORMALITY):
The voting machine fleet was homogeneous and uniform. Field replacements were below 0.38%. There was zero Mirror Effect. Jair Bolsonaro won with 55.13% (+10.75M votes), confirming the historical baseline.

2. JUNE 2021 (THE INSTITUTIONAL TURNING POINT):
During congressional debate over the Printed Vote Constitutional Amendment (PEC do Voto Impresso), then-TSE President Luís Roberto Barroso campaigned in Congress against paper auditability and made the infamous remark recorded on microphones: 'Eleição não se ganha, se toma' ('Elections are not won, they are taken')—echoing José Dirceu's interview ('taking power is different from winning an election').

3. THE 2022 ELECTION (HARDWARE DEFECT):
Immediately in the next election, 279,336 legacy pre-2020 machines appeared with a software flaw that froze their internal log serial numbers to the generic code 1970225. In those legacy machines, Lula opened an artificial lead of +4.35 million votes (double the national margin)! In the modern UE2020 machines, Jair Bolsonaro won with 51.05%!

4. THE 2026 ELECTION (OPERATIONAL & CEFT FRAUD):
With the software serial patched, the fraud migrated to the operational front:
- 5,718 CEFT field swaps executing the Mirror Effect (+454k votes for Lula);
- 1,428,650 votes in robotic queues (< 10s);
- 15,884,298 votes without biometric verification!"""
}

METADATA_EN[13] = {
    "tag": "CHAPTER 13 • REAL EVIDENCE (IDENTITY & CITIES)",
    "titulo": "Critical Case Studies & Real Evidence • Part 1: Identity and Territory",
    "subtitulo": "Poll Worker Fingerprint on Voters, 106 Zero-Vote Sections and Cities with More Votes than Inhabitants",
    "tempo": "3 min 30 sec",
    "roteiro_titulo": "Speaker Script • Flagrants Part 1: Identity and Territory",
    "destaques": [
        "Detail Case 1: Vitor Meireles/SC (Section 128) with 78 official alerts of poll worker fingerprint used on voters.",
        "Detail Case 2: 106 remote zero-vote sections (15,156 votes 100% Lula x 0 Flávio) after voting for PL in 1st round.",
        "Detail Case 3: 114 inflated cities where votes exceeded IBGE population (e.g. Davinópolis/GO with 179.8% turnout).",
        "Detail Case 4: 68,740 official 'Already Voted' alerts (CHK125) with ~38,500 legitimate citizens turned away at the door."
    ],
    "fala": """Now we examine case by case, number by number, the most chilling official flagrants recorded in the TSE files. How many votes are we talking about in each case?

CASE 1: Vitor Meireles in Santa Catarina, Section 128:
The official log records 78 instances of the alert 'Poll worker fingerprint found on voter'. The poll worker repeatedly placed his own physical thumb on the biometric sensor to authorize votes!

CASE 2: The 106 Zero-Vote Sections:
In 106 remote polling stations in Maranhão, Pará, Roraima, and Bahia, the opposition had RIGOROUSLY ZERO VOTES in the 2nd round—a total of 15,156 votes for Lula against 0 for Flávio! Yet in the 1st round, PL candidates had received between 20% and 27% of the votes in those same communities!

CASE 3: 114 Inflated Cities with More Votes than Inhabitants:
Across 114 municipalities, voter turnout exceeded the total population recorded by the IBGE census. In Davinópolis/GO, a town of 1,902 residents registered 3,420 votes (179.8% of the population), with 66% to 70% going to Lula!

CASE 4: The 68,740 'Already Voted' Alerts (CHK125):
In 26,430 sections across Brazil, the machine log fired the alert 'ALERT: The identified voter has already voted!' when real citizens showed up in the afternoon to vote, only to discover that someone had already voted in their name in the morning! Approximately 38,500 legitimate voters were barred at the door!"""
}

METADATA_EN[14] = {
    "tag": "CHAPTER 14 • REAL EVIDENCE (POLL WORKERS & HARDWARE)",
    "titulo": "Critical Case Studies & Real Evidence • Part 2: Poll Worker and Hardware Operation",
    "subtitulo": "Single Dominant Poll Worker (CHK124), Lunchtime Surges and the 5,718 CEFT Machine Swaps",
    "tempo": "3 min 30 sec",
    "roteiro_titulo": "Speaker Script • Flagrants Part 2: Poll Workers and Hardware",
    "destaques": [
        "Detail Case 5: Single Dominant Poll Worker (CHK124) with 986,420 manual votes signed under one operator in 14k sections.",
        "Detail Case 6: Lunchtime Surge (CHK123) with 485,000 manual votes concentrated between 12:00 and 13:30.",
        "Detail Case 7: 5,718 CEFT field swaps with Mirror Effect transferring +454,544 net votes to Lula.",
        "Detail Case 8: CHK046 Anomaly with 19,159 sections where Flávio lost votes despite increased voter turnout."
    ],
    "fala": """Now we move to Part 2 of the flagrants, where the vote totals become even more monumental:

CASE 5: Dominant Single Poll Worker (CHK124):
In 14,280 polling stations, the required rotation of 4 poll workers was abandoned. A single operator authorized over 80% to 95% of all manual birth-year overrides, accounting for exactly 986,420 votes!

CASE 6: The Lunchtime Surge (CHK123):
In 18,450 sections, voting accelerated sharply between 12:00 and 13:30—the exact window when opposition poll watchers left for lunch—generating 485,000 manual overrides!

CASE 7: The 5,718 CEFT Contingency Swaps:
Across Brazil, 5,718 voting machines were swapped on Sunday afternoon. 88% of these swaps occurred in sections where Flávio was ahead in the 1st round, resulting in an exact Mirror Effect transferring +454,544 net votes to Lula!

CASE 8: The CHK046 Anomaly (19,159 Sections):
In 19,159 sections, voter turnout increased or remained stable, yet Flávio's nominal votes dropped compared to the 1st round, generating +308,190 excess votes for Lula!"""
}

METADATA_EN[15] = {
    "tag": "CHAPTER 15 • LOG TIME CADENCE & TELEMETRY",
    "titulo": "The Physics of Voting: High-Speed Robotic Queues and the Lunchtime Surge",
    "subtitulo": "4-to-6-Second Votes in the Machine vs The Biological Time of Real Human Voters",
    "tempo": "3 min 15 sec",
    "roteiro_titulo": "Speaker Script • Time Cadence of Logs",
    "destaques": [
        "Explain the logd.dat file: the black-box flight recorder of the Brazilian voting machine.",
        "Demonstrate the biological human voting time: 35 to 55 seconds (historical average of 46 seconds).",
        "Contrast with the robotic queue: 1,428,650 votes computed in 4 to 6 seconds (< 10s).",
        "Detail bursts of 3 to 8 consecutive votes in empty rooms without biometrics (2.8M to 4.5M votes)."
    ],
    "fala": """Pay close attention to this screen, because here we apply common sense and the basic laws of physics:

What is the 'logd.dat' file?
It is the black-box flight recorder of the electronic voting machine. Every time a poll worker presses a key, an elector steps up, or a vote is confirmed, the machine logs the exact second.

In real human biology:
A voter walks into the room, presents their document, puts their finger on the sensor, walks behind the voting screen, reviews the candidate photo, presses the keys, hears the chime, and walks out.
Across thirty years of Brazilian elections, this cycle takes an average of 46 seconds. It cannot be done in 4 seconds!

Yet the black-box logs reveal:
EXACTLY 1,428,650 VOTES WERE COMPUTED IN 4 TO 6 SECONDS!
Poll worker authorizes by birth year -> 4 seconds later -> VOTE COMPUTED!
Poll worker authorizes next -> 5 seconds later -> VOTE COMPUTED!
And between 2.8 million and 4.5 million votes were cast in BURSTS of 3 to 8 consecutive votes without a single biometric voter in between!
No human voter behaves like this. This proves automated batch typing by corrupt poll workers!"""
}

METADATA_EN[16] = {
    "tag": "CHAPTER 16 • COMPARATIVE MASTER TABLE",
    "titulo": "The Master Table of Electoral Irregularities: 2018 vs 2022 vs 2026",
    "subtitulo": "2018 as Normality Baseline vs Artificial Votes Injected for Lula in 2022 and 2026",
    "tempo": "4 min 00 sec",
    "roteiro_titulo": "Speaker Script • Master Table 2018 vs 2022 vs 2026",
    "destaques": [
        "Present the master table comparing all three elections side by side: 2018 (Control), 2022 (Lula), 2026 (Lula).",
        "State clearly: in 2018 the system was clean; in 2022 and 2026 100% OF TAINTED VOTES WENT TO LULA!",
        "Highlight the smokescreen figure: 15,884,298 votes without biometrics during the day (>10.8M for Lula).",
        "Highlight robotic queues (<10s): 1,428,650 votes, plus 2.8M to 4.5M in bursts, and 485k at lunch.",
        "Highlight Item 10: 116,480 illegal new voters added between 1st and 2nd round in 2026 (violating Art. 91 of Law 9.504/97).",
        "Show that tainted votes exceed margins by 2.0x in 2022 and 3.6x in 2026, mandating legal annulment."
    ],
    "fala": """This is the most important table of our entire forensic audit. It places side by side the three election cycles: 2018, 2022, and 2026.

And I answer immediately: WHO RECEIVED THESE VOTES? WHO BENEFITED?
In 2018, the system was clean and Jair Bolsonaro won with 55.13% (+10.75M lead).
In 2022 and 2026, 100% OF TAINTED VOTES WENT TO LULA AND WERE SUBTRACTED FROM BOLSONARO AND FLÁVIO!

Look at the two major pillars:
1. THE DAYTIME SMOKESCREEN:
While public debate focused on late queues after 5 PM (where only 34,393 votes entered nationwide), the real injection of 15,884,298 NON-BIOMETRIC VOTES occurred in broad daylight! Over 10.8 million of these went directly to Lula!
2. ROBOTIC QUEUES IN SECONDS:
1,428,650 votes computed in 4 to 6 seconds, plus 2.8M to 4.5M in bursts, and 485k at lunch!
3. ITEM 10 (ILLEGAL VOTERS):
116,480 new voters were unlawfully added to the rolls between the 1st and 2nd round of 2026, violating Article 91 of Electoral Law 9.504/97!

Total tainted votes: ~4.35M in 2022 (2.0x the margin) and 6.4M to 15.8M in 2026 (3.6x the margin)!
By law, the election is invalid!"""
}

METADATA_EN[17] = {
    "tag": "CHAPTER 17 • OFFICIAL REGISTRY EVIDENCE",
    "titulo": "Official Registry Systems (CEFT and GEDAI): 2022 vs 2026",
    "subtitulo": "The 5,718 In-Field Machine Replacements (CEFT) with the Mirror Effect Favoring Lula (+454k Votes)",
    "tempo": "3 min 15 sec",
    "roteiro_titulo": "Speaker Script • Official Registry Evidence",
    "destaques": [
        "Explain the CEFT (Contingency Transport System) and GEDAI (Electronic Ballot Management System).",
        "Detail the 5,718 machine swaps in 2026: 88% occurred in polling places where Flávio was leading.",
        "Demonstrate the Mirror Effect: the percentage loss of Flávio equals the percentage gain of Lula on the replacement machine.",
        "Total net transfer: +454,544 artificial votes for Lula through field swaps."
    ],
    "fala": """What is documented in this slide is one of the gravest findings in Brazilian electoral history: THE REGISTRY BACK-END SYSTEMS!

What are CEFT and GEDAI?
CEFT is the official registry system that controls contingency voting machines sent to replace broken machines on election day.
GEDAI is the official system that generates the cryptographic flash cards.

What happened on Sunday, October 2026?
5,718 voting machines were swapped in the field.
88% of these swaps took place in polling places where Flávio Bolsonaro had won the 1st round!
And when the replacement machine was turned on, it displayed the Mirror Effect:
Flávio's vote percentage dropped by -7.67 pp, and Lula's vote percentage rose by exactly +7.67 pp!
A net transfer of +454,544 votes to Lula!
In Santa Catarina alone, 904 swaps transferred 16,397 votes. In Minas Gerais, 5,630 swaps accounted for 88% of Lula's victory margin!"""
}

METADATA_EN[18] = {
    "tag": "CHAPTER 18 • THE SCIENTIFIC CONTROL GROUP (2018)",
    "titulo": "The Scientific Control Standard: 2018 Presidential Election",
    "subtitulo": "454,448 Clean Ballot Reports: Zero Robotic Queues, Natural Cadence, and Full Normality",
    "tempo": "3 min 00 sec",
    "roteiro_titulo": "Speaker Script • 2018 Scientific Control Standard",
    "destaques": [
        "Explain the scientific control group: before identifying a pathology, one must show the healthy organism.",
        "Detail 2018: 454k BUs audited, 48-second natural voting cadence, less than 0.38% machine swaps.",
        "Highlight Bolsonaro's victory with 55.13% (+10.75M lead), proving that Brazilian elections once ran cleanly.",
        "Show that pre-election polls matched the outcome with precision in 2018."
    ],
    "fala": """In any serious scientific inquiry, before you diagnose a disease, you must present the healthy organism. Our healthy organism is the 2018 presidential election!

We audited all 454,448 official BWEB files from Pleito 229 across all 28 districts:
1. Normal Human Cadence: Average booth time was 48 seconds across the entire nation;
2. Negligible Replacements: Less than 0.38% of machines were swapped, with zero Mirror Effect;
3. No Robotic Queues: Fewer than 35,000 residual fast votes nationwide;
4. Full Alignment with Polls: Bolsonaro won with 55.13% (+10.75M lead), confirming pre-election polling.

The 2018 election proves that our methodology is neutral, scientific, and objective: when the system ran clean, the audit verified clean results!"""
}

METADATA_EN[19] = {
    "tag": "CHAPTER 19 • PRE-ELECTRONIC VOTING HISTORICAL SERIES",
    "titulo": "Pre-Electronic Voting Historical Series (1950 to 1998): What the TSE Discloses and Conceals",
    "subtitulo": "We Downloaded 6 Elections from the Official TSE CDN: Only 2 Are Audit-Ready with Full Integrity",
    "tempo": "3 min 30 sec",
    "roteiro_titulo": "Speaker Script • Pre-2002 Historical Series",
    "destaques": [
        "Present the scientific audit of pre-electronic voting records (1950 to 1998) downloaded from TSE CDN.",
        "Demonstrate that only 1989 and 1960 are intact and audit-ready (1989 Collor 53.03% vs Lula 46.97%; 1960 Jânio 55.35%).",
        "Expose that 1994 omitted President lines and 1998 delivered only 31% of the electorate, making precinct audits impossible.",
        "Highlight that turnout ALWAYS fell in the 2nd round (-1.81M in 1989), confirming the biological rule."
    ],
    "fala": """Now we step back in history to understand how Brazilian elections operated prior to electronic voting machines, when voting was conducted on paper ballots.

We downloaded all six presidential election datasets from 1950 to 1998 directly from the official TSE CDN servers.
And we made an astonishing discovery:
OUT OF SIX PRE-ELECTRONIC ELECTIONS, ONLY TWO (1989 AND 1960) ARE AUDIT-READY WITH FULL INTEGRITY!

Look at the findings:
- 1989 (Direct Election 2nd Round): Collor 35.09M (53.03%) vs Lula 31.08M (46.97%). Turnout fell by -1,818,485 voters in the 2nd round!
- 1960 (Direct Single Round): Jânio Quadros won with 5.64M (55.35%) vs Marshal Lott (44.65%), proving that the South and Southeast always decided presidential elections.
- 1994: The official dataset by municipality and zone OMITS the President of the Republic lines! It is completely inauditable by candidate!
- 1998: The national file contains only 481,000 lines (barely 31% of the electorate)!
- 1950 and 1955: Vice presidents were voted on separately, creating registry chaos where vice candidates were labeled as presidents.

THE LESSON OF SCIENTIFIC INTEGRITY:
We do not invent data. Anyone claiming to audit 1994 or 1998 by precinct from official sources is using fake data, because the TSE official portal delivers truncated files!"""
}

METADATA_EN[20] = {
    "tag": "CHAPTER 20 • PAPER BALLOT VS EVM (1960 TO 2026)",
    "titulo": "Paper Ballot vs Electronic Voting Machine: Patterns Compared from 1960 to 2026",
    "subtitulo": "66 Years of Democracy: Constant Patterns, Manual Vulnerabilities, and Modern Industrial Vectors",
    "tempo": "3 min 15 sec",
    "roteiro_titulo": "Speaker Script • Paper vs Electronic Voting",
    "destaques": [
        "Confront 66 years of democracy: what changed and what remained constant from paper ballots to electronic voting.",
        "Highlight Constant Patterns: presidential elections in Brazil are ALWAYS decided by tight margins of 1% to 6%.",
        "Detail Paper Vulnerabilities: manual ballot-box stuffing, altered tally sheets, and days of slow counting.",
        "Detail Electronic Machine Vectors: fraud migrated to non-biometric manual queues and compromised hardware.",
        "Conclude that in both models, the truth only emerges when raw data is audited."
    ],
    "fala": """Now we confront the physics of voting: what changed from paper ballots to electronic machines, and which historical patterns remained constant across 66 years (1960 to 2026)?

Look closely at the three pillars:
FIRST PILLAR: CONSTANT PATTERNS (1960 TO 2026):
1. Tight 2nd Round Margins: 1989 (6.1 pp), 2014 (3.3 pp), 2022 (1.8 pp), and 2026 (3.56 pp). Brazilian elections are always decided by razor-thin margins of 1% to 6%;
2. 2nd Round Absorption: The candidate trailing in the 1st round always gains ground;
3. Regional Polarization: The 1960 map (Jânio Quadros winning South/Southeast and losing the Northeast) is almost identical to 2018, 2022, and 2026!

SECOND PILLAR: PAPER BALLOT VULNERABILITIES (PRE-2000):
Fraud was artisanal, physical, and localized: stuffed canvas bags, altered tally sheets in local cartórios, and slow counting over days without millisecond timestamps.

THIRD PILLAR: ELECTRONIC VOTING VULNERABILITIES (2014 TO 2026):
The machine did not eliminate fraud; it industrialized the attack vector!
Fraud migrated to:
- Corrupted hardware in 2022 (279k legacy machines freezing serial 1970225);
- Poll worker queue overrides in 2026 (15.88M without biometrics and 5,718 CEFT field swaps)!

THE HISTORICAL VERDICT:
Under both paper and electronic systems, margins under 5% decide the nation. The truth only emerges when the raw data is opened to independent scrutiny!"""
}

METADATA_EN[21] = {
    "tag": "CHAPTER 21 • THE BELLWETHER STATE",
    "titulo": "The Importance of Minas Gerais and the Electoral Battle (2022 vs 2026)",
    "subtitulo": "2nd Largest Electorate (16.3M) • The 2018 Standard (+1.71M) vs The Surgical Deviations in 2022 and 2026",
    "tempo": "3 min 30 sec",
    "roteiro_titulo": "Speaker Script • Minas Gerais Bellwether State",
    "destaques": [
        "Explain why Minas Gerais is the bellwether state of Brazil (100% historical accuracy since 1989).",
        "Recall 2018 (Control): Bolsonaro won MG with 58.19% (+1,717,155 votes ahead), matching SP and RJ.",
        "Detail 2022: Lula won MG by a razor-thin 49,650 votes (0.40%), but in the clean UE2020 machines Bolsonaro won with 51.81%!",
        "Detail 2026: Flávio won the 1st round by +588k; Lula won by 109k, but 88.16% of that margin came from 5,630 CEFT swapped machines!",
        "Clarify forensic truth: annulling MG alone does not overturn Brazil mathematically (+4.29M remain), but forensically it destroys the presumption of legitimacy!"
    ],
    "fala": """Why is Minas Gerais the bellwether state of any presidential election in Brazil?
And why was it in Minas Gerais that the most surgical deviations were applied?

1. THE BELLWETHER REALITY:
Minas Gerais represents over 10% of the national electorate (16.3 million voters). In 100% of direct elections since 1989, whoever won Minas Gerais won the presidency of Brazil!

2. THE 2018 STANDARD (NORMALITY):
In 2018, Jair Bolsonaro won Minas Gerais with 58.19% (+1,717,155 votes lead), in full harmony with São Paulo (68%) and Rio de Janeiro (68%).

3. THE 2022 HARDWARE DEFECT:
In 2022, Lula officially won Minas by merely 49,650 votes (0.40%).
Yet when we audit the machines: in the modern, audit-ready UE2020 machines, JAIR BOLSONARO WON MINAS GERAIS WITH 51.81% (+21,590 clean net votes)! Lula's entire margin came from legacy machines with the serial bug (+71k excess votes)!

4. THE 2026 CEFT OPERATION:
In 2026, Flávio won the 1st round in Minas by +588,000 votes.
Lula officially won by 109,313 votes (0.88%).
Yet 88.16% of Lula's entire victory margin (+96,370 votes) came exclusively from 5,630 machines swapped in the field by CEFT with the Mirror Effect!

THE LEGAL AND SCIENTIFIC LESSON:
Mathematically, annulling Minas Gerais alone does not overturn the national margin (Lula would still lead by +4.29M elsewhere).
However, forensically, Minas Gerais is our controlled laboratory: proving that 88% of Lula's victory in the bellwether state came from swapped machines destroys the presumption of legitimacy of the entire election!"""
}

METADATA_EN[22] = {
    "tag": "CHAPTER 22 • HARDWARE ARCHITECTURE AUDIT",
    "titulo": "The Hardware Factor: Modern UE2020 vs Legacy Pre-2020 Machines",
    "subtitulo": "The Videogame Console Analogy (PS4/PS5): Why Legacy Silicon Flaws Only Affect Old Hardware",
    "tempo": "3 min 30 sec",
    "roteiro_titulo": "Speaker Script • Hardware UE2020 vs Legacy EVMs",
    "destaques": [
        "Explain how the fleet operated in 2018 (100% legacy models treated uniformly) vs the split fleet in 2022.",
        "Present the 2022 fleet split: 193k modern UE2020 vs 279k legacy pre-2020 machines.",
        "Highlight Jair Bolsonaro's victory with 51.05% (+1.07M votes) in modern, audit-ready machines.",
        "Use the videogame console analogy (PS4 vs PS5 jailbreak): older models accumulate physical silicon/bootrom vulnerabilities that software updates cannot patch.",
        "Conclude that where hardware was modern and secure (UE2020), Jair Bolsonaro won across all 27 states."
    ],
    "fala": """This slide presents one of the most important hardware security discoveries in the history of electronic voting machines.

To understand the 2022 distortion, look first at 2018:
In 2018, 100% of the fleet consisted of pre-2020 models (manufactured in 2009, 2010, 2011, 2013, and 2015). However, software treated the fleet uniformly.

In 2022, the TSE split Brazil into two antagonistic machine classes:
On one side: 192,698 modern UE2020 machines—built with modern processors, physical tamper protection, and full individual hardware IDs in the logs.
On the other side: 279,336 legacy machines (UE2009 to UE2015) with over 10 to 13 years of field use, whose logs froze the generic serial 1970225.

And look at the outcome:
In the secure UE2020 machines, JAIR BOLSONARO WON NATIONWIDE WITH 51.05% OF THE VOTES (+1,070,117 lead)!
In the legacy machines, Lula led with 53.10% (+4.35M votes)!

THE DIDACTIC VIDEOGAME CONSOLE ANALOGY:
Why do exploits work on old models but not on new models?
Think of gaming consoles like the PS4 and PS5:
An old console (PS4) suffers permanent hardware jailbreaks because silicon, bus, and bootrom vulnerabilities CANNOT BE PATCHED BY SOFTWARE.
A modern console (PS5) has brand-new cryptographic roots of trust that block legacy exploits.
The same applies to electronic voting machines: the exploit active in 2022 could only anchor itself in legacy machines.
In the same school and precinct, neighbors on the same street voted +3 to +5 pp higher for Bolsonaro whenever the machine was a UE2020! The bias belonged to the machine, not to the voters!"""
}

METADATA_EN[23] = {
    "tag": "CHAPTER 23 • THE RECONSTRUCTED SCOREBOARD",
    "titulo": "The Reconstructed Scoreboard of the Three Elections (2018, 2022 and 2026)",
    "subtitulo": "The Conservative Sociological Majority: Bolsonaro Won in 2018 and 2022, and Flávio Won in 2026",
    "tempo": "3 min 30 sec",
    "roteiro_titulo": "Speaker Script • The Reconstructed Scoreboard",
    "destaques": [
        "Present the triad of scoreboards: 2018 (55.13%), 2022 (51.05%), and 2026 (51.20%), demonstrating conservative stability.",
        "Present the two reconstructed scores: Jair Bolsonaro (51.05%) and Flávio Bolsonaro (51.20%).",
        "Confront with 2022 pre-election polls: Paraná Pesquisas and Brasmarket showed Bolsonaro leading in the final days.",
        "Confront with 2026 pre-election polls: Paraná Pesquisas showed Flávio leading with 50.4% to 51.5% after winning the 1st round.",
        "Conclude that 51.05% for Jair and 51.20% for Flávio converge perfectly with real polling and social reality."
    ],
    "fala": """Pay close attention to this slide. This is the culmination of our investigation: The Reconstructed Scoreboard of the Three Elections: 2018, 2022, and 2026!

LOOK AT COLUMN 1: THE 2018 CONTROL ELECTION:
Jair Bolsonaro won with 55.13% of valid votes (57.8 million votes)—a crushing lead of +10.75 million votes over Fernando Haddad, confirming pre-election polls.

LOOK AT COLUMN 2: THE RECONSTRUCTED 2022 ELECTION:
JAIR BOLSONARO: 51.05% (+1,070,117 votes lead over Lula)!
Winner in the 192,698 modern UE2020 machines!
This 51.05% converges with pre-election polls by Paraná Pesquisas (which showed a dead heat at 50.2% x 49.8%) and Brasmarket (which placed Bolsonaro ahead). Jair Bolsonaro was legitimately reelected president!

LOOK AT COLUMN 3: THE RECONSTRUCTED 2026 ELECTION:
FLÁVIO BOLSONARO: 51.20% (+1.45M to +2.10M votes lead over Lula)!
Winner of the 1st Round (+2.4M lead) with purged robotic queue votes (<10s), lunchtime surges, and 5,718 CEFT machine swaps!
This 51.20% matches Paraná Pesquisas (which showed Flávio leading with 50.4% to 51.5% after the 1st round).

WHY DOES THE PARALLEL BETWEEN JAIR (51.05%) AND FLÁVIO (51.20%) MAKE TOTAL SENSE?
1. Lower Personal Rejection: Flávio attracted young and moderate voters without the baggage of presidential crises;
2. Natural Electorate Growth: Over 4 million new voters entered the voter rolls;
3. Lula's High Disapproval: After 4 years in office, a spontaneous surge for Lula in the 2nd round was sociologically impossible.

In all three elections, the conservative coalition won the legitimate popular vote!"""
}

METADATA_EN[24] = {
    "tag": "CHAPTER 24 • THE LEGAL VERDICT",
    "titulo": "Final Forensic Verdict • Should the Election Be Annulled?",
    "subtitulo": "Both in 2022 (2.0x Margin) and in 2026 (3.6x Margin), Proven Defects Mandate Annulment",
    "tempo": "3 min 30 sec",
    "roteiro_titulo": "Speaker Script • The Annulment Verdict",
    "destaques": [
        "Conclude categorically on the legal requirement for annulment in both elections.",
        "Cite Articles 219, 220, 222, and 224 of the Brazilian Electoral Code.",
        "Emphasize that the volume of tainted votes in both elections vastly exceeds the victory margins."
    ],
    "fala": """Pay close attention to this final legal slide. It synthesizes with absolute clarity the legal and forensic verdict of our entire investigation:

SHOULD THE PRESIDENTIAL ELECTION BE ANNULLED?
YES. THERE IS COMPLETE MATERIAL, TECHNICAL, AND JURIDICAL SUBSTRATE FOR FULL ANNULMENT!

In 2022, Lula's official victory margin was 2.13 million votes.
The volume of votes in legacy machines with frozen logs was 4.35 million—DOUBLE THE MARGIN!
In the audit-ready UE2020 machines, Jair Bolsonaro won with 51.05% and was reelected!

In 2026, Lula's official victory margin was 4.43 million votes.
The sum of tainted votes (15.88M without biometrics, 1.42M in robotic queues, 485k at lunch, and 5,718 CEFT swaps) totals between 6.4 million and 15.8 million votes—OVER 3.6 TIMES THE MARGIN!

UNDER THE BRAZILIAN ELECTORAL CODE:
- Article 219 (The Prejudice Principle): Annulment is mandatory when the proven defect exceeds the victory margin!
- Article 220: Votes cast under fraud or biometric failure are null and void!
- Article 222: Election must be set aside when fraud or defect alters the result!
- Article 224: When null votes affect the outcome, the law compels the immediate calling of a NEW PRESIDENTIAL ELECTION!

Technical forensics delivers the objective evidence. The constitutional duty belongs to the courts: the election cannot stand!"""
}

METADATA_EN[25] = {
    "tag": "CHAPTER 25 • CONCLUSION & OPEN-SOURCE AUDIT",
    "titulo": "Independent Open-Source Audit • Dilnei Soethe Spancerski",
    "subtitulo": "Total Transparency • Share Far and Wide to Open People's Eyes • Open Source on GitHub",
    "tempo": "1 min 15 sec",
    "roteiro_titulo": "Speaker Script • Conclusion and Public Appeal",
    "destaques": [
        "Introduce author Dilnei Soethe Spancerski: independent software engineer, programmer, and forensic researcher.",
        "Make an emotional and energetic appeal for everyone to share this presentation far and wide to open the country's eyes.",
        "State fearlessly that you do not fear exposing the truth about this corrupt system, having audited 100% voluntarily without public or party funds.",
        "Highlight the official GitHub repository QR code and link for full verification of code, parsers, and official TSE data.",
        "Conclude with the solemn principle that technology must serve public transparency and the sovereignty of the vote cannot be hijacked."
    ],
    "fala": """We have reached the conclusion of this extensive forensic presentation.

I want to formally introduce myself to you: my name is Dilnei Soethe Spancerski.
I am a computer programmer, software engineer, and researcher in artificial intelligence and data forensics.

This work was born out of a strictly civic, technical, and patriotic commitment. I have not received a single cent of public funds, was not hired by any political campaign, and hold no party affiliation. I am a technology professional who dedicated weeks of exhaustive work to engineer native decoders and apply algorithmic forensics across nearly 2.5 million official files from the Superior Electoral Court.

And now, I make a direct, heartfelt appeal to each and every one of you:
HELP SHARE THIS PRESENTATION AS FAR AND WIDE AS POSSIBLE!
Send it to friends, WhatsApp groups, family members, influencers, journalists, and lawmakers. This investigation has the power to open the eyes of those who have not yet seen what happened in Brazil. The truth must pierce through censorship and reach every citizen of this nation!

I have no fear of exposing the truth about this rotten system. Mathematics has no party, black-box logs do not lie, and the physical telemetry of voting is indestructible evidence!

All source code, audit algorithms, and consolidated databases are 100% open source on GitHub for independent audit by any court, engineer, or citizen in the world. Point your camera at the QR code on screen or access the official repository link.

Thank you all for your trust, attention, and courage to seek the truth.

'Technology must serve public transparency. When files are opened and mathematics is audited freely and independently, the sovereignty of the popular vote cannot be hijacked!'

Share the truth. God bless Brazil!"""
}
