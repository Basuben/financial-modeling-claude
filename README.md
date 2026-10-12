# Financial Modeling with Claude: a valuation workflow on sample data

A small, complete valuation of a made-up company, Savanna Foods Ltd, built to show how an analyst can work with Claude instead of building every model line by hand. It covers a three statement projection, a DCF, a sensitivity grid, trading comps, a football field, and a set of checks on the source data.

Everything here is **sample data**. The company and its peers are fictional, and nothing in this repo describes a real business. Amounts are in KES millions.

## What is in it

| Piece | What it does |
|---|---|
| `scripts/make_sample_data.py` | Generates six years of linked statements (FY2020 to FY2025) plus a second version with 350 of invented FY2025 sales |
| `src/model.py` | Five year projection with a balancing balance sheet, DCF, WACC by growth sensitivity, comps, football field |
| `src/integrity_checks.py` | Balance, cash tie-out, retained earnings roll, receivable days, cash conversion, Beneish M-score |
| `scripts/build_excel.py` | Builds an Excel workbook with live formulas, so the analyst can change an input and watch it flow through |
| `scripts/verify_excel.py` | Recalculates the workbook in LibreOffice and compares 70 cells with the Python model |
| `tests/` | Nine tests covering the maths, the sensitivity direction and the fraud checks |
| `docs/` | Traditional vs Claude comparison and a prompt list for an analyst's day |
| `outputs/` | Valuation summary and integrity report |

The Excel workbook itself is not stored in the repo. Run `python scripts/build_excel.py` to create it.

## Results on the sample data

| | |
|---|---|
| Enterprise value (WACC 13%, g 5%) | KES 9,053m |
| Net cash | KES 538m |
| Equity value | KES 9,590m |
| Value per share | KES 95.90 |
| Terminal value as a share of EV | 71% |

Peers trade at a median 7.0x EV/EBITDA, which puts the comps range at KES 95.5 to 100.0 a share. The DCF range across WACC and growth is KES 82.4 to 115.5. See [`outputs/valuation_summary.md`](outputs/valuation_summary.md) for the full tables.

The terminal value share is the point to watch. Over 70% of the value sits beyond the forecast, so a small change in WACC or growth moves the answer a lot.

## How Claude changes the work

The short version, with the longer one in [`docs/traditional-vs-claude.md`](docs/traditional-vs-claude.md):

- **Building.** The structure and formulas come from a plain English description of the logic, and the analyst reviews them. The linking and formatting is where hand building eats time.
- **Checking.** Claude rebuilds the model in a second tool and compares it cell by cell. Here the Excel workbook and the Python model agree on 70 cells. A second build is something most deadlines never allow when done by hand.
- **Testing the inputs.** A valuation is only as good as the history behind it. The checks catch invented sales in the flagged file through a 37% jump in receivable days and operating cash flow at 74% of net income.
- **Explaining and writing.** Sensitivity commentary and a first draft of the memo come out of the same numbers.

What stays with the analyst: the assumptions, the judgment on whether they are believable, and every number that leaves the building. Claude can be wrong, which is why the repo carries tests and a reconciliation.

I did not time either workflow, so this repo makes no hours saved claim.

## Run it

```bash
pip install -r requirements.txt
python scripts/make_sample_data.py      # regenerate the CSVs (optional, they are included)
python -m pytest                        # 9 tests
python src/report.py                    # writes outputs/valuation_summary.md
python src/integrity_checks.py          # writes outputs/integrity_report.md
python scripts/build_excel.py           # writes outputs/savanna_foods_model.xlsx
python scripts/verify_excel.py          # needs LibreOffice, compares Excel to Python
```

Blue cells in the workbook are inputs. Change WACC, growth or margins on the Assumptions sheet and everything else recalculates.

## Limits worth knowing

- The model is deliberately simple: one debt tranche, no interest on cash, no leases, no share count changes, end of year discounting.
- The Beneish M-score is a screening tool built on a US sample. A flag means look closer. A clean score does not prove clean books. In the flagged file the M-score for FY2025 is -1.79, just under the usual -1.78 cut off, so the receivable days and cash conversion tests did the catching, not the M-score.
- The peers are invented, so the multiples say nothing about real market pricing.
- The forecast assumptions are mine and are not tied to a view on any market.

## About

Built by Collins Basuben, a fraud analyst in Nairobi with a BSc in Finance and a CPA Foundation qualification, working toward CISA, CAMS and CFE. The aim of this project is to join two skills: valuing a business and testing whether the numbers behind it can be trusted. See also my [transaction monitoring project](https://github.com/Basuben/transaction-monitoring-fraud-detection) and my [loan underwriting demo](https://github.com/Basuben/ujima-sacco-ai-pride).
