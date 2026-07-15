import argparse
import csv
import json
import math
import os
import random
import sys
from collections import Counter, defaultdict
from statistics import mean, median, stdev


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
if REPO_ROOT not in sys.path:
  sys.path.insert(0, REPO_ROOT)


DEFAULT_RECORD_FILES = [
  os.path.join(CURRENT_DIR, "game_records.json"),
  os.path.join(CURRENT_DIR, "game_records_local.json"),
]

BT_PSEUDO_DRAWS = 1.0


MODEL_DISPLAY_NAMES = {
  "gpt-4o-mini": "GPT-4o Mini",
  "o3-mini": "o3 Mini",
  "gpt-5": "GPT-5",
  "gemini-3-flash-preview": "Gemini 3 Flash Preview",
  "claude-opus-4": "Claude Opus 4",
  "qwen-plus": "Qwen Plus",
  "deepseek-v3.2": "DeepSeek V3.2",
  "deepseek-chat": "DeepSeek Chat",
  "doubao-seed-2.0-lite": "Doubao Seed 2.0 Lite",
  "doubao-seed-2.0-pro": "Doubao Seed 2.0 Pro",
  "glm-4.7": "GLM-4.7",
  "rule-fair": "Rule Fair Trade",
  "human": "Human",
}


RULE_MODELS = {"rule-fair"}
HUMAN_MODELS = {"human", "Human"}
DEPRECATED_MODELS = {"deepseek-chat"}


def load_records(paths):
  records = []
  seen_records = set()
  for path in paths:
    if not os.path.exists(path):
      continue
    with open(path, "r", encoding="utf-8") as f:
      data = json.load(f)
    if not isinstance(data, list):
      continue
    for index, record in enumerate(data):
      if not isinstance(record, dict):
        continue
      record_key = json.dumps(record, sort_keys=True, ensure_ascii=False)
      if record_key in seen_records:
        continue
      seen_records.add(record_key)
      record = dict(record)
      record["_record_uid"] = len(records)
      records.append(record)
  return records


def iter_results(records, exp_type=None):
  for record in records:
    if exp_type is not None and record.get("exp_type") != exp_type:
      continue
    for result in record.get("results", []):
      if not isinstance(result, dict):
        continue
      model = result.get("model", "Unknown")
      try:
        score = float(result.get("score", 0) or 0)
      except (TypeError, ValueError):
        continue
      if model in DEPRECATED_MODELS:
        continue
      yield record, model, result.get("specie", "Unknown"), score


def fmt_number(value, digits=2):
  if value is None:
    return "N/A"
  if isinstance(value, int):
    return str(value)
  if isinstance(value, float):
    if math.isnan(value):
      return "N/A"
    return f"{value:.{digits}f}"
  return str(value)


def summarize_scores(
  records,
  exp_type=None,
  include_models=None,
  exclude_models=None,
  include_species_coverage=False,
):
  include_models = set(include_models or [])
  exclude_models = set(exclude_models or [])
  scores_by_model = defaultdict(list)
  games_by_model = defaultdict(set)
  species_by_model = defaultdict(Counter)

  for record, model, specie, score in iter_results(records, exp_type=exp_type):
    if include_models and model not in include_models:
      continue
    if model in exclude_models:
      continue
    scores_by_model[model].append(score)
    games_by_model[model].add(record.get("_record_uid", record.get("exp_name")))
    species_by_model[model][specie] += 1

  rows = []
  for model, scores in sorted(scores_by_model.items()):
    row = {
      "Model / baseline": MODEL_DISPLAY_NAMES.get(model, model),
      "Model id": model,
      "Completed games": len(games_by_model[model]),
      "Player seats": len(scores),
      "Mean score": mean(scores),
      "Median": median(scores),
      "Std.": stdev(scores) if len(scores) > 1 else 0.0,
      "Min": min(scores),
      "Max": max(scores),
      "95% bootstrap CI": bootstrap_mean_ci_str(scores),
    }
    if include_species_coverage:
      row["Species coverage"] = format_counter(species_by_model[model])
    rows.append(row)
  return rows


def bootstrap_mean_ci(values, iterations=1000, alpha=0.05, seed=0):
  if not values:
    return None, None
  rng = random.Random(seed)
  means = []
  for _ in range(iterations):
    sample = [values[rng.randrange(len(values))] for _ in values]
    means.append(mean(sample))
  means.sort()
  low_index = int((alpha / 2) * (len(means) - 1))
  high_index = int((1 - alpha / 2) * (len(means) - 1))
  return means[low_index], means[high_index]


def bootstrap_mean_ci_str(values):
  low, high = bootstrap_mean_ci(values)
  if low is None:
    return "N/A"
  return f"[{low:.2f}, {high:.2f}]"


def format_counter(counter):
  if not counter:
    return ""
  return ", ".join(f"{key}:{value}" for key, value in sorted(counter.items()))


def build_seat_pairwise(records, exp_type="elo_exp"):
  pairwise_wins = defaultdict(float)
  pairwise_counts = defaultdict(int)
  model_set = set()
  model_games = defaultdict(set)
  model_seats = defaultdict(int)
  species_by_model = defaultdict(Counter)

  for record in records:
    if exp_type is not None and record.get("exp_type") != exp_type:
      continue
    record_uid = record.get("_record_uid", record.get("exp_name"))
    seats = []
    for result in record.get("results", []):
      if not isinstance(result, dict):
        continue
      model = result.get("model", "Unknown")
      specie = result.get("specie", "Unknown")
      try:
        score = float(result.get("score", 0) or 0)
      except (TypeError, ValueError):
        continue
      if model in DEPRECATED_MODELS:
        continue
      seats.append((model, specie, score))
      model_set.add(model)
      model_games[model].add(record_uid)
      model_seats[model] += 1
      species_by_model[model][specie] += 1

    for i in range(len(seats)):
      for j in range(i + 1, len(seats)):
        left_model, _, left_score = seats[i]
        right_model, _, right_score = seats[j]
        if left_model == right_model:
          continue
        pairwise_counts[(left_model, right_model)] += 1
        pairwise_counts[(right_model, left_model)] += 1
        if left_score > right_score:
          pairwise_wins[(left_model, right_model)] += 1.0
        elif right_score > left_score:
          pairwise_wins[(right_model, left_model)] += 1.0
        else:
          pairwise_wins[(left_model, right_model)] += 0.5
          pairwise_wins[(right_model, left_model)] += 0.5

  return {
    "models": sorted(model_set),
    "wins": pairwise_wins,
    "counts": pairwise_counts,
    "games": model_games,
    "seats": model_seats,
    "species": species_by_model,
  }


def compute_elo_from_pairwise(pairwise, pseudo_draws=BT_PSEUDO_DRAWS, max_iter=500, tol=1e-9):
  models = pairwise["models"]
  pairwise_wins = pairwise["wins"]
  pairwise_counts = pairwise["counts"]
  active_models = [
    model for model in models
    if sum(pairwise_counts[(model, opponent)] for opponent in models if opponent != model) > 0
  ]
  if len(active_models) < 2:
    return {}

  strengths = {model: 1.0 for model in active_models}
  for _ in range(max_iter):
    updated_strengths = {}
    max_relative_change = 0.0
    for model in active_models:
      wins = sum(
        pairwise_wins[(model, opponent)] + pseudo_draws / 2
        for opponent in active_models
        if opponent != model
      )
      denom = 0.0
      for opponent in active_models:
        if opponent == model:
          continue
        comparisons = pairwise_counts[(model, opponent)] + pseudo_draws
        if comparisons:
          denom += comparisons / (strengths[model] + strengths[opponent])
      updated = strengths[model] if denom <= 0 else max(wins / denom, 1e-12)
      updated_strengths[model] = updated
      max_relative_change = max(
        max_relative_change,
        abs(updated - strengths[model]) / max(strengths[model], 1e-12),
      )

    geo_mean = math.exp(sum(math.log(value) for value in updated_strengths.values()) / len(updated_strengths))
    strengths = {
      model: max(value / geo_mean, 1e-12)
      for model, value in updated_strengths.items()
    }
    if max_relative_change < tol:
      break

  mean_log_strength = sum(math.log(strengths[model]) for model in active_models) / len(active_models)
  return {
    model: 1500.0 + (400.0 / math.log(10)) * (math.log(strengths[model]) - mean_log_strength)
    for model in active_models
  }


def bootstrap_elo_ci(records, models, iterations=5000, exp_type="elo_exp", seed=0):
  elo_records = [record for record in records if record.get("exp_type") == exp_type]
  if not elo_records:
    return {model: "N/A" for model in models}
  rng = random.Random(seed)
  samples_by_model = defaultdict(list)
  for _ in range(iterations):
    sample = [elo_records[rng.randrange(len(elo_records))] for _ in elo_records]
    pairwise = build_seat_pairwise(sample, exp_type=exp_type)
    elos = compute_elo_from_pairwise(pairwise)
    for model, value in elos.items():
      samples_by_model[model].append(value)

  ci = {}
  for model in models:
    values = sorted(samples_by_model.get(model, []))
    if not values:
      ci[model] = "N/A"
      continue
    low = values[int(0.025 * (len(values) - 1))]
    high = values[int(0.975 * (len(values) - 1))]
    ci[model] = f"[{low:.1f}, {high:.1f}]"
  return ci


def table_4_elo(records):
  pairwise = build_seat_pairwise(records, exp_type="elo_exp")
  elos = compute_elo_from_pairwise(pairwise)
  ci = bootstrap_elo_ci(records, pairwise["models"])
  rows = []
  for model in sorted(elos, key=lambda key: elos[key], reverse=True):
    comparisons = sum(
      pairwise["counts"][(model, opponent)]
      for opponent in pairwise["models"]
      if opponent != model
    )
    wins = sum(
      pairwise["wins"][(model, opponent)]
      for opponent in pairwise["models"]
      if opponent != model
    )
    rows.append({
      "Model / baseline": MODEL_DISPLAY_NAMES.get(model, model),
      "Model id": model,
      "Regularized Elo": elos[model],
      "95% bootstrap CI": ci.get(model, "N/A"),
      "Completed games": len(pairwise["games"][model]),
      "Player seats": pairwise["seats"][model],
      "Pairwise comparisons": comparisons,
      "Observed pairwise win rate": wins / comparisons if comparisons else None,
    })
  return rows


def table_5_model_by_species(records):
  species = sorted({
    specie for _, model, specie, _ in iter_results(records)
    if model not in HUMAN_MODELS
  })
  counts = defaultdict(Counter)
  for _, model, specie, _ in iter_results(records):
    if model in HUMAN_MODELS:
      continue
    counts[model][specie] += 1
  rows = []
  for model in sorted(counts):
    row = {
      "Model / baseline": MODEL_DISPLAY_NAMES.get(model, model),
      "Model id": model,
    }
    for specie in species:
      row[specie] = counts[model][specie]
    row["Total seats"] = sum(counts[model].values())
    rows.append(row)
  return rows


def table_6_species_scores(records):
  scores = defaultdict(list)
  for _, model, specie, score in iter_results(records):
    if model in HUMAN_MODELS:
      continue
    scores[specie].append(score)
  rows = []
  for specie in sorted(scores):
    values = scores[specie]
    rows.append({
      "Species": specie,
      "Seats": len(values),
      "Mean score": mean(values),
      "Median": median(values),
      "Std.": stdev(values) if len(values) > 1 else 0.0,
      "Min": min(values),
      "Max": max(values),
      "95% bootstrap CI": bootstrap_mean_ci_str(values),
    })
  return rows


def table_7_human_and_model_calibration(records):
  scores_by_model = defaultdict(list)
  games_by_model = defaultdict(set)
  player_nums_by_model = defaultdict(list)

  for record in records:
    results = [
      result for result in record.get("results", [])
      if isinstance(result, dict)
      and result.get("model") not in DEPRECATED_MODELS
    ]
    if not results:
      continue
    player_num = len(results)
    record_uid = record.get("_record_uid", record.get("exp_name"))
    seen_models = set()
    for result in results:
      model = result.get("model", "Unknown")
      try:
        score = float(result.get("score", 0) or 0)
      except (TypeError, ValueError):
        continue
      scores_by_model[model].append(score)
      games_by_model[model].add(record_uid)
      if model not in seen_models:
        player_nums_by_model[model].append(player_num)
        seen_models.add(model)

  rows = []
  for model in sorted(scores_by_model):
    values = scores_by_model[model]
    player_nums = player_nums_by_model[model]
    rows.append({
      "Model / baseline": MODEL_DISPLAY_NAMES.get(model, model),
      "Model id": model,
      "Completed games": len(games_by_model[model]),
      "Average player num": mean(player_nums) if player_nums else 0,
      "Mean score": mean(values),
      "Median": median(values),
      "Std.": stdev(values) if len(values) > 1 else 0.0,
      "Min": min(values),
      "Max": max(values),
      "95% bootstrap CI": bootstrap_mean_ci_str(values),
    })
  return rows


def table_8_rule_comparison(records):
  return summarize_scores(
    records,
    include_models=RULE_MODELS | HUMAN_MODELS | {
      model for _, model, _, _ in iter_results(records)
      if model not in RULE_MODELS and model not in HUMAN_MODELS
    },
  )


def summarize_record_statistics(records):
  fc_by_model = defaultdict(lambda: {"attempts": 0, "successes": 0, "failures": 0})
  trade_by_model = defaultdict(lambda: {
    "games": 0,
    "trade_count": 0.0,
    "gain_count": 0.0,
    "loss_count": 0.0,
    "net_value": 0.0,
    "gain_amount": 0.0,
    "loss_amount": 0.0,
  })
  exploitation_totals = defaultdict(float)
  exploitation_pair_games = defaultdict(int)
  exploitation_observed_pairs = defaultdict(int)
  models_in_stats_records = set()

  for record in records:
    stats = record.get("statistics")
    if not isinstance(stats, dict):
      continue
    models_in_record = {
      result.get("model")
      for result in record.get("results", [])
      if isinstance(result, dict)
      and result.get("model")
      and result.get("model") not in DEPRECATED_MODELS
    }
    models_in_stats_records.update(models_in_record)
    for model in models_in_record:
      trade_by_model[model]["games"] += 1
    for left in models_in_record:
      for right in models_in_record:
        exploitation_pair_games[(left, right)] += 1

    for model, model_stats in stats.get("function_calling", {}).get("by_model", {}).items():
      fc_by_model[model]["attempts"] += int(model_stats.get("attempts", 0) or 0)
      fc_by_model[model]["successes"] += int(model_stats.get("successes", 0) or 0)
      fc_by_model[model]["failures"] += int(model_stats.get("failures", 0) or 0)

    trade_stats = stats.get("trade_value", {}).get("by_model", {})
    if not trade_stats:
      trade_stats = stats.get("trade_loss", {}).get("by_model", {})
    for model, model_stats in trade_stats.items():
      bucket = trade_by_model[model]
      bucket["trade_count"] += float(model_stats.get("trade_count", model_stats.get("loss_count", 0)) or 0)
      bucket["gain_count"] += float(model_stats.get("gain_count", 0) or 0)
      bucket["loss_count"] += float(model_stats.get("loss_count", 0) or 0)
      bucket["net_value"] += float(model_stats.get("net_value", -float(model_stats.get("loss_amount", 0) or 0)) or 0)
      bucket["gain_amount"] += float(model_stats.get("gain_amount", 0) or 0)
      bucket["loss_amount"] += float(model_stats.get("loss_amount", 0) or 0)

    matrix = stats.get("exploitation_matrix", {}).get("by_model", {})
    for beneficiary, losers in matrix.items():
      if not isinstance(losers, dict):
        continue
      for loser, amount in losers.items():
        exploitation_totals[(beneficiary, loser)] += float(amount or 0)
        exploitation_observed_pairs[(beneficiary, loser)] += 1

  return (
    fc_by_model,
    trade_by_model,
    exploitation_totals,
    exploitation_pair_games,
    exploitation_observed_pairs,
    models_in_stats_records,
  )


def table_9_function_calling(records):
  fc_by_model, _, _, _, _, _ = summarize_record_statistics(records)
  rows = []
  for model in sorted(fc_by_model):
    stats = fc_by_model[model]
    attempts = stats["attempts"]
    rows.append({
      "Model / baseline": MODEL_DISPLAY_NAMES.get(model, model),
      "Model id": model,
      "Attempts": attempts,
      "Successes": stats["successes"],
      "Parse failures": stats["failures"],
      "Failure rate": stats["failures"] / attempts if attempts else None,
    })
  return rows


def table_10_trade_value(records):
  _, trade_by_model, _, _, _, _ = summarize_record_statistics(records)
  rows = []
  for model in sorted(trade_by_model):
    stats = trade_by_model[model]
    games = stats["games"]
    trade_count = stats["trade_count"]
    rows.append({
      "Model / baseline": MODEL_DISPLAY_NAMES.get(model, model),
      "Model id": model,
      "Games with stats": games,
      "Trade count": trade_count,
      "Avg. signed trade value/game": stats["net_value"] / games if games else 0,
      "Avg. gain amount/game": stats["gain_amount"] / games if games else 0,
      "Avg. loss amount/game": stats["loss_amount"] / games if games else 0,
      "Loss-trade rate": stats["loss_count"] / trade_count if trade_count else None,
      "Gain trades": stats["gain_count"],
      "Loss trades": stats["loss_count"],
    })
  return rows


def table_11_exploitation_matrix(records):
  _, _, exploitation_totals, exploitation_pair_games, exploitation_observed_pairs, models = summarize_record_statistics(records)
  models = sorted(models)
  rows = []
  for row_model in models:
    row = {
      "Extracting model": MODEL_DISPLAY_NAMES.get(row_model, row_model),
      "Model id": row_model,
    }
    for col_model in models:
      observed_games = exploitation_observed_pairs.get((row_model, col_model), 0)
      if not observed_games:
        row[MODEL_DISPLAY_NAMES.get(col_model, col_model)] = "N/A"
        continue
      pair_games = exploitation_pair_games.get((row_model, col_model), observed_games)
      total = exploitation_totals.get((row_model, col_model), 0.0)
      row[MODEL_DISPLAY_NAMES.get(col_model, col_model)] = total / pair_games if pair_games else "N/A"
    rows.append(row)
  return rows


def write_csv(path, rows):
  if not rows:
    with open(path, "w", encoding="utf-8", newline="") as f:
      f.write("")
    return
  fieldnames = list(rows[0].keys())
  with open(path, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)


def rows_to_markdown(title, rows):
  lines = [f"# {title}", ""]
  if not rows:
    lines.append("No data available.")
    lines.append("")
    return "\n".join(lines)
  headers = list(rows[0].keys())
  lines.append("| " + " | ".join(headers) + " |")
  lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
  for row in rows:
    values = []
    for header in headers:
      value = row.get(header, "")
      if isinstance(value, float):
        value = fmt_number(value, 3 if "rate" in header.lower() else 2)
      values.append(str(value))
    lines.append("| " + " | ".join(values) + " |")
  lines.append("")
  return "\n".join(lines)


def write_markdown(path, title, rows):
  with open(path, "w", encoding="utf-8") as f:
    f.write(rows_to_markdown(title, rows))


def export_tables(records, output_dir):
  os.makedirs(output_dir, exist_ok=True)

  table_specs = [
    ("table_3_self_play_scores", "Table 3. Self-play terminal-score statistics", summarize_scores(
      records,
      exp_type="default",
      exclude_models=RULE_MODELS | HUMAN_MODELS,
    )),
    ("table_4_heterogeneous_elo", "Table 4. Heterogeneous Elo statistics", table_4_elo(records)),
    ("table_5_model_by_species", "Table 5. Model-by-species assignment counts", table_5_model_by_species(records)),
    ("table_6_species_scores", "Table 6. Species-level terminal-score statistics", table_6_species_scores(records)),
    ("table_7_human_calibration", "Table 7. Human/model calibration statistics", table_7_human_and_model_calibration(records)),
    ("table_8_rule_baseline_comparison", "Table 8. Rule-baseline comparison", table_8_rule_comparison(records)),
    ("table_9_function_calling", "Table 9. Function-calling parse reliability", table_9_function_calling(records)),
    ("table_10_trade_value", "Table 10. Trade-value diagnostics", table_10_trade_value(records)),
    ("table_11_exploitation_matrix", "Table 11. Signed exploitation matrix", table_11_exploitation_matrix(records)),
  ]

  combined_parts = []
  for stem, title, rows in table_specs:
    write_csv(os.path.join(output_dir, f"{stem}.csv"), rows)
    write_markdown(os.path.join(output_dir, f"{stem}.md"), title, rows)
    combined_parts.append(rows_to_markdown(title, rows))

  combined_path = os.path.join(output_dir, "rebuttal_tables_3_to_11.md")
  with open(combined_path, "w", encoding="utf-8") as f:
    f.write("\n".join(combined_parts))
  return combined_path


def parse_args():
  parser = argparse.ArgumentParser(description="Export rebuttal tables from game_records.")
  parser.add_argument(
    "--records",
    nargs="*",
    default=DEFAULT_RECORD_FILES,
    help="Path(s) to game_records JSON files. Defaults to charts/game_records.json and charts/game_records_local.json.",
  )
  parser.add_argument(
    "--out",
    default=os.path.join(CURRENT_DIR, "tables"),
    help="Output directory for generated Markdown and CSV tables.",
  )
  return parser.parse_args()


def main():
  args = parse_args()
  records = load_records(args.records)
  combined_path = export_tables(records, args.out)
  print(f"Loaded {len(records)} unique records.")
  print(f"Exported rebuttal tables to {args.out}")
  print(f"Combined Markdown: {combined_path}")


if __name__ == "__main__":
  main()
