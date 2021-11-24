import pandas as pd
from sklearn.model_selection import cross_validate, StratifiedKFold, KFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


def evaluate_model(model, metrics, data, targets, regression=False):
    model = Pipeline([("std", StandardScaler()), ("estimator", model)])

    # Explicitly configure for repeatable results
    if regression:
        cv = KFold(shuffle=True, random_state=1)
    else:
        cv = StratifiedKFold(shuffle=True, n_splits=5, random_state=1)

    scores = cross_validate(
        model,
        data,
        targets,
        scoring=metrics,
        cv=cv
    )
    return scores


def compare_models(models, metrics, data, targets, regression=False):
    comparison = dict()
    for name, model in models:
        print("Evaluating " + name)
        scores = evaluate_model(model, metrics, data, targets, regression)
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
