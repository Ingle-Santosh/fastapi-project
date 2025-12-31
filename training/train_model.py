import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.ensemble import RandomForestRegressor
from training.train_utils import MODEL_PATH, DATA_FILE_PATH, MODEL_DIR

df = (
    pd
    .read_csv(DATA_FILE_PATH)
    .drop_duplicates()
    .drop(columns=['name', 'model', 'edition'])
)

X = df.drop(columns='selling_price')
y = df.selling_price.copy()

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

num_cols = X_train.select_dtypes(include='number').columns.tolist()
cat_cols = [col for col in X_train.columns if col not in num_cols]

num_pipeline = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='median')),
    ('scalar', StandardScaler())
])

cat_pipeline = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='constant', fill_value='missing')),
    ('encoder', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
])

preprocessor = ColumnTransformer(transformers=[
    ('num_col_pp', num_pipeline, num_cols),
    ('cat_col_pp', cat_pipeline, cat_cols)
])

regressor = RandomForestRegressor(
    n_estimators= 21,
    max_depth=5,
    random_state=42
)

rf_model = Pipeline(steps=[
    ('pre_pro', preprocessor),
    ('regressor', regressor)
])

rf_model.fit(X_train, y_train)


MODEL_DIR.mkdir(parents=True, exist_ok=True)
joblib.dump(rf_model, MODEL_PATH)