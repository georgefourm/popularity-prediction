from sklearn import svm, ensemble, linear_model
from sklearn.model_selection import GridSearchCV


def optimize_random_forest(data, targets, measure='accuracy'):
    params = {
        'n_estimators': [100, 500, 100],
        'criterion': ['gini', 'entropy'],
        'class_weight': ['balanced', 'balanced_subsample'],
        'max_features': ['auto', 'log2']
    }

    optimizer = GridSearchCV(
        ensemble.RandomForestClassifier(),
        param_grid=params,
        scoring=measure,
        n_jobs=3,
        verbose=4
    )
    optimizer.fit(data, targets)
    return optimizer


def optimize_svm(data, targets, measure='accuracy'):
    params = [
        {'C': [0.1, 1, 10], 'kernel': ['linear']},
        {'C': [0.1, 1, 10], 'gamma': ['scale', 0.1, 0.5], 'kernel': ['rbf', 'sigmoid']},
        {'C': [0.1, 1, 10], 'gamma': ['scale', 0.1, 0.5, 0.9], 'kernel': ['poly'], 'degree': [3, 4]}
    ]
    optimizer = GridSearchCV(
        svm.SVC(),
        param_grid=params,
        scoring=measure,
        n_jobs=3,
        verbose=4
    )
    optimizer.fit(data, targets)
    return optimizer


def optimize_lr(data, targets):
    params = {
        'penalty': ['l1', 'l2'],
        'C': [0.1, 1, 10],
        'class_weight': ['balanced', None],
        'solver': ['liblinear']
    }
    optimizer = GridSearchCV(
        linear_model.LogisticRegression(),
        param_grid=params,
        scoring='accuracy',
        n_jobs=3,
        verbose=4
    )
    optimizer.fit(data, targets)
    return optimizer
