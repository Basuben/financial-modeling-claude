# Traditional modeling vs working with Claude

This page compares two ways of building the same valuation. I have not timed either one, so there are no hours-saved figures here. The comparison is about where the analyst's effort goes.

## The two workflows

| Step | Traditional build | With Claude alongside |
|---|---|---|
| Set up the model | Analyst lays out the sheets, links every cell by hand | Analyst writes the logic in plain English, Claude drafts the structure and formulas, analyst reviews each line |
| Check the arithmetic | Eyeball the balance check, trace precedents | Claude rebuilds the model in a second tool (Python here) and compares every number. This repo does it for 70 cells |
| Test the inputs | Often skipped under deadline | Claude writes screening tests on the source data (balance, cash tie-out, DSO, cash conversion, Beneish) in minutes |
| Run scenarios | Edit inputs, copy values, paste a table | Ask for the sensitivity grid and Claude explains which assumption drives the answer (terminal value is 71% of EV here) |
| Write it up | Analyst drafts the memo after the model is final | Claude drafts the first version of the memo from the outputs, analyst edits and signs |
| Revise after review | Trace the change through every tab | Change an input, rerun the checks, ask Claude what moved and why |

## What changes

The mechanical part of the job (linking cells, formatting, building the grid, first draft of text) gets faster. The analyst's time moves toward the questions only a person can answer: are these growth rates believable, is this WACC defensible, does the story of the company match the numbers.

## What does not change

- The analyst owns every assumption and every number that goes to a client or an investment committee.
- Claude can be wrong. It can pick the wrong formula or misread a sign. That is why this repo has tests, a Python to Excel reconciliation and a balance check, so a person is checking the output and not trusting it.
- Sample data is not real data. Nothing in this repo says anything about a real company.

## A point from fraud work that carries over

Fraud analysts do not trust a file because it looks tidy. They test it. The same habit helps in modeling: if the historical numbers feeding a DCF are inflated, the valuation is wrong however clean the Excel looks. `data/sample_company_financials_flagged.csv` has 350 of invented FY2025 sales booked to receivables. The checks flag it through a 37% jump in DSO and operating cash flow that is only 74% of net income. The Beneish M-score for that year is -1.79, which sits just under the usual -1.78 flag level, so it misses by a hair. I left that in on purpose. No single test catches everything, which is why several are run together.
