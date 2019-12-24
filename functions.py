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

    # Create CM and labels
    cm = confusion_matrix(test,pred)
    classes = ['Salsa','Bachata']

    # Create fig, ax, and plot
    fig = plt.figure(figsize=(10,7))
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
    # Join together feature importances and feature labels
    feat_imps = tuple(zip(X_train.columns,
                          model.feature_importances_))
    
    # Create df out of this in order to sort by feature importance  
    # while keeping track of the labels
    feat_imps_df = pd.DataFrame(data = model.feature_importances_,
                                index = X_train.columns,
                                columns = ['feature_importance'])

    feat_imps_df.sort_values(by = 'feature_importance', 
                             ascending = True, 
                             inplace=True)
    
    # Store number of features for plotting purposes
    n_features = feat_imps_df.shape[0]
    
    # Instantiate plt fig, add data, and appropriate graph labels
    plt.figure(figsize=(8,8))
    plt.barh(range(n_features), 
             feat_imps_df.feature_importance, 
             align='center',
             color='darkorange') 
    plt.yticks(np.arange(n_features), 
               feat_imps_df.index.map(lambda x: x.title()).values) 
    plt.xlabel('Feature importance')
    plt.ylabel('Feature')
    plt.title('Model Feature Importances')
    

def plot_tempo_comp(train_df, tempo_comp):
    """
    Plot tempo comparison graph. This outputs a very specific graph only.
    As such, I won't go into too much detail here.
    
    Param train_df: [df] training data set
    Param tempo_comp: [df] DataFrame containing tempo comparison report
    """
    plt.figure(figsize=(12,8))

    # Histogram of salsa tempos from the training set 
    plt.hist(train_df[train_df['genre'] == 'salsa']['tempo'],
             bins = 30, 
             alpha=0.5, 
             label='Salsa',
             color='red')

    # Histogram of bachata tempos from the training set 
    plt.hist(train_df[train_df['genre'] == 'bachata']['tempo'],
             bins = 30, 
             alpha=0.6, 
             label='Bachata',
             color='darkorange')

    # Average salsa tempos from incorrect prediction set
    plt.vlines(x = tempo_comp.iloc[1,:].values, 
               ymin=0, 
               ymax= 175, 
               color = 'red')

    # Arrow showing change of average salsa tempo from training set 
    # to incorrect prediction set
    plt.arrow(x = tempo_comp.iloc[1,:][0]+1, 
              y = 120, 
              dx = 12, 
              dy = 0, 
              color = 'red', 
              width= 0.8, 
              head_width = 6, 
              head_length = 6)

    # Add some text by the appropriate average tempo lines
    plt.text(x = 83,
             y = 120,
             s = 'Average tempo of \ntraining salsa set',
             verticalalignment='center',
             horizontalalignment = 'left',
             fontdict = {'fontsize':12})

    plt.text(x = 135,
             y = 120,
             s = 'Average tempo of \nincorrectly predicted \nsalsa set',
             verticalalignment = 'center',
             horizontalalignment = 'left',
             fontdict = {'fontsize':12})

    # Add labels and such
    plt.legend(loc='upper right')
    plt.xlabel('Tempo (bpm)')
    plt.ylabel('No. of Songs')
    plt.title('Tempo Distributions of Training Set')
    plt.show()    
    
    
def plot_duration_comp(train_df,duration_comp):
    """
    Plot tempo comparison graph. This outputs a very specific graph only.
    As such, I won't go into too much detail here.
    
    Param train_df: [df] training data set
    Param duration_comp: [df] DataFrame containing duration comparison report
    """
    plt.figure(figsize=(12,8))

    # Histogram of salsa duration from the training set 
    plt.hist(train_df[train_df['genre'] == 'salsa']['duration_ms'],
             bins = 30, 
             alpha=0.5, 
             label='Salsa',
             color='red')

    # Histogram of bachata duration from the training set 
    plt.hist(train_df[train_df['genre'] == 'bachata']['duration_ms'],
             bins = 30, 
             alpha=0.6, 
             label='Bachata',
             color='darkorange')

    # Average salsa duration from incorrect prediction set
    plt.vlines(x = duration_comp.iloc[1,:].values, 
               ymin=0, 
               ymax= 175, 
               color = 'red')

    # Arrow showing change of average salsa duration from training set 
    # to incorrect prediction set
    plt.arrow(x = duration_comp.iloc[1,:][0] - 5000, 
              y = 120, 
              dx = (duration_comp.iloc[1,:][1] - duration_comp.iloc[1,:][0]) + 20000,
              dy = 0, 
              color = 'red', 
              width= 0.8, 
              head_width = 8, 
              head_length = 10000)

    # Add text by appropriate average duration lines
    plt.text(x = duration_comp.iloc[1,:][0] + 10000,
             y = 120,
             s = 'Average duration of \ntraining salsa set',
             verticalalignment='center',
             horizontalalignment = 'left',
             fontdict = {'fontsize':12})

    plt.text(x = duration_comp.iloc[1,:][1] - 110000,
             y = 120,
             s = 'Average duration of \nincorrectly predicted \nsalsa set',
             verticalalignment = 'center',
             horizontalalignment = 'left',
             fontdict = {'fontsize':12})

    # Add labels and such
    plt.legend(loc='upper right')
    plt.xlabel('Song Duration (ms)')
    plt.ylabel('No. of Songs')
    plt.title('Song Duration Distributions of Training Set')
    plt.show()