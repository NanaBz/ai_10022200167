# Part A — Automated chunking comparison

Generated: `2026-04-21T21:14:54.585642+00:00`

Options: max_queries=all, no_rerank=False


## Configurations

| Config | PDF_CHUNK_CHARS | PDF_CHUNK_OVERLAP |
|--------|-----------------|-------------------|
| **A_baseline** | 1200 | 200 |
| **B_smaller_window** | 800 | 100 |

## Corpus sizes (after chunking)
- **A_baseline**: total chunks = **1309** (`election_csv` = 615, `budget_pdf` = 694)

---

## Retrieval results — `A_baseline`

### Query
In the 2020 results, how many votes did Nana Akufo Addo get in the Ahafo Region?

| Rank | Source | Chunk ID | faiss | rerank | fused | Preview |
|:----:|--------|----------|------:|-------:|------:|---------|
| 1 | `election_csv` | `csv:0` | 0.7122 | 8.0416 | 0.6032 | Year: 2020 | Old Region: Brong Ahafo Region | New Region: Ahafo Region | Code: NPP | Candidate: Nana Akufo Addo | Party: NPP | Votes: 145584 | Votes(%): 55.04% |
| 2 | `election_csv` | `csv:24` | 0.6646 | 7.5237 | 0.5693 | Year: 2020 | Old Region: Brong Ahafo Region | New Region: Bono Region | Code: NPP | Candidate: Nana Akufo Addo | Party: NPP | Votes: 292604 | Votes(%): 58.23% |
| 3 | `election_csv` | `csv:36` | 0.6885 | 7.1735 | 0.5821 | Year: 2020 | Old Region: Brong Ahafo Region | New Region: Bono East Region | Code: NPP | Candidate: Nana Akufo Addo | Party: NPP | Votes: 199720 | Votes(%): 42… |
| 4 | `election_csv` | `csv:144` | 0.7074 | 7.0309 | 0.5843 | Year: 2020 | Old Region: Upper West Region | New Region: Upper West Region | Code: NPP | Candidate: Nana Akufo Addo | Party: NPP | Votes: 121230 | Votes(%): 32… |
| 5 | `election_csv` | `csv:96` | 0.6925 | 7.0195 | 0.5774 | Year: 2020 | Old Region: Northern Region | New Region: Northern Region | Code: NPP | Candidate: Nana Akufo Addo | Party: NPP | Votes: 409063 | Votes(%): 45.61% |
| 6 | `election_csv` | `csv:168` | 0.7127 | 6.9255 | 0.5905 | Year: 2020 | Old Region: Western Region | New Region: Western Region | Code: NPP | Candidate: Nana Akufo Addo | Party: NPP | Votes: 439724 | Votes(%): 50.93% |


### Query
What does the 2025 budget say about revenue or tax policy?

| Rank | Source | Chunk ID | faiss | rerank | fused | Preview |
|:----:|--------|----------|------:|-------:|------:|---------|
| 1 | `budget_pdf` | `pdf:144` | 0.4875 | 2.611 | 0.3883 | s consistent with our resolve to protect the poor and the vulnerable. 262. Mr. Speaker, to improve revenue mobilisation, the implementation of the following ex… |
| 2 | `budget_pdf` | `pdf:213` | 0.5842 | 1.754 | 0.4587 | in securing about $900million from the Fund to support economic reforms; concluded the external debt restructuring programme with Official Creditor Committee a… |
| 3 | `budget_pdf` | `pdf:171` | 0.6436 | 1.587 | 0.4911 | e Fiscal Responsibility Act, 2018 (Act 982), programmed to be enacted by Parliament alongside the approval of this budget, to include a debt rule and legislate… |
| 4 | `budget_pdf` | `pdf:23` | 0.5539 | 1.2875 | 0.426 | se the Budget Statement and Economic Policy of Government for the 2025 Financial Year. 2. Today marks a moment of great significance and I have the singular ho… |
| 5 | `budget_pdf` | `pdf:525` | 0.4996 | 0.2079 | 0.3787 | 2025 Budget 187 Appendix 7B: Non -Tax Revenue / Internally Generated Funds (NTR/IGF) 2024 Proj Vs Actuals and 2025 Projections (GH¢'000) Capped Retention (%) C… |
| 6 | `budget_pdf` | `pdf:173` | 0.6535 | -0.3446 | 0.4912 | P in 2024 to 4.1 percent of GDP in 2025 and improve further to 0.7 percent of GDP by 2028 as shown in Table 35. Table 38: Summary of Central Government Fiscal … |


### Query
Who won the presidential election?

| Rank | Source | Chunk ID | faiss | rerank | fused | Preview |
|:----:|--------|----------|------:|-------:|------:|---------|
| 1 | `election_csv` | `csv:613` | 0.6216 | -8.2168 | 0.434 | Year: 1992 | Old Region: Western Region | New Region: Western Region | Code: NDC | Candidate: Jerry John Rawlings | Party: NDC | Votes: 239477 | Votes(%): 60.7… |
| 2 | `election_csv` | `csv:595` | 0.6201 | -8.4079 | 0.4331 | Year: 1992 | Old Region: Eastern Region | New Region: Eastern Region | Code: NDC | Candidate: Jerry John Rawlings | Party: NDC | Votes: 240076 | Votes(%): 52.6… |
| 3 | `election_csv` | `csv:601` | 0.6303 | -8.4403 | 0.4397 | Year: 1992 | Old Region: Northern Region | New Region: Northern Region | Code: NDC | Candidate: Jerry John Rawlings | Party: NDC | Votes: 203004 | Votes(%): 62… |
| 4 | `election_csv` | `csv:592` | 0.5998 | -8.4891 | 0.4199 | Year: 1992 | Old Region: Central Region | New Region: Central Region | Code: NDC | Candidate: Jerry John Rawlings | Party: NDC | Votes: 222092 | Votes(%): 66.4… |
| 5 | `election_csv` | `csv:607` | 0.6044 | -8.7306 | 0.4228 | Year: 1992 | Old Region: Upper West Region | New Region: Upper West Region | Code: NDC | Candidate: Jerry John Rawlings | Party: NDC | Votes: 66049 | Votes(%):… |
| 6 | `election_csv` | `csv:604` | 0.6026 | -8.7775 | 0.4217 | Year: 1992 | Old Region: Upper East Region | New Region: Upper East Region | Code: NDC | Candidate: Jerry John Rawlings | Party: NDC | Votes: 108999 | Votes(%)… |


### Query
What is the fiscal deficit outlook mentioned in the budget?

| Rank | Source | Chunk ID | faiss | rerank | fused | Preview |
|:----:|--------|----------|------:|-------:|------:|---------|
| 1 | `budget_pdf` | `pdf:74` | 0.6778 | -2.6921 | 0.5009 | 2,529 million (4.2% of GDP). The corresponding primary balance was a deficit of GH¢45,855 million (3.9% of GDP) against a surplus target of GH¢5,469 million (0… |
| 2 | `budget_pdf` | `pdf:72` | 0.6503 | -4.0009 | 0.494 | ernment’s recapitalisation to date is GH¢1.6 billion. 2024 Fiscal Performance 115. Mr. Speaker, I will now update the House on fiscal performance for the 2024 … |
| 3 | `budget_pdf` | `pdf:155` | 0.536 | -4.6841 | 0.4294 | ource allocations for the 2025 fiscal year, the total appropriation for the year ending 31st December 2025 is GH¢290,971,212,435. Figure 12: 2025 Resource Allo… |
| 4 | `budget_pdf` | `pdf:173` | 0.6232 | -4.7882 | 0.4834 | P in 2024 to 4.1 percent of GDP in 2025 and improve further to 0.7 percent of GDP by 2028 as shown in Table 35. Table 38: Summary of Central Government Fiscal … |
| 5 | `budget_pdf` | `pdf:132` | 0.5521 | -4.8337 | 0.4245 | ne leave the Sinking Fund empty, if not because you have no intention to repay your debts? Or to kick the can down the road for the next government to inherit.… |
| 6 | `budget_pdf` | `pdf:73` | 0.5673 | -5.0708 | 0.4386 | DP against a target of 5.3%; and iv. revenue exceeded the target by 5.3% (GH¢9.4 billion) whilst Expenditures (commitment) surpassed the target by 27.1% (GH¢59… |


### Query
Compare NPP and NDC votes for the Ahafo Region in 2020.

| Rank | Source | Chunk ID | faiss | rerank | fused | Preview |
|:----:|--------|----------|------:|-------:|------:|---------|
| 1 | `election_csv` | `csv:0` | 0.6096 | 7.0134 | 0.5151 | Year: 2020 | Old Region: Brong Ahafo Region | New Region: Ahafo Region | Code: NPP | Candidate: Nana Akufo Addo | Party: NPP | Votes: 145584 | Votes(%): 55.04% |
| 2 | `election_csv` | `csv:37` | 0.6307 | 6.5204 | 0.5242 | Year: 2020 | Old Region: Brong Ahafo Region | New Region: Bono East Region | Code: NDC | Candidate: John Dramani Mahama | Party: NDC | Votes: 265728 | Votes(%)… |
| 3 | `election_csv` | `csv:25` | 0.6199 | 6.4479 | 0.5194 | Year: 2020 | Old Region: Brong Ahafo Region | New Region: Bono Region | Code: NDC | Candidate: John Dramani Mahama | Party: NDC | Votes: 203279 | Votes(%): 40.… |
| 4 | `election_csv` | `csv:36` | 0.6266 | 6.2685 | 0.5215 | Year: 2020 | Old Region: Brong Ahafo Region | New Region: Bono East Region | Code: NPP | Candidate: Nana Akufo Addo | Party: NPP | Votes: 199720 | Votes(%): 42… |
| 5 | `election_csv` | `csv:144` | 0.6388 | 4.7579 | 0.5163 | Year: 2020 | Old Region: Upper West Region | New Region: Upper West Region | Code: NPP | Candidate: Nana Akufo Addo | Party: NPP | Votes: 121230 | Votes(%): 32… |
| 6 | `election_csv` | `csv:84` | 0.6525 | 4.754 | 0.5233 | Year: 2020 | Old Region: Northern Region | New Region: North East Region | Code: NPP | Candidate: Nana Akufo Addo | Party: NPP | Votes: 122742 | Votes(%): 51.3… |

- **B_smaller_window**: total chunks = **1606** (`election_csv` = 615, `budget_pdf` = 991)

---

## Retrieval results — `B_smaller_window`

### Query
In the 2020 results, how many votes did Nana Akufo Addo get in the Ahafo Region?

| Rank | Source | Chunk ID | faiss | rerank | fused | Preview |
|:----:|--------|----------|------:|-------:|------:|---------|
| 1 | `election_csv` | `csv:0` | 0.7122 | 8.0416 | 0.6032 | Year: 2020 | Old Region: Brong Ahafo Region | New Region: Ahafo Region | Code: NPP | Candidate: Nana Akufo Addo | Party: NPP | Votes: 145584 | Votes(%): 55.04% |
| 2 | `election_csv` | `csv:24` | 0.6646 | 7.5237 | 0.5693 | Year: 2020 | Old Region: Brong Ahafo Region | New Region: Bono Region | Code: NPP | Candidate: Nana Akufo Addo | Party: NPP | Votes: 292604 | Votes(%): 58.23% |
| 3 | `election_csv` | `csv:36` | 0.6885 | 7.1735 | 0.5821 | Year: 2020 | Old Region: Brong Ahafo Region | New Region: Bono East Region | Code: NPP | Candidate: Nana Akufo Addo | Party: NPP | Votes: 199720 | Votes(%): 42… |
| 4 | `election_csv` | `csv:144` | 0.7074 | 7.0309 | 0.5843 | Year: 2020 | Old Region: Upper West Region | New Region: Upper West Region | Code: NPP | Candidate: Nana Akufo Addo | Party: NPP | Votes: 121230 | Votes(%): 32… |
| 5 | `election_csv` | `csv:96` | 0.6925 | 7.0195 | 0.5774 | Year: 2020 | Old Region: Northern Region | New Region: Northern Region | Code: NPP | Candidate: Nana Akufo Addo | Party: NPP | Votes: 409063 | Votes(%): 45.61% |
| 6 | `election_csv` | `csv:168` | 0.7127 | 6.9255 | 0.5905 | Year: 2020 | Old Region: Western Region | New Region: Western Region | Code: NPP | Candidate: Nana Akufo Addo | Party: NPP | Votes: 439724 | Votes(%): 50.93% |


### Query
What does the 2025 budget say about revenue or tax policy?

| Rank | Source | Chunk ID | faiss | rerank | fused | Preview |
|:----:|--------|----------|------:|-------:|------:|---------|
| 1 | `budget_pdf` | `pdf:202` | 0.6953 | 2.8699 | 0.5159 | to some ceramic companies through the Discounted Industrial Development Tariff (DIDT) will be reversed to the current WACOG. 2025 Revenue Measures 255. Mr. Spe… |
| 2 | `budget_pdf` | `pdf:245` | 0.6172 | 1.956 | 0.4805 | percent by 2028. This steady improvement will be driven by a mix of tax policy measures, strengthened revenue administration, and an improvement in collection … |
| 3 | `budget_pdf` | `pdf:206` | 0.5875 | 0.8474 | 0.4521 | ned in 2025: i. the Modified Taxation System. Government will roll out digitized systems to capture details of eligible taxpayers, submission of returns and a … |
| 4 | `budget_pdf` | `pdf:244` | 0.6181 | 0.793 | 0.4805 | d beyond. This commitment underscores our resolve to ensure debt sustainability, and create the fiscal space needed for long-term economic growth. 345. Mr. Spe… |
| 5 | `budget_pdf` | `pdf:205` | 0.5973 | 0.5855 | 0.4591 | ng business at the Ports by conducting a review of all the taxes, fees and charges with the objective of removing those that are inimical to importers. 260. Mr… |
| 6 | `budget_pdf` | `pdf:750` | 0.4996 | 0.0701 | 0.3821 | 2025 Budget 187 Appendix 7B: Non -Tax Revenue / Internally Generated Funds (NTR/IGF) 2024 Proj Vs Actuals and 2025 Projections (GH¢'000) Capped Retention (%) C… |


### Query
Who won the presidential election?

| Rank | Source | Chunk ID | faiss | rerank | fused | Preview |
|:----:|--------|----------|------:|-------:|------:|---------|
| 1 | `election_csv` | `csv:613` | 0.6216 | -8.2168 | 0.434 | Year: 1992 | Old Region: Western Region | New Region: Western Region | Code: NDC | Candidate: Jerry John Rawlings | Party: NDC | Votes: 239477 | Votes(%): 60.7… |
| 2 | `election_csv` | `csv:595` | 0.6201 | -8.4079 | 0.4331 | Year: 1992 | Old Region: Eastern Region | New Region: Eastern Region | Code: NDC | Candidate: Jerry John Rawlings | Party: NDC | Votes: 240076 | Votes(%): 52.6… |
| 3 | `election_csv` | `csv:601` | 0.6303 | -8.4403 | 0.4397 | Year: 1992 | Old Region: Northern Region | New Region: Northern Region | Code: NDC | Candidate: Jerry John Rawlings | Party: NDC | Votes: 203004 | Votes(%): 62… |
| 4 | `election_csv` | `csv:592` | 0.5998 | -8.4891 | 0.4199 | Year: 1992 | Old Region: Central Region | New Region: Central Region | Code: NDC | Candidate: Jerry John Rawlings | Party: NDC | Votes: 222092 | Votes(%): 66.4… |
| 5 | `election_csv` | `csv:607` | 0.6044 | -8.7306 | 0.4228 | Year: 1992 | Old Region: Upper West Region | New Region: Upper West Region | Code: NDC | Candidate: Jerry John Rawlings | Party: NDC | Votes: 66049 | Votes(%):… |
| 6 | `election_csv` | `csv:604` | 0.6026 | -8.7775 | 0.4217 | Year: 1992 | Old Region: Upper East Region | New Region: Upper East Region | Code: NDC | Candidate: Jerry John Rawlings | Party: NDC | Votes: 108999 | Votes(%)… |


### Query
What is the fiscal deficit outlook mentioned in the budget?

| Rank | Source | Chunk ID | faiss | rerank | fused | Preview |
|:----:|--------|----------|------:|-------:|------:|---------|
| 1 | `budget_pdf` | `pdf:247` | 0.5828 | -0.4974 | 0.4624 | ilarly, the overall fiscal balance (cash) is expected to improve from a deficit of 5.2 percent of GDP in 2024 to 4.1 percent of GDP in 2025 and improve further… |
| 2 | `budget_pdf` | `pdf:106` | 0.6579 | -0.7946 | 0.4915 | overall Fiscal Balance was a deficit of GH¢6 1,411 million (5.2% of GDP) against the target of GH¢54,142 million (5.3% of GDP). The corresponding primary balan… |
| 3 | `budget_pdf` | `pdf:104` | 0.6144 | -1.4382 | 0.476 | deficit of 0.6%; iii. the overall fiscal balance (Commitment) for 2024 was a deficit of 7.9% of GDP against a target deficit of 4.2% whilst the Overall Fiscal … |
| 4 | `budget_pdf` | `pdf:246` | 0.6133 | -1.9634 | 0.4829 | hana We Want 2025 Budget 66 349. Mr. Speaker, the primary expenditure is projected to rise modestly to 15.4 percent of GDP by 2028, ensuring adequate resources… |
| 5 | `budget_pdf` | `pdf:103` | 0.6357 | -3.0256 | 0.4887 | ll now update the House on fiscal performance for the 2024 financial year. 116. Mr. Speaker, the fiscal performance in 2024 was characterized by robust revenue… |
| 6 | `budget_pdf` | `pdf:105` | 0.6608 | -3.9345 | 0.4991 | 0. 2% in 2023 to a deficit of 3.9% of GDP in 2024. The same trend was observed for the overall fiscal balance. 118. Mr. Speaker, Total Revenue and Grants was G… |


### Query
Compare NPP and NDC votes for the Ahafo Region in 2020.

| Rank | Source | Chunk ID | faiss | rerank | fused | Preview |
|:----:|--------|----------|------:|-------:|------:|---------|
| 1 | `election_csv` | `csv:0` | 0.6096 | 7.0134 | 0.5151 | Year: 2020 | Old Region: Brong Ahafo Region | New Region: Ahafo Region | Code: NPP | Candidate: Nana Akufo Addo | Party: NPP | Votes: 145584 | Votes(%): 55.04% |
| 2 | `election_csv` | `csv:37` | 0.6307 | 6.5204 | 0.5242 | Year: 2020 | Old Region: Brong Ahafo Region | New Region: Bono East Region | Code: NDC | Candidate: John Dramani Mahama | Party: NDC | Votes: 265728 | Votes(%)… |
| 3 | `election_csv` | `csv:25` | 0.6199 | 6.4479 | 0.5194 | Year: 2020 | Old Region: Brong Ahafo Region | New Region: Bono Region | Code: NDC | Candidate: John Dramani Mahama | Party: NDC | Votes: 203279 | Votes(%): 40.… |
| 4 | `election_csv` | `csv:36` | 0.6266 | 6.2685 | 0.5215 | Year: 2020 | Old Region: Brong Ahafo Region | New Region: Bono East Region | Code: NPP | Candidate: Nana Akufo Addo | Party: NPP | Votes: 199720 | Votes(%): 42… |
| 5 | `election_csv` | `csv:144` | 0.6388 | 4.7579 | 0.5163 | Year: 2020 | Old Region: Upper West Region | New Region: Upper West Region | Code: NPP | Candidate: Nana Akufo Addo | Party: NPP | Votes: 121230 | Votes(%): 32… |
| 6 | `election_csv` | `csv:84` | 0.6525 | 4.754 | 0.5233 | Year: 2020 | Old Region: Northern Region | New Region: North East Region | Code: NPP | Candidate: Nana Akufo Addo | Party: NPP | Votes: 122742 | Votes(%): 51.3… |


---

*Automated run complete. Pair with UI screenshots (Figure A1/A2).*