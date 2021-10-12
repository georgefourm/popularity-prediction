from sklearn.model_selection import cross_validate
from sklearn import svm, tree, naive_bayes, linear_model, dummy, ensemble


def evaluate_model(model, data, targets, scoring=None):
    if scoring is None:
        scoring = ['precision_macro', 'recall_macro', 'accuracy']

    scores = cross_validate(model, data, targets, scoring=scoring)
    results = []
    for measure in scoring:
        result = scores['test_' + measure].mean()
        results.append(result)
    return results


def compare_models(data, targets):
    models = [
        ("Baseline Classifier", dummy.DummyClassifier(strategy='stratified')),
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
