from sklearn.model_selection import cross_validate
from sklearn import svm, tree, naive_bayes, linear_model, dummy, ensemble, neighbors
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import Pipeline


def evaluate_model(model, data, targets, scoring=None):
    if scoring is None:
        scoring = ['precision_macro', 'recall_macro', 'accuracy']

    scores = cross_validate(model, data, targets, scoring=scoring)
    results = []
    for measure in scoring:
        result = scores['test_' + measure].mean()
        results.append(result)
    return results


def compare_classification_models(data, targets):
    models = [
        ("Baseline", dummy.DummyClassifier(strategy='stratified')),
        ("Decision Tree", tree.DecisionTreeClassifier()),
        ("Random Forest", ensemble.RandomForestClassifier()),
        ("SVC", svm.SVC()),
        ("Logistic Regression", linear_model.LogisticRegression()),
        ("Complement Naive Bayes", naive_bayes.ComplementNB()),
    ]
    template = "{0:<25} {1:<4.2} {2:<4.2} {3:<4.2}"
    print(str.format(template, "Classifier", "Precision", "Recall", "Accuracy"))
    for name, model in models:
        scores = evaluate_model(model, data, targets)
        print(str.format(template, name, *scores))


def compare_regression_models(data, targets):
    models = [
        ("Baseline", dummy.DummyRegressor(strategy='mean')),
        ("Linear Regression", linear_model.LinearRegression(fit_intercept=False)),
        ("Polynomial Regression", Pipeline([
            ('poly', PolynomialFeatures(degree=3)),
            ('linear', linear_model.LinearRegression(fit_intercept=False))
        ])),
        ("Ridge Regression", linear_model.Ridge(fit_intercept=False)),
        ("LARS Lasso", linear_model.LassoLars(normalize=False)),
        ("Bayesian Ridge", linear_model.BayesianRidge(fit_intercept=False)),
        ("SGD", linear_model.SGDRegressor(fit_intercept=False)),
    ]
    template = "{0:<25} {1:<6.2} {2:<6.2} {3:<6.2}"
    print(str.format(template, "Model", "R2 Score", "Max Error", "NMSE"))
    for name, model in models:
        scores = evaluate_model(model, data, targets.ravel(), scoring=['r2', 'max_error', 'neg_mean_squared_error'])
        print(str.format(template, name, *scores))
