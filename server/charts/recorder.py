import json
import os
import matplotlib.pyplot as plt

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

  def plot_boxplot(self, exp_type="default"):
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

    labels = sorted(grouped_data.keys())
    data_values = [grouped_data[label] for label in labels]
    base_value = 5
    data_values = [[((score - base_value) / base_value) for score in grouped_data[label]] for label in labels]

    # Plotting
    plt.figure(figsize=(10, 6))
    plt.boxplot(data_values, labels=labels)
    plt.title(f'Value-added Percentage Distribution by Model')
    plt.xlabel('Model')
    plt.ylabel('Value-added Percentage')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

  def interactive_mode(self):
    last_model = "gpt-4o-mini"
    while True:
      print("\n--- Game Recorder ---")
      print("1. Add New Game Record")
      print("2. Draw Boxplot")
      print("3. Reload Data")
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
          new_record = {
            "exp_type": exp_type,
            "exp_name": exp_name,
            "results": results_buffer
          }
          self.data.append(new_record)
          self.save()
          print(f"Saved {len(results_buffer)} results to {exp_name}")
        else:
          print("No data entered.")

      elif choice == '2':
        exp_type = input("\nEnter Experiment Type to plot [default]: ").strip() or "default"
        self.plot_boxplot(exp_type)
          
      elif choice == '3':
        self.load()
        print("Data reloaded from disk.")
        
      elif choice == 'q':
        break
      else:
        print("Invalid choice.")

game_recorder = GameRecorder()

if __name__ == "__main__":
  game_recorder.plot_boxplot()
  game_recorder.interactive_mode()