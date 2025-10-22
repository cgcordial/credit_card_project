import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.metrics import mean_squared_error, accuracy_score, classification_report

# LOAD AND INSPECT DATA
df = pd.read_csv("/Users/giocordial/PycharmProjects/credit_card_project/output/combined_data.csv")

print("Data loaded successfully!")
print("Columns found:", df.columns.tolist())
print("\nSample data:\n", df.head())

# BASIC CLEANING
# Drop duplicates, handle missing values
df = df.drop_duplicates()
df = df.fillna(0)

# ENCODE CATEGORICAL COLUMNS
# Find non-numeric columns
non_numeric_cols = df.select_dtypes(include=['object']).columns
label_encoders = {}

for col in non_numeric_cols:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col].astype(str))
    label_encoders[col] = le

print("\n Encoded non-numerical features:", non_numeric_cols.tolist())

# REGRESSION MODEL: Predict total spend
if 'Total' in df.columns:
    target_reg = 'Total'
elif 'Amount' in df.columns:
    target_reg = 'Amount'
else:
    raise ValueError("Couldn't find a column representing total spend (try renaming to 'Total').")

X_reg = df.drop(columns=[target_reg])
y_reg = df[target_reg]

X_train, X_test, y_train, y_test = train_test_split(X_reg, y_reg, test_size=0.2, random_state=42)

reg_model = RandomForestRegressor(random_state=42)
reg_model.fit(X_train, y_train)

y_pred_reg = reg_model.predict(X_test)

rmse = np.sqrt(mean_squared_error(y_test, y_pred_reg))
print("\n Regression RMSE:", rmse)

# Add predictions with decoded transaction descriptions (if available)
if 'Description' in label_encoders:
    df_display = pd.DataFrame({
        'Transaction_Description': label_encoders['Description'].inverse_transform(X_test['Description']),
        'Actual_Spend': y_test,
        'Predicted_Spend': y_pred_reg
    })
    print("\n Regression Predictions (showing descriptions):\n", df_display.head())
else:
    print("\n No 'Description' column found for displaying transaction text.")

# CLASSIFICATION MODEL: Predict spend category
# ------------------------------------------------------------
if 'Spend Category' in df.columns or 'Category' in df.columns:
    target_class = 'Spend Category' if 'Spend Category' in df.columns else 'Category'
else:
    raise ValueError("Couldn't find a column representing spend category (try renaming to 'Spend Category').")

X_cls = df.drop(columns=[target_class, target_reg]) if target_reg in df.columns else df.drop(columns=[target_class])
y_cls = df[target_class]

X_train_cls, X_test_cls, y_train_cls, y_test_cls = train_test_split(X_cls, y_cls, test_size=0.2, random_state=42)

cls_model = RandomForestClassifier(random_state=42)
cls_model.fit(X_train_cls, y_train_cls)

y_pred_cls = cls_model.predict(X_test_cls)

accuracy = accuracy_score(y_test_cls, y_pred_cls)
print("\n Classification Accuracy:", accuracy)
print("\n Classification Report:\n", classification_report(y_test_cls, y_pred_cls))

# Show decoded category names if available
if 'Description' in label_encoders:
    desc = label_encoders['Description'].inverse_transform(X_test_cls['Description'])
else:
    desc = ["(no description)"] * len(y_pred_cls)

if target_class in label_encoders:
    y_pred_labels = label_encoders[target_class].inverse_transform(y_pred_cls)
    y_true_labels = label_encoders[target_class].inverse_transform(y_test_cls)
else:
    y_pred_labels = y_pred_cls
    y_true_labels = y_test_cls

df_class_results = pd.DataFrame({
    'Transaction_Description': desc,
    'Actual_Category': y_true_labels,
    'Predicted_Category': y_pred_labels
})

print("\n Classification Predictions (showing descriptions and categories):\n", df_class_results.head())

print("\n Models built successfully!")
