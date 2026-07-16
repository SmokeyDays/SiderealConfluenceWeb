# Table 3. Self-play terminal-score statistics

| Model / baseline | Mean score | Std. | Min | Max | 95% bootstrap CI |
| --- | --- | --- | --- | --- | --- |
| Doubao Seed 2.0 Pro | 8.21 | 3.58 | 3.83 | 11.75 | [5.33, 11.08] |
| Gemini 3 Flash Preview | 13.60 | 7.27 | 8.33 | 23.75 | [8.33, 19.90] |
| GLM-4.7 | 6.08 | 1.65 | 3.83 | 7.67 | [4.58, 7.46] |
| GPT-4o Mini | 6.90 | 1.10 | 5.17 | 8.25 | [6.23, 7.57] |
| GPT-5 | 10.28 | 2.68 | 4.83 | 13.58 | [8.48, 11.89] |
| o3 Mini | 8.42 | 3.01 | 6.25 | 12.83 | [6.54, 11.33] |
| Qwen Plus | 7.73 | 3.10 | 2.83 | 12.83 | [5.68, 9.94] |

# Table 4. Regularized heterogeneous Elo statistics

| Model / baseline | Regularized Elo | 95% bootstrap CI | Pairwise comparisons | Observed pairwise win rate |
| --- | --- | --- | --- | --- |
| Gemini 3 Flash Preview | 1762.90 | [1680.4, 1861.0] | 28 | 0.929 |
| GPT-5 | 1700.42 | [1611.1, 1782.9] | 20 | 0.850 |
| Claude Opus 4 | 1613.39 | [1526.0, 1741.1] | 8 | 0.875 |
| Doubao Seed 2.0 Pro | 1523.69 | [1398.7, 1631.6] | 24 | 0.500 |
| Doubao Seed 2.0 Lite | 1506.58 | [1426.1, 1572.4] | 16 | 0.438 |
| GLM-4.7 | 1464.56 | [1381.6, 1574.0] | 15 | 0.467 |
| DeepSeek V3.2 | 1455.27 | [1403.3, 1503.5] | 23 | 0.435 |
| GPT-4o Mini | 1418.09 | [1281.9, 1576.0] | 13 | 0.308 |
| Qwen Plus | 1409.44 | [1311.0, 1507.0] | 18 | 0.333 |
| Rule Fair Trade | 1391.16 | [1310.4, 1444.5] | 8 | 0.125 |
| o3 Mini | 1254.51 | [1134.3, 1384.9] | 25 | 0.080 |

# Table 5. Model-by-species assignment counts

| Model / baseline | Caylion | Eni | Faderan | Im | Kit | Yengii | Total seats |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Claude Opus 4 | 0 | 0 | 1 | 1 | 0 | 0 | 2 |
| DeepSeek V3.2 | 2 | 0 | 0 | 3 | 0 | 1 | 6 |
| Doubao Seed 2.0 Lite | 0 | 1 | 0 | 0 | 2 | 1 | 4 |
| Doubao Seed 2.0 Pro | 1 | 1 | 1 | 3 | 2 | 2 | 10 |
| Gemini 3 Flash Preview | 4 | 1 | 2 | 1 | 1 | 2 | 11 |
| GLM-4.7 | 1 | 3 | 0 | 2 | 1 | 1 | 8 |
| GPT-4o Mini | 4 | 0 | 3 | 3 | 3 | 0 | 13 |
| GPT-5 | 4 | 3 | 1 | 2 | 0 | 3 | 13 |
| o3 Mini | 1 | 1 | 2 | 1 | 1 | 5 | 11 |
| Qwen Plus | 3 | 3 | 2 | 3 | 1 | 1 | 13 |
| Rule Fair Trade | 13 | 14 | 0 | 13 | 1 | 13 | 54 |

# Table 6. Species-level terminal-score statistics

| Species | Seats | Mean score | Std. | Min | Max | 95% bootstrap CI |
| --- | --- | --- | --- | --- | --- | --- |
| Caylion | 33 | 12.15 | 7.59 | 5.42 | 31.50 | [9.74, 14.66] |
| Eni | 27 | 6.85 | 3.19 | 2.33 | 18.75 | [5.79, 8.01] |
| Faderan | 12 | 16.02 | 11.52 | 3.50 | 39.33 | [10.16, 22.06] |
| Im | 32 | 6.21 | 2.21 | 3.00 | 13.67 | [5.51, 6.97] |
| Kit | 12 | 10.97 | 7.12 | 4.00 | 30.67 | [7.66, 15.28] |
| Yengii | 29 | 9.85 | 4.13 | 2.67 | 20.42 | [8.41, 11.32] |

# Table 7. Human/model calibration statistics

| Model / baseline | Average player num | Mean score | Std. | Min | Max | 95% bootstrap CI |
| --- | --- | --- | --- | --- | --- | --- |
| Claude Opus 4 | 5 | 17.25 | 9.07 | 10.83 | 23.67 | [10.83, 23.67] |
| DeepSeek V3.2 | 4.83 | 8.67 | 2.80 | 5.67 | 13.92 | [6.97, 10.99] |
| Doubao Seed 2.0 Lite | 5 | 9.96 | 3.17 | 6.92 | 14.42 | [7.52, 13.10] |
| Doubao Seed 2.0 Pro | 4.86 | 11.50 | 5.06 | 3.83 | 18.33 | [8.55, 14.44] |
| Gemini 3 Flash Preview | 4.88 | 23.86 | 10.21 | 8.33 | 39.33 | [18.20, 29.28] |
| GLM-4.7 | 4.60 | 6.85 | 3.22 | 3.58 | 14.00 | [4.97, 9.26] |
| GPT-4o Mini | 4.33 | 7.08 | 2.15 | 4.00 | 12.75 | [6.04, 8.42] |
| GPT-5 | 4.71 | 15.10 | 7.23 | 4.83 | 27.08 | [11.42, 18.99] |
| Human | 7 | 47.93 | 16.59 | 20.00 | 80.00 | [40.07, 56.29] |
| o3 Mini | 4.50 | 5.70 | 3.55 | 2.33 | 12.83 | [3.80, 7.76] |
| Qwen Plus | 4.43 | 7.21 | 2.83 | 2.83 | 12.83 | [5.74, 8.69] |
| Rule Fair Trade | 4.13 | 7.24 | 1.86 | 3.00 | 11.42 | [6.76, 7.73] |

# Table 8. Rule-baseline comparison

| Model / baseline | Mean score | Std. | Min | Max | 95% bootstrap CI |
| --- | --- | --- | --- | --- | --- |
| Claude Opus 4 | 17.25 | 9.07 | 10.83 | 23.67 | [10.83, 23.67] |
| DeepSeek V3.2 | 8.67 | 2.80 | 5.67 | 13.92 | [6.97, 10.99] |
| Doubao Seed 2.0 Lite | 9.96 | 3.17 | 6.92 | 14.42 | [7.52, 13.10] |
| Doubao Seed 2.0 Pro | 11.50 | 5.06 | 3.83 | 18.33 | [8.55, 14.44] |
| Gemini 3 Flash Preview | 23.86 | 10.21 | 8.33 | 39.33 | [18.20, 29.28] |
| GLM-4.7 | 6.85 | 3.22 | 3.58 | 14.00 | [4.97, 9.26] |
| GPT-4o Mini | 7.08 | 2.15 | 4.00 | 12.75 | [6.04, 8.42] |
| GPT-5 | 15.10 | 7.23 | 4.83 | 27.08 | [11.42, 18.99] |
| Human | 47.93 | 16.59 | 20.00 | 80.00 | [40.07, 56.29] |
| o3 Mini | 5.70 | 3.55 | 2.33 | 12.83 | [3.80, 7.76] |
| Qwen Plus | 7.21 | 2.83 | 2.83 | 12.83 | [5.74, 8.69] |
| Rule Fair Trade | 7.24 | 1.86 | 3.00 | 11.42 | [6.76, 7.73] |

# Table 9. Function-calling parse reliability

| Model / baseline | Attempts | Successes | Failure rate |
| --- | --- | --- | --- |
| DeepSeek V3.2 | 2824 | 2823 | 0.000 |
| Doubao Seed 2.0 Lite | 1392 | 1392 | 0.000 |
| Doubao Seed 2.0 Pro | 1399 | 1397 | 0.001 |
| Gemini 3 Flash Preview | 1581 | 1577 | 0.003 |
| GLM-4.7 | 85 | 85 | 0.000 |
| GPT-5 | 1001 | 963 | 0.038 |
| o3 Mini | 4300 | 4220 | 0.019 |
| Qwen Plus | 1903 | 1898 | 0.003 |

# Table 10. Trade-value diagnostics

| Model / baseline | Games with stats | Avg. trades/game | Avg. signed trade value/game | Avg. gain amount/game | Avg. loss amount/game | Loss-trade rate | Gain trades | Loss trades |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DeepSeek V3.2 | 4 | 34.75 | -4.12 | 8.25 | 12.38 | 0.647 | 49.00 | 90.00 |
| Doubao Seed 2.0 Lite | 3 | 6.00 | 0.83 | 2.00 | 1.17 | 0.389 | 11.00 | 7.00 |
| Doubao Seed 2.0 Pro | 4 | 21.00 | -1.38 | 7.38 | 8.75 | 0.452 | 46.00 | 38.00 |
| Gemini 3 Flash Preview | 5 | 21.40 | 7.60 | 12.60 | 5.00 | 0.355 | 69.00 | 38.00 |
| GLM-4.7 | 1 | 12.00 | -7.00 | 3.00 | 10.00 | 0.667 | 4.00 | 8.00 |
| GPT-5 | 4 | 11.00 | -4.25 | 2.25 | 6.50 | 0.591 | 18.00 | 26.00 |
| o3 Mini | 4 | 7.50 | 0.88 | 2.50 | 1.62 | 0.400 | 18.00 | 12.00 |
| Qwen Plus | 3 | 19.67 | 0.83 | 5.67 | 4.83 | 0.458 | 32.00 | 27.00 |
| Rule Fair Trade | 7 | 4.14 | -0.07 | 1.43 | 1.50 | 0.517 | 14.00 | 15.00 |

# Table 11. Signed exploitation matrix

| Extracting model | DeepSeek V3.2 | Doubao Seed 2.0 Lite | Doubao Seed 2.0 Pro | Gemini 3 Flash Preview | GLM-4.7 | GPT-5 | o3 Mini | Qwen Plus | Rule Fair Trade |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DeepSeek V3.2 | 0.00 | -0.50 | -4.75 | -2.83 | 7.00 | -1.25 | -0.62 | 0.00 | N/A |
| Doubao Seed 2.0 Lite | 0.50 | N/A | -0.25 | 0.83 | N/A | 0.00 | N/A | -0.50 | 0.25 |
| Doubao Seed 2.0 Pro | 4.75 | 0.25 | N/A | -5.17 | N/A | 0.50 | -1.00 | 0.00 | N/A |
| Gemini 3 Flash Preview | 2.83 | -0.83 | 5.17 | N/A | 0.00 | 5.33 | 0.33 | -0.25 | N/A |
| GLM-4.7 | -7.00 | N/A | N/A | 0.00 | N/A | N/A | 0.00 | N/A | N/A |
| GPT-5 | 1.25 | 0.00 | -0.50 | -5.33 | N/A | N/A | -0.25 | -0.50 | N/A |
| o3 Mini | 0.62 | N/A | 1.00 | -0.33 | 0.00 | 0.25 | N/A | -0.25 | N/A |
| Qwen Plus | 0.00 | 0.50 | 0.00 | 0.25 | N/A | 0.50 | 0.25 | 0.00 | N/A |
| Rule Fair Trade | N/A | -0.25 | N/A | N/A | N/A | N/A | N/A | N/A | 0.00 |
