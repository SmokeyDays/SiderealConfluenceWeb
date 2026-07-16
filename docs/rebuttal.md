Reviewer 1
==========

**W1: Experimental parameters were underspecified.**
Thank you for pointing this out. We agree that the original manuscript did not make the experimental setup sufficiently explicit. Therefore, we add a consolidated experimental-settings table, including the number of completed games, player seats per game, number of rounds, species pool, model assignment procedure, model-call parameters, function-calling mode, and incomplete-run filtering rule. The settings are shown in Table 1.

[table_1]

In all LLM runs, agents use the same observation format, prompt templates, phase-specific caller architecture, action schema, and environment rules. Model calls are run with temperature 0 to reduce generation variance. The default game horizon is 6 rounds. Function calling is enabled through the same validated action interface for all LLM agents, with fallback handling when a provider does not return a valid tool call. Incomplete games are excluded from terminal-score and Elo computation, while diagnostic failures are retained in the corresponding statistics.

We also add two tables to clarify species asymmetry. Table 5 reports model-by-species assignment counts, and Table 6 reports the corresponding species-level terminal-score statistics.

[table_5]

[table_6]

**W2: Experimental scale was small or unclear.**
Thank you for raising this concern. We agree that the original text made the scale of the experiments unclear. A "game" in our setting is one completed multi-player rollout. In the heterogeneous tournament, each game has approximately five players, so one completed game yields about ten pairwise model comparisons. Thus, 20 games correspond to roughly 200 pairwise Elo observations, rather than only 20 binary comparisons. Nevertheless, we agree that this scale is still limited for stable model ranking, especially under asymmetric species assignments and stochastic auction outcomes.

During the rebuttal period, we added several additional completed runs. Because each full rollout is expensive and time-consuming, these new results do not fully eliminate uncertainty, but they allow us to report games, player seats, pairwise comparisons, and bootstrap confidence intervals more transparently. The homogeneous self-play results are shown in Table 3.

[table_3]

The heterogeneous tournament results are shown in Table 4. We will temper model-ranking claims accordingly and present the tournament results as relative-performance estimates under the collected schedule rather than as a definitive ranking.

[table_4]

**W3: Model names were inconsistent.**
Thank you for identifying this issue. We agree and will canonicalize model names across Section 5, Section 6, Appendix A, Appendix D, figures, and released records. The inconsistency arose from two issues. First, the model list in Section 5 was not updated after we added several additional models, which led to conflicts with later result sections and appendices. Second, DeepSeek's official `deepseek-chat` endpoint changed during the V4 release period, making some early records ambiguous. To avoid ambiguity, we discarded those records and reran DeepSeek experiments using the fixed Ark deployment of DeepSeek V3.2.

The canonical model names, record identifiers, exact deployment/API identifiers, providers, and included experiment types are shown in Table 2. In the revision, the DeepSeek entry used for the final experiments will be uniformly reported as DeepSeek V3.2. The Appendix D mention of DeepSeek-V4-Pro was an error and will be removed.

[table_2]

**W4: Human baseline.**
Thank you for the suggestion. We agree that a human calibration point is valuable. We organized volunteer human self-play sessions using the same web interface and game server. These sessions use the same environment state, action protocol, scoring rule, and terminal-score recorder as the LLM rollouts. The human/model calibration results are shown in Table 7.

[table_7]

We were also surprised that human players outperformed LLM agents by a large margin under the same game setting. A plausible explanation is that humans can negotiate through richer discussion patterns, while our current LLM agents interact mainly through structured bulletin-board posts and binding proposals. In addition, LLM context windows are substantially occupied by rules and state descriptions, leaving limited room for strategic deliberation. The gap may also indicate that the current agent architecture and prompts leave considerable room for improvement.

**W5: Typos and presentation errors.**
Thank you for identifying these errors. We will correct the Figure 4 caption so that it describes Elo ratings rather than duplicating the Figure 3 self-play caption. We will also rewrite the truncated Section 3 sentence around the observation function, make model names consistent across the main text and appendix, and proofread figure/table references.

**W6: Engineering contribution.**
Thank you for the concern about the nature of the contribution. We will revise the contribution statement to emphasize the reusable benchmark infrastructure. SidConArena provides an executable multi-agent evaluation harness for open-ended, positive-sum bargaining: structured private/public/market/interaction observations, phase-specific decision modules, a validated function-call interface, asynchronous negotiation, a trusted ledger for binding trades, deterministic production and auction engines, full trajectory logging, and a web interface that supports both LLM and human players under the same protocol.

We also add empirical characterization to support this contribution. Table 9 reports function-calling parse reliability. This statistic measures parse/schema failures after a model response is obtained; it does not include network errors, API timeouts, provider-side connection failures, or other model-call failures.

[table_9]

Table 10 reports signed trade gain/loss statistics under the environment's reference valuation, and Table 11 reports the signed exploitation matrix between model pairs. These diagnostics complement terminal scores and Elo by exposing valuation and trade-quality failures in executable records.

[table_10]

[table_11]

**W7: Reproducibility.**
Thank you for the reproducibility concern. We will release the implementation and analysis artifacts, including source code for the game server, web interface, LLM agent harness, and rule-based baseline; running logs for the experiments used in the paper; serialized game snapshots / room states in `pkl` format; prompt templates and function/action schemas; agent cards with canonical display names and exact model identifiers; configuration files; completed `game_records`; and scripts for generating the reported tables.

In summary, besides addressing the direct reviewer concerns, we add the following empirical materials to the revision: self-play score statistics (Table 3), heterogeneous Elo statistics (Table 4), model-by-species assignment counts (Table 5), species-level score statistics (Table 6), human/model calibration (Table 7), rule-baseline comparison (Table 8), function-calling parse reliability (Table 9), trade-value diagnostics (Table 10), and the signed exploitation matrix (Table 11).


Reviewer 2
==========

**W1: Baselines.**
Thank you for requesting stronger baselines. We implemented a deterministic fair-trade rule baseline and added it to the evaluation. The baseline uses the same public game state and action API as the LLM agents and receives no privileged hidden state. It accepts trades that are non-losing under the reference valuation, proposes approximately fair exchanges for missing resources, runs feasible converters greedily, and follows a conservative bidding rule. It is intentionally myopic, so it calibrates how far consistent local economic rules can go without language-based negotiation, opponent modeling, or long-horizon replanning.

The rule-baseline comparison is shown in Table 8. The rule baseline is also included in the heterogeneous tournament results in Table 4.

[table_8]

An exact terminal-utility-maximizing baseline is not a uniquely defined simple rule baseline in this setting: it would require assumptions about opponent policies, hidden private states, future negotiations, production choices, and auctions. We therefore use the tractable fair-trade policy above and make its local assumptions explicit rather than claiming global optimality. We also avoid labeling a hand-written scripted policy as "human-like" without behavioral data; instead, we report the volunteer human calibration in Table 7.

**W2: Systematic quantification of qualitative failure modes.**
Thank you for suggesting concrete behavioral metrics. We agree with the motivation of complementing representative trajectories with systematic quantitative evidence. However, several proposed quantities are not directly observable, model-independent metrics in our open-ended, asynchronous, multi-party setting; each requires additional assumptions that may introduce subjectivity.

A counteroffer rate requires defining what constitutes a response to a particular offer. An agent may revise a public proposal, approach another buyer, split a bundle, or preserve the original offer while soliciting alternatives. These actions can serve the same strategic function as a direct counteroffer. Similarly, an acceptance rate for Pareto-improving trades requires estimating whether a proposal improves both agents' state-dependent utilities, which depend on inventories, converters, remaining production opportunities, and future interactions. Scarcity exploitation also requires assumptions about whether public demand reflects true scarcity, strategic cheap talk, available substitutes, or future production.

For the auction, the difference between a bid and the reserve price is more accurately a priority premium than a direct overpayment: agents bid for selection order, and the reserve price is a participation floor rather than the player-specific value of the asset. Establishing true overpayment would require estimating the asset's state-dependent future yield, the opportunity cost of Ships, and the counterfactual outcome under alternative bids. Likewise, an early-investment ratio depends on author-chosen definitions of the early-game window, what counts as investment, and how heterogeneous assets are valued.

For these reasons, we add diagnostics that are directly and reproducibly derived from executable environment records. Table 9 reports function-calling parse reliability, Table 10 reports accepted-trade value transfer statistics, and Table 11 reports the signed model exploitation matrix. We explicitly interpret the latter two as reference-value transfer statistics rather than estimates of agents' latent utilities or globally optimal behavior.

**W3: Non-LLM calibration baseline.**
This is addressed by the fair-trade rule baseline described above. Its score statistics and comparison with LLM and human calibration results are reported in Table 8. The rule agent is deliberately simple and local, which makes it a useful calibration point: if an LLM fails to outperform it, the failure is not merely about interface compliance, but about economic valuation, negotiation, or planning beyond local fair exchange.

**W4: Generality beyond the SidConArena economy.**
Thank you for raising this important question about scope and generality. Cross-environment transfer is not a claim of this work. SidConArena is introduced as a controlled benchmark for open-ended, positive-sum economic interaction; its fixed resources and rules make agent behavior executable, reproducible, and quantitatively comparable. Our goal is to evaluate clearly defined capabilities, such as identifying complementary needs, bargaining under scarcity, resource allocation, and planning under delayed returns, across asymmetric roles within this environment. Testing whether the same patterns persist under other market mechanisms is valuable follow-up work, but is beyond the scope of introducing and validating this benchmark.

**W5: Experimental details and reproducibility.**
Thank you for pointing this out. We will release the complete implementation, experiment configurations, logs, serialized `pkl` states, prompts, action schemas, completed records, and analysis scripts. The consolidated experimental settings are shown in Table 1, and canonical model identifiers are shown in Table 2.

**W6: Figures 3 and 4.**
Thank you for identifying the repetitive captions and discussion. This is a presentation error. Figure 3 reports homogeneous self-play score distributions, whereas Figure 4 reports heterogeneous Elo estimates. We will correct the Figure 4 caption and remove repetitive discussion so that each figure's purpose and underlying sample size are stated clearly.

In summary, besides addressing the direct reviewer concerns, we add self-play score statistics (Table 3), heterogeneous Elo statistics (Table 4), model-by-species assignment counts (Table 5), species-level score statistics (Table 6), human/model calibration (Table 7), rule-baseline comparison (Table 8), function-calling parse reliability (Table 9), trade-value diagnostics (Table 10), and the signed exploitation matrix (Table 11).


Reviewer 3
==========

**W1: Relationship to Chen et al. (2024).**
Thank you for pointing us to *Put Your Money Where Your Mouth Is*. We agree that AucArena is relevant prior work and should have been cited and compared explicitly. Both environments use LLM agents to make decisions under resource or budget constraints and evaluate aspects of strategic planning and execution. AucArena conducts this evaluation through a sequence of open ascending-price auctions. In SidConArena, the auction appears as one subphase within each turn of a broader multi-agent economy.

Table 12 summarizes the structural comparison between the two environments.

[table_12]

Table 12. Structural comparison between AucArena and SidConArena.

| Dimension | AucArena | SidConArena |
| --- | --- | --- |
| Auction mechanism | Sequential, public ascending-price auctions | A sealed-bid auction subphase within each turn |
| Other interactions | Bid or withdraw during the auction | Natural-language negotiation, binding trades, converter production, bidding, and asset selection |
| Agent/economy structure | Bidders allocate budgets across items | Asymmetric agents have different inventories, converters, and production opportunities |
| Temporal dependency | Earlier purchases reduce the budget available for later items | Negotiation changes production feasibility; production changes later resources and bids; auctioned assets affect future production |
| Behavioral signals | Budget management, belief updating, replanning, and bid behavior | Trade valuation, bargaining behavior, converter utilization, cross-phase planning, and terminal economic outcomes |

AucArena studies strategic behavior in transparent, sequential, open ascending-price auctions: bidders allocate limited budgets across items, update beliefs and plans, and primarily optimize auction profit or item acquisition. SidConArena evaluates a negotiation-production-auction cycle repeated across turns. Asymmetric agents first negotiate binding exchanges over complementary resources, then use those resources in private production engines, and subsequently participate in a sealed-bid auction for persistent Colonies and Technologies. The inputs to the auction and its downstream consequences are therefore coupled with the surrounding economy.

Some auction-focused experiments can be studied in both environments, including bidding behavior, budget/resource allocation, and planning for future auction opportunities. However, the experiments and analyses in Sections 6.3-6.5 rely on interactions and trajectories specific to SidConArena's negotiation-production-auction cycle. The valuation analysis examines how agents price resources in binding bilateral trades relative to private production opportunities. The bargaining analysis examines whether an agent counteroffers, preserves optionality, or uses competing demand when multiple partners seek a scarce resource. The long-horizon analysis follows whether early trades and investments enable converter activation, compounded production, and late-game score conversion. These require negotiation messages, trade records, converter states, and cross-phase production histories that are not part of AucArena's auction protocol.

We will add Chen et al. (2024) to Related Work and discuss both the shared auction/planning elements and the different research questions supported by the two environments.

**W2: Limited empirical insights.**
Thank you for raising this important question. A terminal score indicates whether an agent performed poorly, but does not by itself explain why. SidConArena is designed to expose the intermediate trajectory that produces that outcome. Each LLM decision is associated with its turn and game phase, together with the observation, generated response, and structured action. The environment state records inventories, converter availability and activation, pending and completed trade proposals, submitted bids, asset allocations, and terminal outcomes. Because committed actions are validated before execution, the framework can distinguish interface- or rule-level failures from economically poor decisions that are nevertheless valid.

These records support phase-by-phase diagnosis. During negotiation, one can compare planned resource needs with proposed, accepted, and rejected trades. During production, one can examine whether acquired resources make planned converters feasible and whether the agent actually activates them. During the auction, one can relate Ships preserved from earlier phases, submitted bids, and long-term assets acquired. Across turns, these records make it possible to trace whether early trades and investments lead to converter activation, compounded production, and late-game score conversion.

The current paper already illustrates three uses of this diagnostic structure: valuation grounding, passive bargaining, and long-horizon planning failures. We agree that the current error analysis mainly presents representative cases rather than systematic frequencies and model-wise breakdowns. Therefore, we add aggregate diagnostics derived from executable records: function-calling parse reliability (Table 9), trade-value diagnostics (Table 10), and a signed exploitation matrix (Table 11). These supplement the trajectory examples without relying on post-hoc annotation of ambiguous bargaining behavior.

**W3: Overcomplicated terminology and figures.**
Thank you for pointing out the presentation issue. We agree that the current figures and terminology make the execution process appear more complicated than necessary. The game has three phases: negotiation, production, and auction. Separately, the implementation uses a four-step agent-environment loop: construct an observation, select the phase-specific decision module, generate a structured action, and validate/execute that action.

We will revise the relevant figures to show these structures separately and use plainer terminology. "Phase-aware agent brain" will be described as a phase-specific dispatcher that selects the relevant prompt and action schema. "Neural-symbolic action interface" will be described as a validated function-call interface that converts an LLM response into a machine-checkable trade, production, bidding, or item-selection action.

**W4: Clarification of converters, Ships, and the Sidereal Confluence economic structure.**
Thank you for pointing out that the paper assumes too much familiarity with the source game. We will add a plain-language overview and a worked example before the formalization.

A converter is a reusable input-output production rule. It consumes a specified bundle of resources and produces another bundle; normally, each converter can be activated at most once per turn, and its output becomes part of the subsequent state. Ships are tradable resources and the bidding currency for Colonies and Technologies. During the auction, an agent allocates its available Ships across two tracks. Its bid determines selection priority, and the full bid is paid if the agent selects an asset. Colonies and Technologies provide persistent production opportunities, so spending Ships creates a trade-off between current liquid resources and future productive capacity.

By saying that SidConArena is based on the economic structure of *Sidereal Confluence*, we mean that it adopts this abstract cycle: asymmetric agents trade complementary resources, activate converter-based production, acquire long-term productive assets, and maximize terminal economic value. We will explain this structure without requiring knowledge of the commercial board game and distinguish the abstract mechanics from the executable LLM-agent framework.

**W5: Reproducibility and underspecified experimental settings.**
Thank you for the reproducibility assessment. We will add a consolidated experimental-settings table (Table 1), a canonical model table (Table 2), and release code, logs, serialized `pkl` states, prompts, action schemas, completed records, and evaluation scripts.

In summary, besides addressing the direct reviewer concerns, we add self-play score statistics (Table 3), heterogeneous Elo statistics (Table 4), model-by-species assignment counts (Table 5), species-level score statistics (Table 6), human/model calibration (Table 7), rule-baseline comparison (Table 8), function-calling parse reliability (Table 9), trade-value diagnostics (Table 10), and the signed exploitation matrix (Table 11).
