import pandas as pd
from sklearn.model_selection import GroupShuffleSplit

# Yorum bazlı split: aynı yorumun farklı aspect satırları aynı bölmeye gider,
# böylece train/test sızıntısı önlenir.
SEED = 42
df = pd.read_csv("data/processed/trendyol_yorumlar_etiketli.csv", encoding="utf-8-sig")
groups = df["yorum"].astype(str).str.strip()

train_idx, temp_idx = next(
    GroupShuffleSplit(n_splits=1, test_size=0.30, random_state=SEED).split(df, groups=groups)
)
train, temp = df.iloc[train_idx], df.iloc[temp_idx]

temp_groups = temp["yorum"].astype(str).str.strip()
val_idx, test_idx = next(
    GroupShuffleSplit(n_splits=1, test_size=0.50, random_state=SEED).split(temp, groups=temp_groups)
)
val, test = temp.iloc[val_idx], temp.iloc[test_idx]

for name, part in [("train", train), ("val", val), ("test", test)]:
    part.to_csv(f"data/split/{name}.csv", index=False, encoding="utf-8-sig")

ytr, yva, yte = (set(p["yorum"].astype(str).str.strip()) for p in (train, val, test))
print(f"Train: {len(train)}  Val: {len(val)}  Test: {len(test)}")
print(f"Yorum ortusmesi: train-test={len(ytr & yte)}  train-val={len(ytr & yva)}  val-test={len(yva & yte)}")
for name, part in [("train", train), ("val", val), ("test", test)]:
    print(f"  {name} sentiment: {part['sentiment'].value_counts(normalize=True).round(3).to_dict()}")
