# Table 3. Self-play terminal-score statistics

| Model / baseline | Model id | Completed games | Player seats | Mean score | Median | Std. | Min | Max | 95% bootstrap CI |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Doubao Seed 2.0 Pro | doubao-seed-2.0-pro | 1 | 4 | 8.21 | 8.62 | 3.58 | 3.83 | 11.75 | [5.33, 11.08] |
| Gemini 3 Flash Preview | gemini-3-flash-preview | 1 | 4 | 13.60 | 11.17 | 7.27 | 8.33 | 23.75 | [8.33, 19.90] |
| GLM-4.7 | glm-4.7 | 1 | 4 | 6.08 | 6.42 | 1.65 | 3.83 | 7.67 | [4.58, 7.46] |
| GPT-4o Mini | gpt-4o-mini | 2 | 9 | 6.90 | 6.33 | 1.10 | 5.17 | 8.25 | [6.23, 7.57] |
| GPT-5 | gpt-5 | 2 | 8 | 10.28 | 10.21 | 2.68 | 4.83 | 13.58 | [8.48, 11.89] |
| o3 Mini | o3-mini | 1 | 4 | 8.42 | 7.29 | 3.01 | 6.25 | 12.83 | [6.54, 11.33] |
| Qwen Plus | qwen-plus | 2 | 8 | 7.73 | 7.29 | 3.10 | 2.83 | 12.83 | [5.68, 9.94] |

# Table 4. Heterogeneous Elo statistics

| Model / baseline | Model id | Elo | 95% bootstrap CI | Completed games | Player seats | Pairwise comparisons |
| --- | --- | --- | --- | --- | --- | --- |
| Gemini 3 Flash Preview | gemini-3-flash-preview | 2491.60 | [1910.7, 4208.3] | 4 | 4 | 16 |
| GPT-5 | gpt-5 | 2313.33 | [2139.0, 3545.0] | 2 | 2 | 8 |
| Claude Opus 4 | claude-opus-4 | 2309.90 | [1511.3, 4436.3] | 2 | 2 | 8 |
| Doubao Seed 2.0 Pro | doubao-seed-2.0-pro | 2134.07 | [1562.7, 3382.0] | 3 | 3 | 12 |
| Doubao Seed 2.0 Lite | doubao-seed-2.0-lite | 1487.27 | [992.1, 2204.0] | 1 | 1 | 4 |
| GLM-4.7 | glm-4.7 | 987.34 | [631.8, 2268.2] | 4 | 4 | 15 |
| DeepSeek V3.2 | deepseek-v3.2 | 972.02 | [545.3, 2269.8] | 4 | 4 | 15 |
| GPT-4o Mini | gpt-4o-mini | 910.21 | [-3299.9, 1993.6] | 4 | 4 | 13 |
| Qwen Plus | qwen-plus | 763.02 | [-3299.8, 2107.7] | 3 | 3 | 10 |
| o3 Mini | o3-mini | 631.26 | [-3300.0, 1135.1] | 5 | 5 | 17 |

# Table 5. Model-by-species assignment counts

| Model / baseline | Model id | Caylion | Eni | Faderan | Im | Kit | Yengii | Total seats |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Claude Opus 4 | claude-opus-4 | 0 | 0 | 1 | 1 | 0 | 0 | 2 |
| DeepSeek V3.2 | deepseek-v3.2 | 2 | 0 | 0 | 2 | 0 | 0 | 4 |
| Doubao Seed 2.0 Lite | doubao-seed-2.0-lite | 0 | 0 | 0 | 0 | 1 | 0 | 1 |
| Doubao Seed 2.0 Pro | doubao-seed-2.0-pro | 1 | 1 | 1 | 1 | 1 | 2 | 7 |
| Gemini 3 Flash Preview | gemini-3-flash-preview | 2 | 1 | 2 | 1 | 0 | 2 | 8 |
| GLM-4.7 | glm-4.7 | 1 | 3 | 0 | 2 | 1 | 1 | 8 |
| GPT-4o Mini | gpt-4o-mini | 4 | 0 | 3 | 3 | 3 | 0 | 13 |
| GPT-5 | gpt-5 | 2 | 3 | 0 | 2 | 0 | 3 | 10 |
| o3 Mini | o3-mini | 1 | 1 | 1 | 1 | 1 | 4 | 9 |
| Qwen Plus | qwen-plus | 3 | 2 | 1 | 3 | 1 | 1 | 11 |
| Rule Fair Trade | rule-fair | 14 | 14 | 0 | 14 | 0 | 14 | 56 |

# Table 6. Species-level terminal-score statistics

| Species | Seats | Mean score | Median | Std. | Min | Max | 95% bootstrap CI |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Caylion | 30 | 10.03 | 8.00 | 5.31 | 5.42 | 31.50 | [8.40, 12.07] |
| Eni | 25 | 6.99 | 6.67 | 3.27 | 2.33 | 18.75 | [5.87, 8.29] |
| Faderan | 9 | 17.21 | 12.83 | 11.97 | 6.25 | 39.33 | [10.15, 24.30] |
| Im | 30 | 5.83 | 5.38 | 1.77 | 3.00 | 10.83 | [5.27, 6.49] |
| Kit | 8 | 7.98 | 7.50 | 2.99 | 4.00 | 14.00 | [6.11, 10.01] |
| Yengii | 27 | 9.91 | 9.33 | 4.03 | 2.67 | 20.42 | [8.52, 11.52] |

# Table 7. Human/model calibration statistics

| Model / baseline | Model id | Completed games | Average player num | Mean score | Median | Std. | Min | Max | 95% bootstrap CI |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Claude Opus 4 | claude-opus-4 | 2 | 5 | 17.25 | 17.25 | 9.07 | 10.83 | 23.67 | [10.83, 23.67] |
| DeepSeek V3.2 | deepseek-v3.2 | 4 | 4.75 | 8.67 | 7.54 | 3.61 | 5.67 | 13.92 | [6.15, 12.31] |
| Doubao Seed 2.0 Lite | doubao-seed-2.0-lite | 1 | 5 | 9.33 | 9.33 | 0.00 | 9.33 | 9.33 | [9.33, 9.33] |
| Doubao Seed 2.0 Pro | doubao-seed-2.0-pro | 4 | 4.75 | 11.18 | 10.42 | 5.39 | 3.83 | 18.33 | [7.55, 15.26] |
| Gemini 3 Flash Preview | gemini-3-flash-preview | 5 | 4.80 | 22.16 | 22.08 | 11.50 | 8.33 | 39.33 | [14.70, 29.61] |
| GLM-4.7 | glm-4.7 | 5 | 4.60 | 6.85 | 6.46 | 3.22 | 3.58 | 14.00 | [4.97, 9.26] |
| GPT-4o Mini | gpt-4o-mini | 6 | 4.33 | 7.08 | 6.33 | 2.15 | 4.00 | 12.75 | [6.04, 8.42] |
| GPT-5 | gpt-5 | 4 | 4.50 | 11.74 | 10.88 | 3.92 | 4.83 | 18.75 | [9.67, 13.80] |
| Human | human | 2 | 7 | 47.93 | 46.00 | 16.59 | 20.00 | 80.00 | [40.07, 56.29] |
| o3 Mini | o3-mini | 6 | 4.33 | 6.14 | 6.25 | 3.82 | 2.33 | 12.83 | [4.04, 8.72] |
| Qwen Plus | qwen-plus | 5 | 4.20 | 7.33 | 6.75 | 2.96 | 2.83 | 12.83 | [5.77, 9.01] |
| Rule Fair Trade | rule-fair | 14 | 4 | 7.19 | 7.79 | 1.78 | 3.00 | 9.42 | [6.70, 7.63] |

# Table 8. Rule-baseline comparison

| Model / baseline | Model id | Completed games | Player seats | Mean score | Median | Std. | Min | Max | 95% bootstrap CI |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Claude Opus 4 | claude-opus-4 | 2 | 2 | 17.25 | 17.25 | 9.07 | 10.83 | 23.67 | [10.83, 23.67] |
| DeepSeek V3.2 | deepseek-v3.2 | 4 | 4 | 8.67 | 7.54 | 3.61 | 5.67 | 13.92 | [6.15, 12.31] |
| Doubao Seed 2.0 Lite | doubao-seed-2.0-lite | 1 | 1 | 9.33 | 9.33 | 0.00 | 9.33 | 9.33 | [9.33, 9.33] |
| Doubao Seed 2.0 Pro | doubao-seed-2.0-pro | 4 | 7 | 11.18 | 10.42 | 5.39 | 3.83 | 18.33 | [7.55, 15.26] |
| Gemini 3 Flash Preview | gemini-3-flash-preview | 5 | 8 | 22.16 | 22.08 | 11.50 | 8.33 | 39.33 | [14.70, 29.61] |
| GLM-4.7 | glm-4.7 | 5 | 8 | 6.85 | 6.46 | 3.22 | 3.58 | 14.00 | [4.97, 9.26] |
| GPT-4o Mini | gpt-4o-mini | 6 | 13 | 7.08 | 6.33 | 2.15 | 4.00 | 12.75 | [6.04, 8.42] |
| GPT-5 | gpt-5 | 4 | 10 | 11.74 | 10.88 | 3.92 | 4.83 | 18.75 | [9.67, 13.80] |
| Human | human | 2 | 14 | 47.93 | 46.00 | 16.59 | 20.00 | 80.00 | [40.07, 56.29] |
| o3 Mini | o3-mini | 6 | 9 | 6.14 | 6.25 | 3.82 | 2.33 | 12.83 | [4.04, 8.72] |
| Qwen Plus | qwen-plus | 5 | 11 | 7.33 | 6.75 | 2.96 | 2.83 | 12.83 | [5.77, 9.01] |
| Rule Fair Trade | rule-fair | 14 | 56 | 7.19 | 7.79 | 1.78 | 3.00 | 9.42 | [6.70, 7.63] |

# Table 9. Function-calling parse reliability

| Model / baseline | Model id | Attempts | Successes | Parse failures | Failure rate |
| --- | --- | --- | --- | --- | --- |
| DeepSeek V3.2 | deepseek-v3.2 | 2161 | 2160 | 1 | 0.000 |
| Doubao Seed 2.0 Pro | doubao-seed-2.0-pro | 670 | 669 | 1 | 0.001 |
| Gemini 3 Flash Preview | gemini-3-flash-preview | 1033 | 1030 | 3 | 0.003 |
| GLM-4.7 | glm-4.7 | 85 | 85 | 0 | 0.000 |
| GPT-5 | gpt-5 | 466 | 463 | 3 | 0.006 |
| o3 Mini | o3-mini | 2023 | 2022 | 1 | 0.000 |
| Qwen Plus | qwen-plus | 1295 | 1295 | 0 | 0.000 |

# Table 10. Trade-value diagnostics

| Model / baseline | Model id | Games with stats | Trade count | Avg. signed trade value/game | Avg. gain amount/game | Avg. loss amount/game | Loss-trade rate | Gain trades | Loss trades |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DeepSeek V3.2 | deepseek-v3.2 | 2 | 130.00 | -6.50 | 17.75 | 24.25 | 0.600 | 52.00 | 78.00 |
| Doubao Seed 2.0 Pro | doubao-seed-2.0-pro | 1 | 62.00 | -6.00 | 18.00 | 24.00 | 0.500 | 31.00 | 31.00 |
| Gemini 3 Flash Preview | gemini-3-flash-preview | 2 | 88.00 | 17.00 | 25.00 | 8.00 | 0.295 | 62.00 | 26.00 |
| GLM-4.7 | glm-4.7 | 1 | 12.00 | -7.00 | 3.00 | 10.00 | 0.667 | 4.00 | 8.00 |
| GPT-5 | gpt-5 | 1 | 24.00 | -4.00 | 5.00 | 9.00 | 0.583 | 10.00 | 14.00 |
| o3 Mini | o3-mini | 2 | 23.00 | 1.00 | 3.50 | 2.50 | 0.391 | 14.00 | 9.00 |
| Qwen Plus | qwen-plus | 1 | 51.00 | -6.00 | 12.00 | 18.00 | 0.569 | 22.00 | 29.00 |
| Rule Fair Trade | rule-fair | 6 | 28.00 | 0.00 | 1.67 | 1.67 | 0.500 | 14.00 | 14.00 |

# Table 11. Signed exploitation matrix

| Extracting model | Model id | DeepSeek V3.2 | Doubao Seed 2.0 Pro | Gemini 3 Flash Preview | GLM-4.7 | GPT-5 | o3 Mini | Qwen Plus | Rule Fair Trade |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DeepSeek V3.2 | deepseek-v3.2 | 0.00 | -6.50 | -7.25 | 7.00 | 0.00 | -1.00 | 3.00 | N/A |
| Doubao Seed 2.0 Pro | doubao-seed-2.0-pro | 6.50 | N/A | -11.50 | N/A | -1.00 | -1.00 | 1.00 | N/A |
| Gemini 3 Flash Preview | gemini-3-flash-preview | 7.25 | 11.50 | N/A | 0.00 | 4.00 | 0.75 | 2.50 | N/A |
| GLM-4.7 | glm-4.7 | -7.00 | N/A | 0.00 | N/A | N/A | 0.00 | N/A | N/A |
| GPT-5 | gpt-5 | 0.00 | 1.00 | -4.00 | N/A | N/A | 0.00 | -1.00 | N/A |
| o3 Mini | o3-mini | 1.00 | 1.00 | -0.75 | 0.00 | 0.00 | N/A | 0.50 | N/A |
| Qwen Plus | qwen-plus | -3.00 | -1.00 | -2.50 | N/A | 1.00 | -0.50 | N/A | N/A |
| Rule Fair Trade | rule-fair | N/A | N/A | N/A | N/A | N/A | N/A | N/A | 0.00 |
