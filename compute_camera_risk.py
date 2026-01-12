import pandas as pd

# Load alert history
df = pd.read_csv("alert_logs.csv")

# Risk weights per alert type
ALERT_WEIGHTS = {
    "SOS_GESTURE": 5,
    "HIGH_RISK_AUDIO": 4,
    "WOMAN_SURROUNDED": 3,
    "WOMAN_ISOLATED": 1
}

# Convert alert types to risk scores
df["risk_score"] = df["alert_type"].map(ALERT_WEIGHTS)

# Aggregate total risk per camera
camera_priority = (
    df.groupby("camera_id")["risk_score"]
    .sum()
    .reset_index()
    .sort_values(by="risk_score", ascending=False)
)

# Save for UI use
camera_priority.to_csv("camera_priority.csv", index=False)

print("\n📊 CAMERA PRIORITY (High → Low Risk)\n")
print(camera_priority)
print("\n✅ camera_priority.csv generated")
