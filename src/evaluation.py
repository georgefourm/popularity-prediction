import pandas as pd
from sklearn.model_selection import cross_validate
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


def evaluate_model(model, metrics, data, targets):
    model = Pipeline([("std", StandardScaler()), ("estimator", model)])
    scores = cross_validate(model, data, targets, scoring=metrics)
    return scores


def compare_models(models, metrics, data, targets):
    comparison = dict()
    for name, model in models:
        print("Evaluating " + name)
        scores = evaluate_model(model, metrics, data, targets)
        table = pd.DataFrame(scores.values(), columns=scores.keys())
        comparison[name] = table

    evaluation_df = []
    for name, metrics in comparison.items():
        means = metrics.mean(axis=1)
        means = dict(zip(metrics.columns, means))
        evaluation_df.append({
            "model": name,
            **means
        })

    return pd.DataFrame(evaluation_df)
