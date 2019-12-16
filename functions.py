# Data manipulation and visualization
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import itertools

# Statistical modeling
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score
from sklearn.tree import DecisionTreeClassifier 
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn import metrics
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.linear_model import LogisticRegression

def avg_section_duration(sections):
    """
    Returns the average section duration of a Spotify track.
    Param sections: [list] section object obtained from Spotify API. 
    """
    total = 0
    for section in sections:
        total += section['duration']
    return total/len(sections)

def decision_tree_gs(X_train, X_test, y_train, y_test):
    """
    Runs GridSearch CV on various parameters for a decision tree on a set of data.
    
    Returns the mean test score.
    """
    
    # Create the classifier, fit it on the training data and make predictions on the test set
    dt_clf = DecisionTreeClassifier(random_state=1)

    # GridSearch CV grid parameters
    param_grid = {
        'criterion': ['gini', 'entropy'],
        'max_depth': [None, 2, 3, 4, 5, 6],
        'min_samples_split': [2, 5, 10],
        'min_samples_leaf': [1, 2, 3, 4, 5, 6]
    }

    # Instantiate GS and fit
    dt_grid_search = GridSearchCV(dt_clf, param_grid, cv=3, return_train_score=True)
    dt_grid_search.fit(X_train, y_train)

    # Mean training score
    dt_gs_training_score = np.mean(dt_grid_search.cv_results_['mean_train_score'])

    # Mean test score
    dt_gs_testing_score = dt_grid_search.score(X_test, y_test)

#     print(f"Mean Training Score: {dt_gs_training_score :.2%}")
#     print(f"Mean Test Score: {dt_gs_testing_score :.2%}")
    print(f"Optimal Parameters: {dt_grid_search.best_params_}")
    
    return dt_gs_testing_score

def random_forest_gs(X_train, X_test, y_train, y_test):
    """
    Runs GridSearch CV on various parameters for a random forest model on a set of data.
    
    Returns the mean test score.
    """

    rf_clf = RandomForestClassifier(random_state=1)

    rf_param_grid = {
        'n_estimators': [10, 30, 100],
        'criterion': ['gini', 'entropy'],
        'max_depth': [None, 2, 6, 10],
        'min_samples_split': [5, 10],
        'min_samples_leaf': [3, 6]
    }

    rf_grid_search = GridSearchCV(rf_clf, rf_param_grid, cv=3)
    rf_grid_search.fit(X_train, y_train)

#     print(f"Training Accuracy: {rf_grid_search.best_score_ :.2%}")
#     print(f"Testing: {rf_grid_search.score(X_test, y_test) :.2%}")
    print(f"Optimal Parameters: {rf_grid_search.best_params_}")
    
    return rf_grid_search.score(X_test, y_test)

#getting matrix with Weighted Scores
def evaluate(test, pred, model):
    """
    Returns confusion matrix information for the given sklearn model.
    
    Param test: test data
    Param pred: predicted set of data
    Param model: sklearn model
    """
    return [model, 
            round(accuracy_score(test, pred),3),
            round(precision_score(test, pred),3), 
            round(recall_score(test, pred),3),
            round(f1_score(test, pred),3)]

def plot_cm(test,pred):
    """
    Displays a confusion matrix given the inputted data sets.
    
    Param test: test data for a given train-test split
    Param pred: predicted target values based on the test data
    """

    # Create CM
    cm = confusion_matrix(test,pred)
    classes = ['salsa','bachata']
    print(cm)

    # Create fig, ax, and plot
    fig = plt.figure(figsize=(12,8))
    ax = fig.add_subplot(111)
    cax = ax.matshow(cm,cmap=plt.cm.Oranges)
    fig.colorbar(cax)

    # Apply labels
    plt.title('Confusion matrix',fontdict={'size':14})
    ax.set_xticklabels([''] + classes,fontdict={'size':14})
    ax.set_yticklabels([''] + classes,fontdict={'size':14})
    plt.xlabel('Actual Values',fontdict={'size':14})
    plt.ylabel('Predicted Values',fontdict={'size':14})

    # Remove grid lines
    plt.grid(b=None)

    # Apply text
    thresh = cm.max() / 2.
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        plt.text(j, i, format(cm[i, j], 'd'),
                 horizontalalignment="center",
                 fontdict={'size':14,'weight':'heavy'},
                 color="white" if cm[i, j] > thresh else "black")
    plt.show()
    
def plot_feature_importances(model, X_train):
    """
    Plots the feature importances of the given model
    Param model: sklearn model
    Param X_train: array with train data
    """
    n_features = X_train.shape[1]
    plt.figure(figsize=(8,8))
    plt.barh(range(n_features), model.feature_importances_, align='center',color='darkorange') 
    plt.yticks(np.arange(n_features), X_train.columns.map(lambda x: x.title()).values) 
    plt.xlabel('Feature importance')
    plt.ylabel('Feature')
    plt.title('Model Feature Importances')