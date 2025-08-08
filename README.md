
# 💞 Relationship Sensitivity

Ever wondered *why* you feel more connected to one partner than another — and how much that feeling depends on certain qualities?  
**Relationship Sensitivity** is a small but mighty toolkit for quantifying and exploring the dynamics between you and the important people in your life.

At its core, it takes a set of **relationship dimensions** (e.g., *Emotional connection*, *Shared values & life goals*, *Aesthetics & taste*, etc.) and assigns each a **weight** representing how important that dimension is to you.  
It then scores two people (or more, if you extend it) across those dimensions — for example, a current partner vs. an ex — and lets you:

- 📊 **Score & compare**: See where each person shines (or struggles) across dimensions.
- 📈 **Visualize**: Generate radar charts and sensitivity plots to understand the strengths and gaps.
- 🧪 **Run sensitivity analysis**: Test *"what-if"* scenarios by tweaking how much weight you give to certain traits, revealing:
  - **1D analysis** – How much you’d need to change *just one dimension’s* importance before the “winner” flips.
  - **3D analysis** – How combinations of three dimensions influence the outcome at once.


## Features
- Weighted totals (Option A vs B)  
- Radar charts (unweighted / weighted)  
- 1D & 3D **weight sensitivity** (find boundary where two options tie)  
- CSV/Excel outputs for your own charts

# Quickstart


## 1) Install
```bash
pip install -r requirements.txt
```

## 2) Prepare your data (CSV)
Columns (case-sensitive):
- Dimension – factor name
- Weight – importance (0–1). If not summing to 1, we normalize.
- ExScore or Ex_score_raw – score for Option A (e.g., “Ex”)
- CurScore or Cur_score_raw – score for Option B (e.g., “Current”)

Example (examples/relationship.csv):

| Dimension                      | Weight | ExScore | CurScore |
|---------------------------------|--------|---------|----------|
| Emotional connection           | 0.12   | 9       | 7        |
| Unconditional acceptance       | 0.10   | 8       | 6        |
| Care & daily attentiveness     | 0.13   | 7       | 8        |
| Shared values & life goals     | 0.15   | 6       | 8        |
| Income & economic potential    | 0.14   | 7       | 7        |
| Activity & interest fit        | 0.09   | 6       | 8        |
| Physical preference            | 0.06   | 8       | 6        |
| Communication & conflict       | 0.08   | 7       | 9        |
| Patience & holding space       | 0.05   | 6       | 8        |
| Social handling                | 0.04   | 5       | 7        |
| Aesthetics & taste             | 0.04   | 7       | 8        |

# Use app.py
```
python3 -m streamlit run app.py
``` 

# If You Somehow Chose to Run Everything on Your Local Ternimal

## 3) Run Scoring and Plot Radar Chart
Calculate and export scores for current and ex-partners.
```bash
python3 -m src.rel_sense.scoring examples/relationship.csv
```
Output:
outputs/scores.csv — Detailed scores per dimension.

**Plot Radar Chart**
```
python3 -m src.rel_sense.plots --radar outputs/scores.csv
```

## 4) Sensitivity Analysis 

### 4.1 Run 1D sensitivity
Vary one dimension’s weight to find the decision boundary.
```
python3 -m src.rel_sense.run_sensitivity examples/relationship.csv \
  --dim "Emotional connection"
```
Output:
outputs/boundary_emotionalconnection.csv

### 4.3 Run 3D sensitivity
```bash
python3 -m src.rel_sense.run_sensitivity examples/relationship.csv \
  --tri "Emotional connection,Shared values & life goals,Aesthetics & taste"
```
### 4.4) Plot 1D and 3D sensitivity boundary
```
python3 -m src.rel_sense.plots --one outputs/boundary_emotionalconnection.csv
python3 -m src.rel_sense.plots --tri outputs/tri_sensitivity.csv --eps 0.02
```


Lastly, find Results in Output Folder


## Common issues

- ImportError: attempted relative import with no known parent package

    Run with -m:
    ```python3 -m src.rel_sense.scoring examples/relationship.csv
    python3 -m src.rel_sense.run_sensitivity examples/relationship.csv
    ```

- “Dimension 'X' not found”

    Use --list to see exact names, then pass them with quotes:
    ```--dim "Emotional connection" \
    --tri "Emotional connection,Shared values & life goals,Aesthetics & taste"
    ```
- Weights don’t sum to 1

    We auto-normalize and print a warning.


###  LICENSE
MIT - do what you want, no warranty.

## 🪞 Behind the Scenes

This project started from a personal reflection on relationships — wondering why certain connections feel stronger than others, and how much those feelings shift when specific qualities change.

What began as a casual conversation about emotional patterns unexpectedly turned into a full development journey: building scoring logic, sensitivity analysis, and a visual interface with Streamlit.

It’s both a tool for playful exploration and a mirror for deeper self-understanding — a reminder that sometimes, coding can be another way of making sense of the heart.