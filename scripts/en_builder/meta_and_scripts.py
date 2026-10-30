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
