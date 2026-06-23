import re
import pandas as pd
from pathlib import Path

# Input / output paths
input_path = "raw_dataset.csv"  # change this if your file has a different name
output_dir = Path("batches")
batch_size = 50

def clean_text(value):
    if pd.isna(value):
        return ""

    value = str(value)

    replacements = {
        "\u2018": "'",   # left single quote
        "\u2019": "'",   # right single quote / apostrophe
        "\u201c": '"',   # left double quote
        "\u201d": '"',   # right double quote
        "\u2013": "-",   # en dash
        "\u2014": "-",   # em dash
        "\u2026": "...",  # ellipsis
        "\xa0": " ",     # non-breaking space
    }

    for old, new in replacements.items():
        value = value.replace(old, new)

    value = value.replace("\r", " ").replace("\n", " ").replace("\t", " ")
    value = re.sub(r"\s+", " ", value).strip()
    return value

# Create output folder
output_dir.mkdir(exist_ok=True)

# Read CSV
df = pd.read_csv(input_path)

# Optional: keep only the columns you want
expected_columns = ["text", "label", "notes"]
df = df[expected_columns]

# Fill empty notes
df["notes"] = df["notes"].fillna("")

# Apply text cleaning
df["text"] = df["text"].apply(clean_text)

# Split into batches
for i in range(0, len(df), batch_size):
    batch = df.iloc[i:i + batch_size]
    batch_number = (i // batch_size) + 1
    output_path = output_dir / f"batch_{batch_number}.csv"
    batch.to_csv(output_path, index=False)
    print(f"Saved {output_path} with {len(batch)} rows")

print("Done.")
