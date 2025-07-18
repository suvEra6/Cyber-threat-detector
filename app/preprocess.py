import pandas as pd
import os

# Set absolute output path
output_path = os.path.join(os.path.dirname(__file__), "../data/formatted_logs.csv")

# Load dataset
df = pd.read_csv("data/cicids2017_ddos.csv", low_memory=False)

# Strip column name whitespace
df.columns = df.columns.str.strip()

# Check available labels
print(f"\nData shape: {df.shape}")
print("\nColumns:\n", df.columns.tolist())
print("\nLabel distribution:\n", df['Label'].value_counts())

# Define a safe log-formatting function (based on available columns)
def format_logs(row):
    return (
        f"DestPort: {row['Destination Port']}, "
        #f"Protocol: {row['Protocol']}, "
        f"Flow Duration: {row['Flow Duration']}, "
        f"Fwd Pkts: {row['Total Fwd Packets']}, "
        f"Bwd Pkts: {row['Total Backward Packets']}"
    )


# Apply and generate label
df['log_text'] = df.apply(format_logs, axis=1)
df['label'] = df['Label'].apply(lambda x: 0 if 'BENIGN' in x.upper() else 1)

# Keep only necessary columns
df_final = df[['log_text', 'label']]

# Save to file
df_final.to_csv(output_path, index=False)
print(f"\n✅ Saved cleaned dataset to: {output_path}")
