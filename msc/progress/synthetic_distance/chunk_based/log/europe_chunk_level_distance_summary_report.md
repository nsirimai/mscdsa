# European Chunk-Level Synthetic Sentiment Distance Report

## Corpus balance

- European policy chunks: 789
- Original sentiment chunks: 536
- Synthetic sentiment chunks available: 212
- Selected synthetic sentiment chunks: 201
- Balanced sentiment chunks: 737

## Character balance

- European policy characters: 1324951
- Original sentiment characters: 900307
- Synthetic characters required: 424644
- Selected synthetic characters: 422859
- Balanced sentiment characters: 1323166

## Original vs selected synthetic sentiment — lexical

| comparison                                                |   unigram_js_divergence |   bigram_js_divergence |   tfidf_centroid_cosine |
|:----------------------------------------------------------|------------------------:|-----------------------:|------------------------:|
| original_sentiment_vs_selected_synthetic_sentiment_chunks |                 0.22134 |               0.581293 |                0.571565 |

## Original vs selected synthetic sentiment — semantic

| comparison                                                |   embedding_centroid_cosine |   avg_nearest_synthetic_to_original_cosine |   avg_nearest_original_to_synthetic_cosine |   frechet_embedding_distance |   mmd_rbf_embedding_distance |
|:----------------------------------------------------------|----------------------------:|-------------------------------------------:|-------------------------------------------:|-----------------------------:|-----------------------------:|
| original_sentiment_vs_selected_synthetic_sentiment_chunks |                      0.9507 |                                   0.720077 |                                   0.668863 |                     0.341638 |                  0.000390827 |

## Original vs selected synthetic sentiment — C2ST

| comparison                                                |   accuracy_mean |   accuracy_std |   f1_mean |    f1_std |   roc_auc_mean |   roc_auc_std |
|:----------------------------------------------------------|----------------:|---------------:|----------:|----------:|---------------:|--------------:|
| original_sentiment_vs_selected_synthetic_sentiment_chunks |        0.952778 |      0.0120362 |  0.950229 | 0.0133144 |       0.995024 |    0.00664664 |

Interpretation: High distinguishability.

## European policy comparison

| comparison                            |   unigram_js_divergence |   bigram_js_divergence |   tfidf_centroid_cosine |
|:--------------------------------------|------------------------:|-----------------------:|------------------------:|
| european_policy_vs_original_sentiment |                0.329685 |               0.732191 |                0.541206 |
| european_policy_vs_balanced_sentiment |                0.338303 |               0.747242 |                0.500196 |

## Methodological note

This is a chunk-level validation calibrated to the France + Ireland policy corpus. The synthetic sentiment corpus is used only as a labelled auxiliary corpus for robustness, sensitivity, and corpus-balance testing.
