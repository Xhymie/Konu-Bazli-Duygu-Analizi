import pandas as pd
from sklearn.model_selection import train_test_split

df = pd.read_csv("data/processed/trendyol_yorumlar_etiketli.csv", encoding="utf-8-sig")

train, temp = train_test_split(df, test_size=0.30, stratify=df["sentiment"], random_state=42)
val, test = train_test_split(temp, test_size=0.50, stratify=temp["sentiment"], random_state=42)

train.to_csv("data/split/train.csv", index=False, encoding="utf-8-sig")
val.to_csv("data/split/val.csv", index=False, encoding="utf-8-sig")
test.to_csv("data/split/test.csv", index=False, encoding="utf-8-sig")

print(f"Train: {len(train)}  Val: {len(val)}  Test: {len(test)}")
