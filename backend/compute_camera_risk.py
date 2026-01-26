import pandas as pd

df = pd.read_csv("alert_logs.csv")

ALERT_WEIGHTS = {
    "WOMAN_ISOLATED": 1,   # LOW
    "WOMAN_SURROUNDED": 3,
    "TUCK_THUMB": 5,      # HIGH
    "TRAP_THUMB": 5,      # HIGH
    "HIGH_RISK_AUDIO": 5
}

df["risk_score"] = df["alert_type"].map(ALERT_WEIGHTS).fillna(0)

df["lat_bucket"] = df["latitude"].round(3)
df["lon_bucket"] = df["longitude"].round(3)

hotspots = (
    df.groupby(["lat_bucket", "lon_bucket"])
      .agg(
          total_risk=("risk_score", "sum"),
          alert_count=("alert_type", "count")
      )
      .reset_index()
      .sort_values(by="total_risk", ascending=False)
)

hotspots.to_csv("hotspot_priority.csv", index=False)
