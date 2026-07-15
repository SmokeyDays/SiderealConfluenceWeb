# Draft Response to Reviewer 1

We thank the reviewer for the careful reading and concrete suggestions. We agree that the original submission underreported several experimental details and quantitative results. We will revise the paper to make the evaluation protocol, model set, species assignment, human calibration, and reproducibility package explicit.

## W1: Experimental Parameters Were Underspecified

We agree and will add a dedicated experimental-settings table in the main paper or appendix. The revised table will report, for each experiment group, the number of games, number of player seats per game, number of rounds, species pool, model assignment schedule, random seeds, model identifiers, decoding parameters, and failed-run filtering criteria.

We will add the following experimental-settings table:

| Experiment group | Completed games | Player seats/game | Rounds | Species pool | Model assignment | Random seeds | Temperature | Function-calling mode | Incomplete-run filtering |
| --- | ---: | ---: | ---: | --- | --- | --- | ---: | --- | --- |
| Self-play | Reported in Table 3 | 4 by default | 6 | Caylion, Yengii, Im, Eni, Faderan, Kit | Homogeneous: all bot seats use the same model | Original runs did not fix a global seed; deck/species randomness is preserved in logs and `pkl` snapshots | 0 | `on`, with legacy JSON fallback | Only completed games in `game_records` are used for terminal-score tables |
| Heterogeneous Elo | Reported in Table 4 | 5 in the current runner | 6 | Caylion, Yengii, Im, Eni, Faderan, Kit, shuffled before assignment | `sample_random_api(4) + rule-fair` in the current runner; one model per bot seat | Original runs did not fix a global seed; assignment and deck randomness are preserved in logs and `pkl` snapshots | 0 | `on`, with legacy JSON fallback | Only completed games in `game_records` are used for Elo and terminal-score tables |
| Rule baseline | Reported in Table 8 | 4 in homogeneous self-play; also included as one seat in mixed Elo runs | 6 | Same as the corresponding experiment group | `rule-fair` controls the corresponding bot seat(s) | Rule policy is deterministic except when a legal random fallback is required | N/A | N/A | Only completed games in `game_records` are used |
| Human calibration | Reported in Table 7 | Determined by volunteer room size | Full completed game | Human-play species selected through the same web UI | Human players use the same game server and action protocol | Preserved in released logs and `pkl` snapshots | N/A | N/A | Only completed human games in `game_records` are used |

In all reported LLM runs, agents use the same observation format, prompt templates, phase-aware caller architecture, action schema, and environment rules. Model calls are run with temperature set to 0 to reduce generation variance. The default game horizon is 6 rounds. Function calling is enabled through the same validated action interface for all LLM agents, with legacy JSON fallback only when a provider does not return a valid tool call. We will also state that incomplete games are excluded from terminal-score and Elo computation, while function-calling failures and invalid actions are retained in diagnostic statistics.

We will add a model-by-species assignment table. Because SidConArena contains asymmetric species, we will report both raw terminal scores and species-balanced statistics. In the expanded experiments, each evaluated model is assigned to each species at least once, and the appendix will include per-species mean scores so readers can inspect whether a model ranking is confounded by species assignment.

## W2: The Number of Experiments Was Too Small / Not Clearly Reported

We agree that the original text made the scale of the experiments unclear and that the 20-game heterogeneous tournament is too small to support strong claims without uncertainty estimates.

First, we will clarify what is counted. A "game" is one completed multi-player rollout. In our setting, each game has approximately five players, so one completed heterogeneous game yields about ten pairwise model comparisons. Thus, the 20-game Elo tournament corresponds to roughly 200 pairwise Elo observations rather than only 20 binary comparisons. Nevertheless, we agree that this scale is still limited for a stable model ranking, especially under asymmetric species assignments and stochastic auction outcomes. We will report all three quantities explicitly: completed games, player seats, and pairwise comparisons.

Because each full game is expensive and time-consuming, we have been running additional experiments during the rebuttal period. At the time of writing, we have obtained 3 additional completed experimental groups. We will include these new results in the revised table and mark the experimental scale clearly. We also added additional monitoring statistics to the game records, including function-calling parse failure rate by model, signed trade gain/loss rate and amount, loss-trade ratio, and a signed exploitation matrix that measures value transfer in accepted trades. These diagnostics are intended to make the smaller-scale rollouts more informative and to support the qualitative claims with systematic evidence.

Second, we will expand the reported quantitative tables. The revised paper will include:

- A self-play table with number of games/seats, mean, median, standard deviation, min/max score, and bootstrap 95% confidence intervals.
- An Elo table with actual Elo values, number of completed games, number of pairwise comparisons, and bootstrap 95% confidence intervals.
- A model-by-species coverage table.
- A species-level table reporting average score by species, so that readers can judge the impact of asymmetric starting conditions.

We will temper the wording of ranking claims accordingly. Rather than presenting the small tournament as a definitive ranking, we will describe it as a relative-performance estimate under the collected tournament schedule, with uncertainty explicitly shown. The expanded schedule is balanced so that each model plays each species at least once and model pairs co-occur more evenly.

The quantitative result tables will be inserted in the revision in the following format:

| Model / baseline | Completed games | Player seats | Mean score | Median | Std. | Min | Max | 95% bootstrap CI |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD |

| Model / baseline | Elo | 95% bootstrap CI | Completed games | Player seats | Pairwise comparisons |
| --- | ---: | --- | ---: | ---: | ---: |
| TBD | TBD | TBD | TBD | TBD | TBD |

| Model / baseline | Function-call attempts | Parse failures | Failure rate | Avg. signed trade value/game | Loss-trade rate | Avg. exploitation transfer/game |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| TBD | TBD | TBD | TBD | TBD | TBD | TBD |

## W3: Model Names Were Inconsistent

We agree and will canonicalize all model names across Section 5, Section 6, Appendix A, Appendix D, figures, and released records. We will add an "Evaluated Models" table with both display names and exact API/deployment identifiers.

The inconsistency arose from two issues. First, the model list in Section 5 was not updated after we added several additional models, which led to conflicts with later result sections and appendices. Second, DeepSeek's official `deepseek-chat` platform endpoint was silently upgraded from a V3-series model to a V4-series model when the platform released V4. As a result, some early records using that endpoint could not be cleanly attributed to either V4 or V3.2. To avoid ambiguity, we decided to discard those ambiguous DeepSeek records and rerun the DeepSeek experiments using the fixed Ark deployment of DeepSeek V3.2.

The intended canonical names are:

| Display name in paper | Agent id in records | Exact model/deployment identifier | Provider / endpoint | Included use |
| --- | --- | --- | --- | --- |
| GPT-4o Mini | `gpt-4o-mini` | Azure deployment `gpt-4o-mini` | Azure OpenAI | Self-play / Elo |
| o3 Mini | `o3-mini` | Azure deployment `o3-mini` | Azure OpenAI | Self-play / Elo |
| GPT-5 | `gpt-5` | Azure deployment `gpt-5` | Azure OpenAI | Self-play / Elo |
| Gemini 3 Flash Preview | `gemini-3-flash-preview` | `gemini-3-flash-preview` | Google GenAI | Self-play / Elo |
| Claude Opus 4 | `claude-opus-4` | `claude-opus-4-5-20251101` | OpenAI-compatible Claude endpoint | Self-play / Elo |
| Qwen Plus | `qwen-plus` | `qwen-plus` | DashScope OpenAI-compatible endpoint | Self-play / Elo where available |
| DeepSeek V3.2 | `deepseek-v3.2` | `deepseek-v3-2-251201` | Volcengine Ark fixed deployment | Self-play / Elo |
| Doubao Seed 2.0 Lite | `doubao-seed-2.0-lite` | `doubao-seed-2-0-lite-260428` | Volcengine Ark | Diagnostic / additional runs |
| Doubao Seed 2.0 Pro | `doubao-seed-2.0-pro` | `doubao-seed-2-0-pro-260215` | Volcengine Ark | Diagnostic / additional runs |
| GLM-4.7 | `glm-4.7` | `glm-4-7-251222` | Volcengine Ark | Self-play / Elo |
| Rule Fair Trade | `rule-fair` | local rule policy | Local baseline | Rule baseline / Elo calibration |
| Human | `human` | N/A | Web UI | Human calibration |

In the revision, the DeepSeek entry used for the final experiments will be uniformly reported as DeepSeek V3.2. The Appendix D mention of DeepSeek-V4-Pro was an error and will be removed. GLM-4.7 and the Doubao variants will also be introduced in the model table before being discussed in results.

## W4: Human Baseline

We agree that a human calibration point is valuable. We have organized volunteer human self-play sessions using the same web interface and game server. These sessions use the same environment state, action protocol, scoring rule, and terminal-score recorder as the LLM rollouts.

Current volunteer self-play records contain 2 human-only games and 14 human player seats. In the revised table, we will report the human baseline side by side with model baselines and use average player count per game instead of raw player-seat count:

| Model / baseline | Completed games | Average player num | Mean | Median | Std. | Min | Max | 95% bootstrap CI |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Human | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD |
| LLM / rule baselines | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD |

The recorded species coverage is: Zeth 2, Kit 2, Eni 2, Caylion 2, Im 1, Kjasjavikalimm 1, Unity 1, Faderan 1, Far 1, and Yengii 1. We will include this as a small calibration baseline rather than as a definitive human-vs-LLM comparison. The game setting, scoring rule, server, and action protocol are the same as in the model runs. We were also surprised that human players outperformed LLM agents by such a large margin. A plausible explanation is that humans can negotiate through richer discussion patterns, while our current LLM agents mainly interact through structured bulletin-board posts and binding proposals. In addition, LLM context windows are substantially occupied by rules and state descriptions, leaving limited room for strategic deliberation. Finally, the gap may also indicate that the current agent architecture and prompts leave considerable room for improvement. We will clearly label the sample size and avoid overclaiming. If space allows, we will also include a mixed human-LLM pilot or human-vs-rule-agent pilot in the appendix.

## W5: Typos and Presentation Errors

We will fix the copy-editing issues identified by the reviewer. In particular:

- The Figure 4 caption will be corrected to describe Elo ratings rather than duplicating the Figure 3 self-play caption.
- The truncated Section 3 sentence around the observation function will be rewritten.
- Model names will be made consistent across the main text, appendix, figures, and released records.
- We will proofread the result discussion to ensure every figure/table reference points to the correct artifact.

## W6: Engineering Contribution

We appreciate the concern that the benchmark should be more than a port of an existing game. We will revise the contribution statement to emphasize the reusable benchmark infrastructure rather than only the game mechanics.

The main engineering contribution is an executable multi-agent evaluation harness for open-ended, positive-sum bargaining. It combines: structured private/public/market/interaction observations; phase-aware dispatch to specialized callers for planning, trading, production, bidding, and picking; a validated neural-symbolic action interface that converts natural-language reasoning into executable game actions; asynchronous negotiation so agents can react concurrently; a trusted negotiation ledger for binding trades; deterministic production and auction engines; full trajectory logging; and a web interface that supports both LLM and human players under the same protocol.

We will also add empirical characterization to support this contribution. In addition to terminal scores and Elo, the revision will report diagnostic metrics such as function-calling parse failure rate, trade gain/loss rate, accepted-trade value transfer, and a signed exploitation matrix. The function-calling statistic specifically measures parse/schema failures after a model response is obtained; it does not include network errors, API timeouts, provider-side connection failures, or other model-call failures. These metrics show that the framework is not merely a UI around a board game, but an instrumented environment for analyzing valuation, bargaining, and long-horizon planning behavior.

## W7: Reproducibility

We will improve reproducibility by releasing the implementation and analysis artifacts. The release will include:

- Source code for the game server, web interface, LLM agent harness, and rule-based baseline.
- Running logs for the experiments used in the paper.
- Serialized game snapshots / room states in `pkl` format for the corresponding runs.
- Prompt templates and function/action schemas.
- Agent cards with canonical display names and exact model identifiers.
- Configuration files specifying player count, round count, species pool, temperature, function-calling mode, timeout/watchdog settings, and random seeds.
- Scripts for running homogeneous self-play and heterogeneous Elo tournaments.
- Completed `game_records` files and analysis scripts for producing score tables, Elo estimates, bootstrap confidence intervals, model-by-species coverage, and diagnostic statistics.

The concrete default settings to be documented are: 6 game rounds, temperature 0 for LLM calls, identical prompts and action schemas across models, validated function calling enabled with fallback, explicit species assignment schedules, and exclusion of incomplete games from terminal-score/Elo tables. We will also release the exact list of completed runs used for each figure/table so the reported results can be regenerated from the records.

## Tables to Add in the Revision

1. Experimental settings table: game count, player count, rounds, species pool, model assignment, seeds, temperature, function-calling mode, and filtering rule.
2. Canonical model table: display name, exact deployment/API identifier, provider, and whether the model is included in self-play, Elo, or diagnostic runs.
3. Self-play terminal-score table: games, seats, mean, median, std., min/max, bootstrap CI, and species coverage.
4. Heterogeneous Elo table: Elo, bootstrap CI, completed games, player seats, and pairwise comparisons.
5. Model-by-species assignment table: rows as non-human models/baselines and columns as species.
6. Species-level score table: non-human seats only; each species' mean/std score and number of seats, used to show species asymmetry.
7. Human/model calibration table: human baseline and model baselines side by side, with games, average player number, mean/median/std/min/max terminal scores, and bootstrap CI.
8. Rule-baseline comparison table: rule-fair versus LLM models and human calibration under the same terminal-score metrics.
9. Function-calling parse reliability table: attempts, parse/schema failures, and parse failure rates by model; network/API call failures are reported separately in logs rather than counted in this table.
10. Trade-value diagnostic table: signed average trade gain/loss per game, loss-trade rate, gain amount, and loss amount by model.
11. Signed exploitation matrix: row model's average value extracted from column model per game; positive means exploitation and negative means being exploited. Unobserved model pairs are reported as N/A rather than 0.
