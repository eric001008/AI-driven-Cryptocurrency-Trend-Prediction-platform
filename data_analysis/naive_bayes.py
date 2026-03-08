
import pandas as pd
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.metrics import classification_report, confusion_matrix


def train_naive_bayes_model(df):

    # Train a Naive Bayes model using fake feature data and return the model and test set.

    # Load and prepare data
    df["future_trend"] = df["price_trend"].shift(-1)
    df = df.dropna().reset_index(drop=True)

    # Define features and target (predict future_trend using current features)
    features = ['reddit', 'youtube', 'banknews', 'gnews', 'newsapi', 'telegram']
    X = df[features]
    y = df["future_trend"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Pipeline: one-hot encoding + naive bayes
    categorical_transformer = OneHotEncoder(handle_unknown='ignore')
    preprocessor = ColumnTransformer(
        transformers=[('cat', categorical_transformer, features)]
    )

    model = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('classifier', MultinomialNB())
    ])

    # Fit the model
    model.fit(X_train, y_train)

    return model, X_test, y_test

# =======TEST=======

def predict_with_explanation(model, features: pd.DataFrame):

    # Given a trained model and a dataframe of feature samples, print top-2 predicted probabilities per sample.

    # Get predicted probabilities
    probs = model.predict_proba(features)
    labels = model.named_steps['classifier'].classes_

    # Iterate through each test sample
    for i, prob_dist in enumerate(probs):
        # Readable description of current feature values
        features_desc = ', '.join([f"{col}={features.iloc[i][col]}" for col in features.columns])

        sorted_indices = prob_dist.argsort()[::-1]
        top1_idx, top2_idx = sorted_indices[:2]
        top1_label, top1_prob = labels[top1_idx], prob_dist[top1_idx]
        top2_label, top2_prob = labels[top2_idx], prob_dist[top2_idx]

        print(f"Under the current condition ({features_desc}),")
        print(f"there is a {top1_prob:.1%} probability of {top1_label}, followed by {top2_prob:.1%} probability of {top2_label}.")
        print("-" * 80)