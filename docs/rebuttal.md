Reviewer 1:

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
- An Elo table with regularized Bradley-Terry/Elo values, number of completed games, number of pairwise comparisons, observed pairwise win rate, and bootstrap 95% confidence intervals.
- A model-by-species coverage table.
- A species-level table reporting average score by species, so that readers can judge the impact of asymmetric starting conditions.

We will temper the wording of ranking claims accordingly. Rather than presenting the small tournament as a definitive ranking, we will describe it as a relative-performance estimate under the collected tournament schedule, with uncertainty explicitly shown. The expanded schedule is balanced so that each model plays each species at least once and model pairs co-occur more evenly.

For the Elo estimate, we will use a regularized Bradley-Terry model rather than an unregularized fit. The unregularized estimate is unstable in small tournaments because some model pairs have very few comparisons and can exhibit near-complete separation. We therefore add a symmetric weak prior equivalent to one virtual drawn comparison between each model pair. This keeps estimates finite and shrinks unsupported differences toward 1500, while preserving the observed ranking signal. We also report the raw observed pairwise win rate so the regularized Elo values remain interpretable.

The quantitative result tables will be inserted in the revision in the following format:

| Model / baseline | Completed games | Player seats | Mean score | Median | Std. | Min | Max | 95% bootstrap CI |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD |

| Model / baseline | Regularized Elo | 95% bootstrap CI | Completed games | Player seats | Pairwise comparisons | Observed pairwise win rate |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| TBD | TBD | TBD | TBD | TBD | TBD | TBD |

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

Reviewer 2:

W1 baseline

我们实现了一个 fair-trade 的 agent；比较 LLMs 的情况如下；utility-maximizing 在无法形式化 LLMs based agent 的行为的情况下是不可实现的； human-like negotiation agent 较复杂，我们承认我们难以实现；

加上 fair-trade agent 后的 elo 如下

除此以外，我们还添加了人类 baseline；

**w2. Systematic quantification of the qualitative failure modes**

Thank you for suggesting concrete behavioral metrics. We agree with the motivation of complementing representative trajectories with systematic quantitative evidence. However, the proposed quantities are not directly observable, model-independent metrics in our open-ended, asynchronous, multi-party setting; each requires additional assumptions that may introduce substantial subjectivity.

First, a **counteroffer rate** requires an unambiguous definition of what constitutes a response to a particular offer. An agent may revise a public proposal, approach another buyer, split a bundle, or preserve the original offer while soliciting alternatives. These actions can serve the same strategic function as a direct counteroffer. Moreover, immediately accepting an offer is not necessarily passive if that offer is already preferable to the available alternatives. A counteroffer statistic would therefore depend on an author-chosen response window, proposal-lineage rule, and definition of bargaining opportunity.

Second, an **acceptance rate for Pareto-improving trades** requires estimating whether a proposal improves both agents’ state-dependent utilities, which depend on their converters, inventories, remaining production opportunities, and future interactions. Consequently, this metric would require additional assumptions for classifying both accepted and unaccepted proposals. In our setting, we instead use a closely related but directly reproducible measure: the **number and rate of accepted trades in which an agent incurs a negative transfer under the environment’s fixed reference valuation**. This captures trade-quality failures using explicit environment records without requiring an additional utility estimator.

Similarly, **scarcity exploitation** requires defining scarcity from more than resource counts or expressed demand. Publicly stated demand may be strategic cheap talk, resources may have substitutes, and future production can change scarcity within the same turn. In addition, extracting the largest possible premium is not always optimal in a repeated positive-sum economy, where reciprocity and future cooperation also matter.

For the auction, the difference between a bid and the reserve price is more accurately a **priority premium** than an overpayment: agents bid for selection order, and the reserve price is a participation floor rather than the player-specific value of the asset. Establishing true overpayment would require estimating the asset’s state-dependent future yield, the opportunity cost of Ships, and the counterfactual outcome under alternative bids.

Finally, an **early-investment ratio** depends on author-chosen definitions of the early-game window, what counts as investment, and how heterogeneous assets are valued. Optimal investment timing also differs across species, initial endowments, converter structures, and auction outcomes. A high early-investment ratio therefore does not necessarily indicate better long-horizon planning, nor does a low ratio by itself establish myopia.

For these reasons, treating these quantities as objective ground-truth statistics could introduce additional modeling assumptions rather than necessarily improving rigor. Instead, we have added three diagnostics that are directly and reproducibly derived from executable environment records: **(1)** the number and rate of failed function calls, which measure failures to translate decisions into valid actions; **(2)** the number and rate of accepted trades in which an agent incurs a negative transfer under the environment’s fixed reference valuation; and **(3)** a pairwise **model exploitation matrix**, which aggregates signed reference-value transfers between models and is normalized by their observed interactions. We explicitly interpret the latter two as reference-value transfer statistics rather than estimates of agents’ latent utilities or globally optimal behavior. These aggregate diagnostics complement the trajectory examples while remaining machine-verifiable and free from post-hoc behavioral annotation.

**w3. Non-LLM calibration baseline**

We thank the reviewer for requesting non-LLM calibration. We implemented a deterministic **utility-guided fair-trade agent** and added it to the heterogeneous tournament. It uses the same observations and action API as the LLM agents and receives no privileged hidden state. It (i) accepts non-losing trades under the reference valuation, (ii) proposes approximately fair exchanges for inputs missing from its highest-gain converter, (iii) greedily runs feasible converters with non-negative immediate gain, and (iv) follows a fixed conservative bidding policy. It is intentionally myopic and therefore measures how far consistent local economic rules can progress without language-based negotiation, opponent modeling, or long-horizon replanning. The agent obtains an Elo of **[ELO, 95% CI, N games, rank]**. **[INSERT ONE-SENTENCE VERIFIED INTERPRETATION.]**

An exact terminal-utility-maximizing policy is not a uniquely defined simple rule baseline: it would require assumptions about opponent policies and private states and solving the multi-agent POSG over future negotiations, production, and auctions. We therefore use the tractable utility-guided policy above and make its local assumptions explicit rather than claiming global optimality. We also do not label a hand-written negotiation policy “human-like,” since a hand-written “human-like” agent would require an arbitrary choice of anchoring, concession, counteroffer, and reciprocity rules. Without human behavioral data, such an agent would be another authored heuristic rather than a validated human baseline. Instead, we include a human baseline under the same environment rules and interface **[INSERT N AND RESULT]**, and will add the rule specification, code, game counts, and uncertainty estimates to the revision.

**W4. Generality beyond the SidConArena economy**

Thank you for raising this important question about the scope and generality of our findings. We respectfully clarify that cross-environment transfer is not a claim of this work. SidConArena is introduced as a controlled benchmark for open-ended, positive-sum economic interaction; its fixed resources and rules make agent behavior executable, reproducible, and quantitatively comparable. Our goal is to evaluate clearly defined capabilities—such as identifying complementary needs, bargaining under scarcity, resource allocation, and planning under delayed returns—across asymmetric roles within this environment, rather than to claim unchanged transfer to every market setting. Testing whether the same patterns persist under other market mechanisms is valuable follow-up work, but is beyond the scope of introducing and validating this benchmark.

**w5. Experimental details and reproducibility**

Thank you for pointing this out. We will release the complete implementation and experiment configurations, and expand the appendix with the exact model-call parameters, number of games, species-assignment procedure, Elo computation. These details will be summarized in the following table to make the experiments fully reproducible. [插入一个数据的表格，可能要包括 model-call parameters, number of games, species-assignment procedure,Elo computation(我怀疑这个论文里除了具体的算式基本都写了)]

w6. Figures 3 and 4

Thank you for identifying the repetitive captions and discussion. This is a presentation error. Fig. 3 reports homogeneous self-play score distributions, whereas Fig. 4 reports heterogeneous Elo estimates. We will correct the Fig. 4 caption and remove repetitive discussion so that each figure's purpose and underlying sample size are stated clearly.

Reviewer 3:

**W1: Relationship to Chen et al. (2024).**

Thank you for pointing us to *Put Your Money Where Your Mouth Is*. We agree that AucArena is relevant prior work and should have been cited and compared explicitly. Both environments use LLM agents to make auction decisions under resource or budget constraints and evaluate aspects of strategic planning and execution. AucArena conducts this evaluation through a sequence of open ascending-price auctions. In SidConArena, the auction appears as one subphase within each turn of a broader multi-agent economy.

AucArena studies strategic behavior in transparent, sequential, open ascending-price auctions: bidders allocate a limited budget across items, update their beliefs and plans, and primarily optimize auction profit or item acquisition. SidConArena evaluates a negotiation–production–auction cycle repeated across turns. Asymmetric agents first negotiate binding exchanges over complementary resources, then use those resources in private production engines, and subsequently participate in a sealed-bid auction for persistent Colonies and Technologies. The inputs to the auction and its downstream consequences are therefore coupled with the surrounding economy. An early trade may enable a previously infeasible converter, alter the resources and Ships available in later turns, affect access to long-term production assets, and ultimately change terminal value.

**Table 1.** Structural comparison between AucArena and SidConArena.

<table>
<thead>
<tr><th>Dimension</th><th>AucArena</th><th>SidConArena</th></tr>
</thead>
<tbody>
<tr><td>Auction mechanism</td><td>Sequential, public ascending-price auctions</td><td>A sealed-bid auction subphase within each turn</td></tr>
<tr><td>Other interactions</td><td>Bid or withdraw during the auction</td><td>Natural-language negotiation, binding trades, converter production, bidding, and asset selection</td></tr>
<tr><td>Agent/economy structure</td><td>Bidders allocate budgets across items</td><td>Asymmetric agents have different inventories, converters, and production opportunities</td></tr>
<tr><td>Temporal dependency</td><td>Earlier purchases reduce the budget available for later items</td><td>Negotiation changes production feasibility; production changes later resources and bids; auctioned assets affect future production</td></tr>
<tr><td>Behavioral signals</td><td>Budget management, belief updating, replanning, and bid behavior</td><td>Trade valuation, counteroffers, converter utilization, cross-phase planning, and terminal economic outcomes</td></tr>
</tbody>
</table>

**Can the same experiments be conducted and the same conclusions be reached using AucArena?** Some auction-focused experiments can be studied in both environments, including bidding behavior, budget/resource allocation, and planning for future auction opportunities. The broad conclusions that stronger models often perform better and that strategic planning remains challenging may therefore appear in both studies.

However, the experiments and analyses in Secs. 6.3–6.5 rely on interactions and trajectories that are specific to the negotiation–production–auction cycle. The valuation analysis in Sec. 6.3 examines how agents price resources in binding bilateral trades relative to their private production opportunities. The bargaining analysis in Sec. 6.4 examines whether an agent counteroffers, preserves optionality, or uses competing demand when multiple partners seek a scarce resource. The long-horizon analysis in Sec. 6.5 follows whether early trades and investments enable converter activation, compounded production, and late-game score conversion. These experiments require negotiation messages, trade records, converter states, and cross-phase production histories that are not part of AucArena's auction protocol. Thus, while the two frameworks can support related auction and planning conclusions, they expose different behavioral evidence and support different failure analyses.

We thank the reviewer again for bringing this relevant work to our attention. We will add Chen et al. (2024) to Related Work and discuss both the shared auction/planning elements and the different research questions supported by the two environments.

**W2: Concern about limited empirical insights.**

Thank you for raising this important question. A terminal score indicates whether an agent performed poorly, but does not by itself explain why. SidConArena is designed to expose the intermediate trajectory that produces that outcome. Each LLM decision is associated with its turn and game phase, together with the observation, generated response, and structured action. The environment state records inventories, converter availability and activation, pending and completed trade proposals, submitted bids, asset allocations, and terminal outcomes. Because committed actions are validated before execution, the framework can first distinguish interface- or rule-level failures from economically poor decisions that are nevertheless valid.

These records support a phase-by-phase diagnosis. During negotiation, one can compare an agent's planned resource needs with its proposed, accepted, and rejected trades, and inspect whether it counteroffers or immediately accepts an offer. During production, one can examine whether the acquired resources make planned converters feasible and whether the agent actually activates them. During the auction, one can relate the Ships preserved from earlier phases, the submitted bids, and the long-term assets acquired. Across turns, these records make it possible to trace whether early trades and investments lead to converter activation, compounded production, and late-game score conversion. The framework therefore allows researchers to move from a scalar observation—such as a low terminal score—to the phase and decision at which the trajectory first becomes economically ineffective.

The current paper already illustrates three uses of this diagnostic structure. Sec. 6.3 separates syntactically valid actions from valuation grounding by comparing recorded Ship-related trades with the local reference valuation. Sec. 6.4 uses negotiation messages and proposal records to identify passive bargaining, such as accepting the first reasonable offer without counteroffering despite competing demand. Sec. 6.5 follows cross-turn state and production changes to show trajectories in which locally reasonable actions fail to produce early investment, compounded production, or effective late-game conversion.

We agree that the current error analysis mainly presents representative cases rather than systematic frequencies, model-wise breakdowns, or their relation to terminal outcomes, and we will strengthen this analysis. We believe identifying the causal source of each failure is a substantially broader problem because outcomes emerge from coupled valuations, opponent strategies, resource constraints, and cross-phase interactions. Our focus is to provide a benchmark that exposes and localizes these failures, rather than a complete economic causal analysis; we will clarify this scope and leave rigorous causal source identification to future work.

**W3: Concern about overcomplicated terminology and figures.**

We agree that the current presentation makes the execution process appear more complicated than necessary. The confusion also reveals that we did not clearly separate two different structures. The game has three phases: negotiation, production, and auction. Separately, the implementation uses a four-step agent–environment loop: construct an observation, select the phase-specific decision module, generate a structured action, and validate/execute that action.

We will revise the relevant figures to show these structures separately and use plainer terminology. “Phase-aware agent brain” will be described as a **phase-specific dispatcher** that selects the relevant prompt and action schema. “Neural-symbolic action interface” will be described as a **validated function-call interface** that converts an LLM response into a machine-checkable trade, production, bidding, or item-selection action. 

**W4: Clarification of converters, Ships, and the Sidereal Confluence economic structure.**

We agree that the paper currently assumes too much familiarity with the source game. We will add a plain-language overview and a worked example before the formalization.

A **converter** is a reusable input–output production rule. It consumes a specified bundle of resources and produces another bundle; normally, each converter can be activated at most once per turn, and its output becomes part of the subsequent state. 

**Ships** are tradable resources and the bidding currency for Colonies and Technologies. During the auction, an agent allocates its available Ships across two tracks. Its bid determines selection priority, and the full bid is paid if the agent selects an asset. Colonies and Technologies provide persistent production opportunities, so spending Ships creates a trade-off between current liquid resources and future productive capacity.

By saying that SidConArena is based on the economic structure of *Sidereal Confluence*, we mean that it adopts this abstract cycle: asymmetric agents trade complementary resources, activate converter-based production, acquire long-term productive assets, and maximize terminal economic value. We will explain this structure without requiring knowledge of the commercial board game and distinguish the abstract mechanics from the executable LLM-agent framework.

**W5: Reproducibility and underspecified experimental settings.**

We also appreciate the reproducibility assessment. We will add a consolidated experimental-settings table specifying the exact model/API versions, token limits, number of homogeneous and heterogeneous games, species/seat assignment, and Elo computation procedure. We will open-source the environment code, complete prompts, action schemas and evaluation scripts to facilitate reproduction and follow-up research.
