import json
import math
import os
import time
from collections import defaultdict

import matplotlib.pyplot as plt
import random

from server.utils.config import get_config

class GameRecorder:
  def __init__(self, filepath=None):
    if filepath is None:
      # Default to json in the same directory as this script
      base_dir = os.path.dirname(os.path.abspath(__file__))
      self.filepath = os.path.join(base_dir, 'game_records.json')
    else:
      self.filepath = filepath
    self.data = []
    self.load()

  def _get_default_new_records_path(self):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, 'game_records_new.json')

  def load(self):
    """读取 json 并将结果载入"""
    if os.path.exists(self.filepath):
      try:
        with open(self.filepath, 'r', encoding='utf-8') as f:
          self.data = json.load(f)
      except json.JSONDecodeError:
        print(f"Error decoding JSON from {self.filepath}, initializing empty list.")
        self.data = []
    else:
      print(f"File {self.filepath} not found, initializing empty list.")
      self.data = []

  def save(self):
    """保存数据到 json"""
    # Ensure directory exists
    os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
    with open(self.filepath, 'w', encoding='utf-8') as f:
      json.dump(self.data, f, indent=4) # indent for readability

  def add_record(self, exp_type, exp_name, results):
    new_record = {
      "exp_type": exp_type,
      "exp_name": exp_name,
      "results": results
    }
    self.data.append(new_record)
    self.save()

  def merge_records_from_file(self, filepath=None):
    """Merge records from a secondary file by exp_name."""
    source_path = filepath or self._get_default_new_records_path()
    if not os.path.exists(source_path):
      print(f"Merge source not found: {source_path}")
      return {"merged": 0, "skipped": 0, "source_path": source_path}

    try:
      with open(source_path, 'r', encoding='utf-8') as f:
        new_data = json.load(f)
    except json.JSONDecodeError:
      print(f"Error decoding JSON from {source_path}")
      return {"merged": 0, "skipped": 0, "source_path": source_path}

    if not isinstance(new_data, list):
      print(f"Unexpected format in {source_path}: expected a list of records.")
      return {"merged": 0, "skipped": 0, "source_path": source_path}

    existing_names = {
      record.get("exp_name")
      for record in self.data
      if isinstance(record, dict) and record.get("exp_name")
    }

    merged_count = 0
    skipped_count = 0
    for record in new_data:
      if not isinstance(record, dict):
        skipped_count += 1
        continue

      exp_name = record.get("exp_name")
      if not exp_name:
        skipped_count += 1
        continue

      if exp_name in existing_names:
        skipped_count += 1
        continue

      self.data.append(record)
      existing_names.add(exp_name)
      merged_count += 1

    if merged_count:
      self.save()

    print(
      f"Merged {merged_count} new records from {source_path}; "
      f"skipped {skipped_count} records with duplicate or invalid exp_name."
    )
    return {"merged": merged_count, "skipped": skipped_count, "source_path": source_path}

  def _build_pairwise_results(self, exp_type=None):
    pairwise_wins = defaultdict(float)
    pairwise_counts = defaultdict(int)
    model_set = set()

    for record in self.data:
      if exp_type is not None and record.get("exp_type") != exp_type:
        continue

      results = record.get("results", [])
      per_model_scores = defaultdict(list)
      for result in results:
        if not isinstance(result, dict):
          continue
        model = result.get("model", "Unknown")
        try:
          score = float(result.get("score", 0))
        except (TypeError, ValueError):
          continue
        per_model_scores[model].append(score)

      aggregated_scores = {
        model: sum(scores) / len(scores)
        for model, scores in per_model_scores.items()
        if scores
      }
      if len(aggregated_scores) < 2:
        continue

      models = list(aggregated_scores.keys())
      for i in range(len(models)):
        for j in range(i + 1, len(models)):
          left = models[i]
          right = models[j]
          left_score = aggregated_scores[left]
          right_score = aggregated_scores[right]

          model_set.add(left)
          model_set.add(right)
          pairwise_counts[(left, right)] += 1
          pairwise_counts[(right, left)] += 1

          if left_score > right_score:
            pairwise_wins[(left, right)] += 1.0
          elif right_score > left_score:
            pairwise_wins[(right, left)] += 1.0
          else:
            pairwise_wins[(left, right)] += 0.5
            pairwise_wins[(right, left)] += 0.5

    return sorted(model_set), pairwise_wins, pairwise_counts

  def estimate_elo(self, exp_type=None, max_iter=500, tol=1e-9):
    """Estimate time-order-independent Elo ratings via Bradley-Terry MLE."""
    models, pairwise_wins, pairwise_counts = self._build_pairwise_results(exp_type=exp_type)
    if len(models) < 2:
      print("Not enough multi-model records to estimate Elo.")
      return {}

    strengths = {model: 1.0 for model in models}
    for _ in range(max_iter):
      updated_strengths = {}
      max_relative_change = 0.0

      for model in models:
        wins = sum(pairwise_wins[(model, opponent)] for opponent in models if opponent != model)
        denom = 0.0
        for opponent in models:
          if opponent == model:
            continue
          comparisons = pairwise_counts[(model, opponent)]
          if comparisons:
            denom += comparisons / (strengths[model] + strengths[opponent])

        if denom <= 0:
          updated = strengths[model]
        else:
          updated = max(wins / denom, 1e-12)

        updated_strengths[model] = updated
        max_relative_change = max(
          max_relative_change,
          abs(updated - strengths[model]) / max(strengths[model], 1e-12)
        )

      log_strengths = [math.log(value) for value in updated_strengths.values() if value > 0]
      if not log_strengths:
        print("Unable to stabilize Elo estimates.")
        return {}

      geo_mean = math.exp(sum(log_strengths) / len(log_strengths))
      for model in models:
        updated_strengths[model] = max(updated_strengths[model] / geo_mean, 1e-12)

      strengths = updated_strengths
      if max_relative_change < tol:
        break

    mean_log_strength = sum(math.log(strengths[model]) for model in models) / len(models)
    elos = {
      model: 1500.0 + (400.0 / math.log(10)) * (math.log(strengths[model]) - mean_log_strength)
      for model in models
    }

    ranking = sorted(models, key=lambda model: elos[model], reverse=True)
    print("\n--- Elo Estimate ---")
    if exp_type is not None:
      print(f"Experiment type: {exp_type}")
    for index, model in enumerate(ranking, start=1):
      total_games = sum(
        pairwise_counts[(model, opponent)]
        for opponent in models
        if opponent != model
      )
      print(f"{index:>2}. {model}: {elos[model]:.2f} (comparisons: {total_games})")

    return elos

  def save_plot(self, filename):
    """保存当前绘图到 charts/plots 目录"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    save_dir = os.path.join(base_dir, "plots")
    os.makedirs(save_dir, exist_ok=True)
    
    filepath = os.path.join(save_dir, filename)
    plt.savefig(filepath, dpi=300)
    print(f"Plot saved to {filepath}")

  def plot_boxplot(self, exp_type="default", save=False):
    """为 record 的结果绘制一张箱形图"""
    exps = [r for r in self.data if r.get("exp_type") == exp_type]
    if not exps:
      print(f"No experiments found for type: {exp_type}")
      return
    results = [r for exp in exps for r in exp.get("results", [])]
    if not results:
      print("No results to plot.")
      return

    # Prepare data for plotting
    # Group by model
    grouped_data = {}
    for r in results:
      key = r.get("model", "Unknown")
      if key not in grouped_data:
        grouped_data[key] = []
      grouped_data[key].append(r.get("score", 0))

    # Sort labels by mean score
    mean_scores = {k: sum(v)/len(v) if v else 0 for k, v in grouped_data.items()}
    labels = sorted(grouped_data.keys(), key=lambda x: mean_scores[x])

    base_value = 5
    data_values = [[((score - base_value) / base_value) for score in grouped_data[label]] for label in labels]

    # Plotting
    plt.figure(figsize=(12, 8))
    
    # Create boxplot with patch_artist=True to fill with color
    bplot = plt.boxplot(data_values, labels=labels, patch_artist=True,
                        medianprops=dict(color="black", linewidth=1.5),
                        flierprops=dict(marker='o', markersize=5, linestyle='none', markeredgecolor='gray'))
    
    # Color palette
    colors = ['#FF9999', '#66B2FF', '#99FF99', '#FFCC99', '#c2c2f0', '#ffb3e6', '#c4e17f', '#76D7C4']
    for patch, color in zip(bplot['boxes'], colors * (len(data_values) // len(colors) + 1)):
        patch.set_facecolor(color)
        patch.set_alpha(0.6)

    # Add jittered scatter points
    # for i, data in enumerate(data_values):
    #     x = [i + 1 + random.uniform(-0.08, 0.08) for _ in data]
    #     plt.scatter(x, data, alpha=0.6, s=20, color='darkblue', zorder=10)

    plt.title(f'Value-added Percentage Distribution by Model (Exp: {exp_type})', fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Model', fontsize=12)
    plt.ylabel('Value-added Percentage', fontsize=12)
    
    # Add horizontal line at 0%
    plt.axhline(y=0, color='gray', linestyle='--', linewidth=1.2, alpha=0.8)
    
    plt.grid(True, linestyle=':', alpha=0.6, axis='y')
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    if save:
      timestamp = int(time.time())
      filename = f"{exp_type}_{timestamp}.png"
      self.save_plot(filename)

    plt.show()

  def interactive_mode(self):
    last_model = get_config('default_bot_type')
    while True:
      print("\n--- Game Recorder ---")
      print("1. Add New Game Record")
      print("2. Draw Boxplot")
      print("3. Reload Data")
      print("4. Merge Records From game_records_new.json")
      print("5. Estimate Elo")
      print("q. Exit")
      
      choice = input("Enter choice: ").strip().lower()
      
      if choice == '1':
        exp_type = input("Experiment Type [default]: ").strip() or "default"
        
        # Calculate default experiment name
        count = len([r for r in self.data if r.get('exp_type') == exp_type])
        default_name = f"{exp_type}_{count + 1}"
        
        exp_name = input(f"Experiment Name [{default_name}]: ").strip() or default_name
        
        print("Enter results (Press Enter on Model to finish)")
        results_buffer = []
        
        while True:
          # Model input
          prompt_model = f"Model [{last_model}]: "
          model_in = input(prompt_model).strip()
          
          current_model = last_model
          if model_in:
            current_model = model_in
            last_model = model_in
          elif not last_model:
            # No input and no default -> finish
            break
            
          # Special check if user wants to finish and pressed enter with a default set?
          # Actually standard is usually: Empty input = default. 
          # To finish, maybe check Specie? Or separate command?
          # Let's say if Model is empty AND Specie is skipped, we stop?
          # Or just: if model is empty, use default.
          # We need a clear way to exit.
          # "Enter results (Type 'q' in Model to finish)"
          if model_in.lower() == 'q':
            break

          # Specie input
          specie_in = input("Specie: ").strip()
          if not specie_in:
             # If specie is empty, maybe stop?
             break
          specie_abbr = {
            "Kja": "Kjasjavikalimm",
            "Fad": "Faderan",
            "Cay": "Caylion",
            "Yen": "Yengii",
          }
          if specie_in in specie_abbr.keys():
            specie_in = specie_abbr[specie_in]
          # Score input
          try:
            score_in = float(input("Score: ").strip())
          except ValueError:
            print("Invalid score.")
            continue
            
          results_buffer.append({
            "model": current_model,
            "specie": specie_in,
            "score": score_in
          })
          print(f" ... Added {specie_in}: {score_in}")
        
        if results_buffer:
          self.add_record(exp_type, exp_name, results_buffer)
          save_input = input("Save plot? (y/n) [n]: ").strip().lower()
          save = save_input == 'y'
          self.plot_boxplot(exp_type, save=save)
          print(f"Saved {len(results_buffer)} results to {exp_name}")
        else:
          print("No data entered.")

      elif choice == '2':
        exp_type = input("\nEnter Experiment Type to plot [default]: ").strip() or "default"
        self.plot_boxplot(exp_type)
          
      elif choice == '3':
        self.load()
        print("Data reloaded from disk.")

      elif choice == '4':
        source_path = input("Source file [game_records_new.json]: ").strip() or None
        self.merge_records_from_file(source_path)

      elif choice == '5':
        exp_type = input("\nEnter Experiment Type for Elo [all]: ").strip() or None
        self.estimate_elo(exp_type=exp_type)
        
      elif choice == 'q':
        break
      else:
        print("Invalid choice.")

game_recorder = GameRecorder()

if __name__ == "__main__":
  game_recorder.plot_boxplot()
  game_recorder.interactive_mode()