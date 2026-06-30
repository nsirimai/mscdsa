"""

@author: aurelia power
"""

import re, pandas as pd, numpy as np, matplotlib.pyplot as plt, seaborn as sns
import nltk
from collections import Counter 
import warnings 
warnings.filterwarnings('ignore') 
from sklearn.feature_extraction.text import CountVectorizer 
from sklearn.feature_extraction.text import TfidfVectorizer

from sklearn.metrics import confusion_matrix, RocCurveDisplay
from sklearn.metrics import classification_report
from sklearn.model_selection import cross_val_predict, train_test_split
from sklearn.model_selection import cross_validate, StratifiedKFold

from sklearn.feature_selection import chi2
from sklearn.feature_selection import f_classif
from sklearn.feature_selection import GenericUnivariateSelect
from sklearn.preprocessing import LabelEncoder

from sklearn.preprocessing import label_binarize
from sklearn.metrics import roc_curve, auc
from sklearn.multiclass import OneVsRestClassifier

import wordcloud 

#########################################################
########## vectorisation functions ######################
"""
NOTE: all vectorisers from sklearn discard punctuation, which may not be appropriate.
So, need to specify a regex to deal with this situation. 
"""
token_regex = r"(?u)\w+(?:'\w+)?|[^\w\s]" 

"""
function to build count, tf, or tfidf matrix; takes in a list of documents, applies the 
vectoriser from sklearn using mostly default hyperparams by default;
by default it builds a tfidf matrix, but can build count matrix using the is_count=True; 
to build a tf matrix only, set use_idf=False
it returns a data frame for more intuitive view"""
def build_matrix(docs, is_count=False, decode_error='replace', strip_accents=None,
                       lowercase=False, token_pattern=token_regex, ngram_range=(1, 1),
                       norm='l2', use_idf=True, sublinear_tf=False):
    if is_count:
      vectorizer = CountVectorizer(decode_error=decode_error, strip_accents=strip_accents,
                                 lowercase=lowercase, token_pattern=token_pattern,
                                 ngram_range=ngram_range)
    else:
      vectorizer = TfidfVectorizer(decode_error=decode_error, strip_accents=strip_accents,
                                 lowercase=lowercase, token_pattern=token_pattern,
                                 ngram_range=ngram_range, norm=norm, use_idf=use_idf,
                                 sublinear_tf=sublinear_tf)
    X = vectorizer.fit_transform(docs)
    terms = list(vectorizer.get_feature_names_out())
    tfidf_matrix = pd.DataFrame(X.toarray(), columns=terms)
    return tfidf_matrix.fillna(0)
    
############################################################################
########### CLASSIFICATION EVALUATION (from last year) #####################
############################################################################

## function to plot the confusion matrix given the true labels and the predicted labels
def plot_confusion_matrix(y_test, predictions):
  # get and output the confusion matrix
  confusion_m = confusion_matrix(y_test, predictions)
  # can also visualise it
  labels = np.unique(y_test)
  confusion_frame = pd.DataFrame(confusion_m,
                            index=labels, columns=labels)
  plt.figure(figsize=(5, 5))
  sns.heatmap(data=confusion_frame, annot=True, square=True,
              cbar=False)
  plt.xlabel('Predicted Labels')
  plt.ylabel('Actual Labels')
  plt.show()

def plot_confusion_matrix_2(y_test, predictions):
    # Get the confusion matrix
    confusion_m = confusion_matrix(y_test, predictions)
    # Get unique labels
    labels = np.unique(y_test)
    # Create DataFrame with labels
    confusion_frame = pd.DataFrame(confusion_m,
                                   index=labels, 
                                   columns=labels)
    # Increase figure size (width, height)
    plt.figure(figsize=(5, 5))  # Adjust to fit all labels
    
    # Plot heatmap
    sns.heatmap(data=confusion_frame, annot=True, fmt='d',
                cbar=False, square=True)
    
    plt.xlabel('Predicted Labels')
    plt.ylabel('Actual Labels')
    plt.xticks(rotation=45)  # Rotate x-axis labels for readability
    plt.yticks(rotation=0)
    plt.tight_layout()
    plt.show()



"""
function to output the average scores and their stds for accuracy, precision, recall, and f-measure metrics;
it takes as arguments the classifier, the regular attributes data, the label column data;
it defines 1 default parameter: the number of folds that's set to 5
"""
def cross_validation_avg_scores(clf, X, y, cv_=5):
  scoring_metrics = ['accuracy', 'precision_macro', 'recall_macro', 'f1_macro']
  scores = cross_validate(clf, X, y, scoring=scoring_metrics, groups=y, cv=cv_)
  print(f"Mean accuracy: {scores['test_accuracy'].mean()*100:.2f}% +/-{scores['test_accuracy'].std()*100:.2f}%")
  print(f"Mean precision: {scores['test_precision_macro'].mean()*100:.2f}% +/-{scores['test_precision_macro'].std()*100:.2f}%")
  print(f"Mean recall: {scores['test_recall_macro'].mean()*100:.2f}% +/-{scores['test_recall_macro'].std()*100:.2f}%")
  print(f"Mean F1-score is {scores['test_f1_macro'].mean()*100:.2f}% +/-{scores['test_f1_macro'].std()*100:.2f}%")

## function that combines the 2 above
def custom_crossvalidation(X, y, clf, cv_=5):  
  cross_validation_avg_scores(clf, X, y, cv_=cv_)
  predictions = cross_val_predict(clf, X, y, cv=cv_)
  print(classification_report(y, predictions))
  plot_confusion_matrix(y, predictions) 


"""
function to generate the test dataset with added columns for predictions and confidence levels;
it takes as arguments an already trained classifier, the regualr attributes data, and the corresponding labels
"""
def get_test_confidence_dataset(clf, X_test, y_test):
  confidences = clf.predict_proba(X_test)
  predictions = clf.predict(X_test)
  output = X_test.copy()
  output['true labels'] = y_test
  output['predictions'] = predictions
  for i, class_name in enumerate(clf.classes_):
    output[f'confidence_{class_name}'] = confidences[:, i]
  return output


"""
function to generate and plot multiclass rocs for several classifiers;
it takes as arguments a dictionary of classifiers, the regular data, the label data, the size of the test portion, and the random state
"""
def plot_multiclass_roc(clfs_dict, X, y, test_size_=0.3, random_state_=43):
  # binarize the labels for multi-class ROC
  classes = list(range(len(np.unique(y))))
  labels = label_binarize(LabelEncoder().fit_transform(y), classes=classes)
  n_classes = labels.shape[1]
  X_train, X_test, y_train, y_test = train_test_split(
                                X, labels,
                                test_size=test_size_,
                                stratify=labels,
                                random_state=random_state_)
  # use the One-vs-Rest classier to wrap around each classifier
  y_scores = {}
  # iterate though each classifier, wrap a One-vs-Rest classier around each,
  # train the wrapper and add the resulting probabilities to the scores
  for name, clf in clfs_dict.items():
      clf = OneVsRestClassifier(clf)
      clf.fit(X_train, y_train)
      y_scores[name] = clf.predict_proba(X_test)  
  plt.figure(figsize=(7, 5))
  # iterate through each score, compute fprs, tprs, rocs, aucs
  for name, y_score in y_scores.items(): 
    fpr = dict()
    tpr = dict()
    roc_auc = dict()
    for i in range(n_classes):
        fpr[i], tpr[i], _ = roc_curve(y_test[:, i], y_score[:, i])
        roc_auc[i] = auc(fpr[i], tpr[i])
    # compute micro-average roc and auc
    fpr["micro"], tpr["micro"], _ = roc_curve(y_test.ravel(), y_score.ravel())
    roc_auc["micro"] = auc(fpr["micro"], tpr["micro"])  
    plt.plot(fpr["micro"], tpr["micro"],
          label=f'{name}: micro-average ROC curve (area = {roc_auc["micro"]:0.2f})')
  # add the diagonal line for random guess
  plt.plot([0, 1], [0, 1], 'k--')
  plt.xlabel('False Positive Rate')
  plt.ylabel('True Positive Rate')
  plt.title('ROC Curves for 3 classifiers on Iris Dataset')
  plt.legend(loc="best")
  plt.show()

#############################################
############ text visualisations ############

"""
takes in a list of tagged documents and a POS(as a string) 
returns the normalised count of a POS for each tagged document 
"""
def normalise_POS_counts(tagged_docs, pos):
	counts = []
	for doc in tagged_docs:
		count = 0
		for pair in doc:
			if pair[1] == pos:
				count += 1
		counts.append(count)
	lengths = [len(doc) for doc in tagged_docs]
	return [count/length for count, length in zip(counts, lengths)]

"""
takes in a list of documents, a POS(as a string), and a list of categories/labels;
it tags the documents and calls the above function;
it then plots the normalised frequency of the POS across all labels;
"""
def plot_POS_freq(docs, pos, labels):
	tagged_docs = [nltk.pos_tag(nltk.word_tokenize(doc)) for doc in docs]
	normalised_counts = normalise_POS_counts(tagged_docs, pos)
	plt.bar(np.arange(len(docs)), normalised_counts, align='center')
	plt.xticks(np.arange(len(docs)), labels, rotation=40)
	plt.xlabel('Label (Category)')
	plt.ylabel(pos + ' frequency')
	plt.title('Frequency distribution of ' + pos)

""" function to generate the word cloud for a given topic/class """
def generate_cloud(text, topic, bg_colour='black', min_font=10):
    cloud = wordcloud.WordCloud(width=700, height=700, random_state=1, background_color=bg_colour, min_font_size=min_font).generate(text) 
    plt.figure(figsize=(7, 7), facecolor=None) 
    plt.imshow(cloud) 
    ##plt.axis('off') 
    plt.tight_layout(pad=0) 
    plt.xlabel(topic) 
    plt.xticks([]) 
    plt.yticks([]) 

"""function to generate multiple word clouds for a set of topics/classes/categories"""
def generate_wordclouds(texts, categories, bg_colour, min_font=10):
  fig = plt.figure(figsize=(21, 7))
  for i in range(len(texts)):
    ax = fig.add_subplot(1,3,i+1)
    cloud = wordcloud.WordCloud(width=700, height=700, random_state=1, 
                      background_color=bg_colour, 
                      min_font_size=min_font).generate(texts[i])
    ax.imshow(cloud)
    ax.axis('off')
    ax.set_title(categories[i])



#########################################################
############# word stats functions ######################
## function to print the n most frequent tokens in a text belonging to a given topic
def print_n_most_frequent(topic, text, n):
    tokens = nltk.word_tokenize(text) 
    counter = Counter(tokens) 
    n_freq_tokens = counter.most_common(n) 
    print("=== "+ str(n) + " most frequent tokens in "  + topic + " ===") 
    for token in n_freq_tokens:
        print("\tFrequency of", "\"" + token[0] + "\" is:", token[1]/len(tokens)) 
        
## function to find the frequency of a token in several texts belonging to same topics/classes        
def token_percentage(token, texts):
    token_count = 0 
    all_tokens_count = 0 
    for text in texts:
        tokens = nltk.word_tokenize(text) 
        token_count += tokens.count(token) 
        all_tokens_count += len(tokens) 
    return token_count/all_tokens_count * 100 
        
#########################################################
############# preprocessing functions ###################
## function to carry out some initial cleaning
def clean_doc(doc, clean_operations):
    for key, value in clean_operations.items():
        doc = re.sub(key, value, doc) 
    return doc 

## function to resolve contractions
def resolve_contractions(doc, contr_dict):
    for key, value, in contr_dict.items():
        doc = re.sub(key, value, doc) 
    return doc 
    
## function to carry out concept typing, resolve synonyms and word variations
def improve_bow(doc, repl_dict):
    for key in repl_dict.keys():
        for item in repl_dict[key]:
            doc = re.sub(item, key, doc, flags=re.IGNORECASE)
    return doc

## function to remove tokens using POS  tags
def remove_terms_by_POS(doc, tags_to_remove):
    tagged_doc = nltk.pos_tag(nltk.word_tokenize(doc)) ## (sea, 'NN')
    new_doc = [pair[0] for pair in tagged_doc if pair[1] not in tags_to_remove]
    new_doc = ' '.join(new_doc)
    ## replace space before punctuation sign
    return re.sub(r' (?=[!\.,?:;])', "", new_doc)


## function to remove stop words and/or punctuation
def remove_sw_punct(doc, to_remove):
    tokens = nltk.word_tokenize(doc)
    return re.sub(r' (?=[!\.,?:;])', "",
                  ' '.join([token for token in tokens if token not in to_remove]))


## function to remove short tokens
def remove_by_token_len(doc, n):
    tokens = nltk.word_tokenize(doc);
    return re.sub(r' (?=[!\.,?:;])', "",
                  ' '.join([token for token in tokens if len(token) > n]))

## function to remove digits
def remove_d(doc):
    return re.sub(r'\d+', '', doc)

## function to carry out stemming
def stem_doc(doc, stemmer):
    tokens = nltk.word_tokenize(doc)
    return ' '.join([stemmer.stem(t, to_lower=False) for t in tokens])


########################################################################
######################### feature selection ############################
########################################################################

""" function to perform univariate feature selection within a cross-validation loop
    to prevent data leakage."""
def univariate_feature_selection_cv(X: pd.DataFrame, y: pd.Series, score_func=f_classif,
    mode: str='percentile', param=50, n_splits: int=5, random_state: int=43):
    # initialise cross-validator
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=random_state)
    # store resutls in lists
    fold_selected_features = []
    features_intersection = []
    fold_scores = []
    fold_pvalues = []
    # in each fold we do the following:
    for train_idx, _ in skf.split(X, y):
        X_train, y_train = X.iloc[train_idx], y.iloc[train_idx]
        # initialize and train the feature selector only on the training data
        selector = GenericUnivariateSelect(score_func=score_func, mode=mode, param=param)
        selector.fit(X_train, y_train)
        # get selected features for this fold and append them to the lists
        mask = selector.get_support()
        selected_features = list(X_train.columns[mask])
        fold_selected_features.append(selected_features)
        features_intersection.append(set(selected_features))
        # get scores and p-values for this fold and append them to their lists
        scores_sel = selector.scores_[mask] if selector.scores_ is not None else np.array([])
        pvals_sel  = selector.pvalues_[mask] if selector.pvalues_ is not None else np.array([])
        fold_scores.append(list(scores_sel))
        fold_pvalues.append(list(pvals_sel))
    # aggregate the results across folds by looking at the intersection/the set
    # of features selected consistently across all folds
    # intersection across folds: features selected in every fold
    if features_intersection:
        consistent_features = set.intersection(*features_intersection)
    else:
        consistent_features = set()
    # if there are no consistent features return empty results
    if not consistent_features:
        print("Warning: No features were consistently selected across all folds.")
        empty_results_df = pd.DataFrame(columns=['Feature', 'Mean_Score', 'Mean_P_Value'])
        empty_transformed_df = pd.DataFrame()
        return empty_results_df, empty_transformed_df
    # preserve original column order for consistent features
    ordered_consistent = [c for c in X.columns if c in consistent_features]
    # collect scores and p-values for each consistent feature across folds
    consistent_scores = {f: [] for f in ordered_consistent}
    consistent_pvals = {f: [] for f in ordered_consistent}
    # go through each
    for selected_list, scores_list, pvals_list in zip(fold_selected_features, fold_scores, fold_pvalues):
        # selected_list, scores_list, pvals_list are aligned by index
        for feat, sc, pv in zip(selected_list, scores_list, pvals_list):
            if feat in consistent_scores:
                consistent_scores[feat].append(sc)
                consistent_pvals[feat].append(pv)
    # compute means
    mean_scores = {f: float(np.mean(consistent_scores[f])) for f in ordered_consistent}
    mean_pvals  = {f: float(np.mean(consistent_pvals[f]))  for f in ordered_consistent}
    # create the dataframe
    aggregated_results = pd.DataFrame({
        'Feature': list(consistent_features),
        'Score': [mean_scores[f] for f in consistent_features],
        'P_Value': [mean_pvals[f] for f in consistent_features]
    })
    # transform the data by retaining values across those consitently selcted features
    transformed_data = X[list(consistent_features)].copy()
    # retrun the 2 data frames
    return aggregated_results, transformed_data

