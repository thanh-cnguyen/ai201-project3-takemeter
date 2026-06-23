import pandas as pd
from pathlib import Path

batch_dir = Path("batches")
label_dir = Path("labels")
output_path = "takemeter_dataset_labeled.csv"

merged_batches = []

for i in range(1, 6):
    batch_path = batch_dir / f"batch_{i}.csv"
    label_path = label_dir / f"batch_{i}_labels.csv"

    batch_df = pd.read_csv(batch_path)
    label_df = pd.read_csv(label_path)

    # Basic validation
    if len(batch_df) != len(label_df):
        raise ValueError(
            f"Row count mismatch in batch {i}: "
            f"{len(batch_df)} original rows vs {len(label_df)} label rows"
        )

    if "text" not in batch_df.columns:
        raise ValueError(f"{batch_path} is missing text column")

    if "label" not in label_df.columns or "notes" not in label_df.columns:
        raise ValueError(f"{label_path} must contain label and notes columns")

    # Replace/assign labels and notes from AI output
    batch_df["label"] = label_df["label"].astype(str).str.strip()
    batch_df["notes"] = label_df["notes"].fillna("").astype(str).str.strip()

    merged_batches.append(batch_df)

final_df = pd.concat(merged_batches, ignore_index=True)

# Optional: keep only required columns
final_df = final_df[["text", "label", "notes"]]

# Validate labels
valid_labels = {
    "evidence_based_take",
    "reasoned_opinion",
    "community_prompt",
}

bad_labels = final_df[~final_df["label"].isin(valid_labels)]

if not bad_labels.empty:
    print("Warning: found invalid labels:")
    print(bad_labels[["label", "text"]].head(20))
else:
    print("All labels are valid.")

# Save final merged dataset
final_df.to_csv(output_path, index=False)

print(f"Saved merged dataset to {output_path}")
print(f"Total rows: {len(final_df)}")

print("\nLabel distribution:")
print(final_df["label"].value_counts())
