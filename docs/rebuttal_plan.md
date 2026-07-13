# Rebuttal Experiment Plan

This document summarizes the additional experiments and analyses needed in response to the reviewer comments in `docs/rebuttal.md`.

## Main Reviewer Concerns

The reviews converge on five empirical weaknesses:

1. Quantitative results are underreported.
2. The heterogeneous Elo tournament is too small and lacks uncertainty estimates.
3. Species asymmetry and model/species assignment are underspecified.
4. There are no non-LLM or human calibration baselines.
5. Qualitative failure modes are not supported by systematic metrics.

## Priority 1: Quantitative Results Table

Add a table for all self-play experiments.

Report, for each model:

- Number of games.
- Number of player seats.
- Mean terminal score.
- Median terminal score.
- Standard deviation.
- Min and max score.
- 95% bootstrap confidence interval.
- Species coverage.

Recommended additional columns:

- Mean species-normalized score.
- Number of completed games used after filtering failed or incomplete runs.

Code basis:

- Existing results are stored in `server/charts/game_records.json` and `server/charts/game_records_local.json`.
- `GameRecorder.add_record` already stores `model`, `specie`, and `score`.
- `GameRecorder.plot_boxplot` currently visualizes self-play, but does not export a quantitative table.

Implementation note:

Add an analysis script or extend `server/charts/recorder.py` with a non-interactive summary export function that writes CSV/Markdown tables.

## Priority 2: Larger Elo Tournament With Confidence Intervals

Expand heterogeneous evaluation from the current small tournament to at least 100 completed games.

Report:

- Elo rating for each model.
- 95% bootstrap confidence interval for each Elo.
- Number of games each model appears in.
- Number of pairwise comparisons per model pair.
- Model assignment and species assignment schedule.

Code basis:

- `Server.series_elo` currently starts chained Elo experiments.
- `Server.add_elo_exp` creates heterogeneous games.
- `GameRecorder._compute_elo` already estimates Elo-like ratings using Bradley-Terry MLE.

Recommended change:

Use a balanced schedule rather than pure random sampling:

- Each model should appear approximately the same number of times.
- Each model should play each species approximately the same number of times.
- Each pair of models should co-occur enough times for stable pairwise comparisons.

## Priority 3: Species Assignment and Normalization

Reviewers explicitly asked how species asymmetry is handled.

Add:

- A table of model-by-species counts.
- Raw score results.
- Species-normalized score results.

Possible normalization:

For each species, compute the mean and standard deviation across all runs. Then transform each score:

```text
normalized_score = (score - species_mean) / species_std
```

If the number of runs per species is small, use a simpler centered score:

```text
species_centered_score = score - species_mean
```

Use both raw and normalized values in the appendix if space allows.

## Priority 4: Non-LLM Baselines

Add at least three rule-based baselines to calibrate task difficulty.

Recommended baselines:

1. Fair-trade agent
   - Proposes trades whose estimated immediate resource value is close to equal.
   - Accepts trades above a small value threshold.

2. Utility-maximizing rule agent
   - Greedily runs converters with highest estimated value gain.
   - Trades only for resources needed by planned converters.
   - Bids ships according to estimated colony/research value.

3. Scripted human-like negotiation agent
   - Posts needs/offers.
   - Makes targeted proposals.
   - Counteroffers instead of only accepting/rejecting.
   - Keeps some ships for future bidding.

Code basis:

- Rule agents can call the same game actions used by LLM agents:
  - `trade_proposal`
  - `accept_trade_proposal`
  - `produce`
  - `submit_bid`
  - `submit_pick`

Expected rebuttal value:

This addresses the concern that the paper only compares LLMs against LLMs and gives no calibration for whether the environment is difficult or meaningful.

## Priority 5: Human Baseline or Mixed Human-LLM Pilot

Add a small human calibration study if feasible.

Minimum viable options:

- Human-only historical baseline table.
- 1 human + 3-5 LLM mixed games.
- Human-vs-rule-agent comparison.

Report:

- Human terminal scores.
- LLM terminal scores in mixed games.
- Number of trades.
- Optional short post-game questionnaire about whether agents were useful negotiation partners.

Code basis:

- The web UI already supports human play.
- `Room.on_game_end` records non-bot users as `"Human"`.

If a new human study is not feasible before rebuttal:

- Clearly label existing human records as historical calibration.
- Avoid overstating them as a controlled human evaluation.

## Priority 6: Quantify Qualitative Failure Modes

The current qualitative examples are useful, but reviewers want systematic metrics.

### Ship and Resource Mispricing

Metrics:

- Ship trade discount: implied value of Ship in accepted trades.
- Auction overpayment rate: fraction of bids exceeding estimated downstream value.
- Ship retention rate before and after auction.
- Invalid or unaffordable bid rate.
- Correlation between ship spending and final score.

Code basis:

- `get_item_value` defines current heuristic item values.
- `submit_bid` records colony/research bids in game state.
- `TradeRecorder` records accepted trades and trade value gaps.

### Passive Bargaining

Metrics:

- Proposals per player per round.
- Counteroffer rate.
- Acceptance rate.
- Withdrawal rate.
- Ratio of targeted proposals to generic bulletin-board updates.
- Scarcity exploitation: whether a player holding scarce resources asks for a premium.

Code basis:

- `trade_proposal`, `withdraw_trade_proposal`, and `accept_trade_proposal` are structured game actions.
- LLM responses are already stored in `Brain.recent_responses`, but this is in-memory only.

Recommended change:

Persist action-level trajectories to disk so these metrics can be computed after runs.

### Short-Horizon Planning

Metrics:

- Early investment ratio: fraction of early resources spent on colonies, research, upgrades, or compounding converters.
- Converter utilization rate: usable converters actually run.
- Missed profitable converter count.
- End-game unused resource value.
- Correlation between early investment and final score.

Code basis:

- `produce` executes converters.
- Player state includes storage, factories, tech, and score.
- Current game snapshots can be serialized with `Game.to_dict`.

## Priority 7: System Ablations

Add small ablations to isolate the contribution of engineering choices.

Recommended ablations:

- Function calling on/off.
- Converter value hints on/off.
- Phase-aware modular callers vs a single generic caller.
- Asynchronous negotiation vs sequential stepping.

Code basis:

- `agent_function_calling_mode` is configurable.
- `prompt_converter_value_adding` is configurable.
- `Brain` already routes planning, trading, production, bidding, and picking through different callers.

Expected rebuttal value:

These experiments support the claim that the environment and agent harness are not merely a thin wrapper around the board game mechanics.

## Priority 8: Experimental Detail Cleanup

Fix reporting issues independent of new runs:

- Correct Figure 3 and Figure 4 captions.
- Reconcile model names across the main text and appendix.
- Report exact model identifiers.
- Report temperature and other API parameters.
- Report player count, rounds, species pool, random seeds, and failed-run filtering.
- Clarify how scores are normalized or not normalized.
- Mention code and trajectory release plans.

## Suggested Execution Order

1. Export quantitative self-play and Elo tables from existing records.
2. Add bootstrap confidence intervals for self-play means and Elo.
3. Run additional balanced Elo games.
4. Add species assignment and species-normalized analyses.
5. Implement or simulate rule-based baselines.
6. Persist action-level trajectories.
7. Compute systematic failure-mode metrics.
8. Add human or mixed human-LLM pilot results if time permits.

## Minimum Rebuttal Package

If time is limited, prioritize this package:

- Quantitative self-play table.
- Elo table with 95% bootstrap CI.
- Model-by-species assignment table.
- Expanded Elo tournament or a clear reliability caveat if expansion is incomplete.
- At least one simple rule baseline.
- Quantified versions of the three qualitative failure modes.

This directly addresses the highest-frequency reviewer criticisms.
