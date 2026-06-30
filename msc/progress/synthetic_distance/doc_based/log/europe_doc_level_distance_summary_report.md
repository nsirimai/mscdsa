# European Document-Level Synthetic Sentiment Distance Report

## Corpus balance

- European policy documents: 22
- Original sentiment documents: 17
- Synthetic sentiment documents available: 53
- Selected synthetic sentiment documents: 53
- Balanced sentiment documents: 70

## Character balance

- European policy characters: 1223977
- Original sentiment characters: 829406
- Synthetic characters required: 394571
- Selected synthetic characters: 384754
- Balanced sentiment characters: 1214160

## Original vs selected synthetic sentiment — lexical

| comparison                                                   |   unigram_js_divergence |   bigram_js_divergence |   tfidf_centroid_cosine |
|:-------------------------------------------------------------|------------------------:|-----------------------:|------------------------:|
| original_sentiment_vs_selected_synthetic_sentiment_documents |                0.263494 |               0.585869 |                0.489186 |

## Original vs selected synthetic sentiment — semantic

| comparison                                                   |   embedding_centroid_cosine |   avg_nearest_synthetic_to_original_cosine |   avg_nearest_original_to_synthetic_cosine |   frechet_embedding_distance |   mmd_rbf_embedding_distance |
|:-------------------------------------------------------------|----------------------------:|-------------------------------------------:|-------------------------------------------:|-----------------------------:|-----------------------------:|
| original_sentiment_vs_selected_synthetic_sentiment_documents |                    0.877174 |                                   0.663138 |                                   0.577128 |                     0.821044 |                  0.000756554 |

## Original vs selected synthetic sentiment — C2ST

| comparison                                                   |   accuracy_mean |   accuracy_std |   f1_mean |   f1_std |   roc_auc_mean |   roc_auc_std |
|:-------------------------------------------------------------|----------------:|---------------:|----------:|---------:|---------------:|--------------:|
| original_sentiment_vs_selected_synthetic_sentiment_documents |        0.790476 |       0.122706 |  0.704762 | 0.197834 |              1 |             0 |

Interpretation: High distinguishability.

## European policy comparison

| comparison                            |   unigram_js_divergence |   bigram_js_divergence |   tfidf_centroid_cosine |
|:--------------------------------------|------------------------:|-----------------------:|------------------------:|
| european_policy_vs_original_sentiment |                0.327293 |               0.718301 |                0.714462 |
| european_policy_vs_balanced_sentiment |                0.335498 |               0.739806 |                0.540009 |

## Methodological note

This is a document-level validation calibrated to the France + Ireland policy corpus. The synthetic sentiment corpus is used only as a labelled auxiliary corpus for robustness, sensitivity, and corpus-balance testing.
