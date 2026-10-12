# Prompts that fit an analyst's day

These are the kinds of requests I would give Claude on a deal. Replace the brackets with your own details. Always read what comes back and check the numbers yourself.

## Build

1. "Here are five years of income statement, balance sheet and cash flow data. Build a three statement projection for five years using these drivers: [growth, margins, DSO, DIO, DPO, capex, tax]. Make the balance sheet balance and show me the check line."
2. "Turn the projection into a DCF with end of year discounting, a terminal growth rate and a WACC by growth sensitivity grid. Use formulas, no hard coded results."

## Check

3. "Audit this model. List every hard coded number sitting inside a formula, every sign that looks wrong, and every cell where the units change."
4. "Rebuild the DCF independently in Python and compare it with the workbook cell by cell. Tell me which cells differ and by how much."
5. "Run screening tests on the historical statements: balance, cash tie-out, receivable days, cash conversion, Beneish M-score. Tell me which years look odd and what to ask management."

## Explain

6. "Which assumption moves enterprise value the most? Give me the sensitivity and one paragraph I can say out loud to a managing director."
7. "Terminal value is more than 70% of enterprise value. Write three sentences on why that matters and what I should show next to the DCF."

## Write

8. "Draft a one page valuation memo from these outputs: business in two lines, method, football field, key risks, what would change the range. Plain language, no filler."
9. "List ten questions a skeptical committee member would ask about this valuation, and my best answer to each."

## Review

10. "Here is my draft. Mark anything that claims more than the numbers support."
