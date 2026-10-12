# Integrity check report

Screening tests only. A flag means look closer, not that fraud occurred.

### Clean sample

| FY | balance_ok | cash_ties | re_ok | dso | dso_change | cash_conversion | m_score | red_flags |
|---|---|---|---|---|---|---|---|---|
| 2020 | True | True | True | 44.0 |  | 1.06 |  | 0 |
| 2021 | True | True | True | 46.0 | 0.045 | 0.98 | -2.35 | 0 |
| 2022 | True | True | True | 45.0 | -0.022 | 1.07 | -2.47 | 0 |
| 2023 | True | True | True | 47.0 | 0.044 | 0.98 | -2.34 | 0 |
| 2024 | True | True | True | 45.0 | -0.043 | 1.1 | -2.53 | 0 |
| 2025 | True | True | True | 44.0 | -0.022 | 1.08 | -2.5 | 0 |

### Sample with 350 of invented FY2025 sales

| FY | balance_ok | cash_ties | re_ok | dso | dso_change | cash_conversion | m_score | red_flags |
|---|---|---|---|---|---|---|---|---|
| 2020 | True | True | True | 44.0 |  | 1.06 |  | 0 |
| 2021 | True | True | True | 46.0 | 0.045 | 0.98 | -2.35 | 0 |
| 2022 | True | True | True | 45.0 | -0.022 | 1.07 | -2.47 | 0 |
| 2023 | True | True | True | 47.0 | 0.044 | 0.98 | -2.34 | 0 |
| 2024 | True | True | True | 45.0 | -0.043 | 1.1 | -2.53 | 0 |
| 2025 | True | True | True | 61.5 | 0.367 | 0.74 | -1.79 | 2 |
