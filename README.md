# Salsa/Bachata Classifier

These two popular latin music genres are easily distinguished by the trained ear based on trends in tempo, instrumentation, song structure, and harmonic progressions, among other traits. The untrained ear may have trouble discerning between them though. At a dance party, one who cannot distinguish between the two genres could risk the embarrassment of trying to dance the wrong steps to a particular song. The goal of this project is to train a machine to assist in the classification between salsa and bachata.

# Data
Audio information was obtained from the Spotify API on roughly 1400 tracks from 8 popular salsa and bachata artists. There is roughly a 45:55 ratio between salsa and bachata songs. Audio features from spotify include:
* tempo
* key 
* duration
* acousticness
* loudness
* etc.

many of which are features which Spotify has engineered from its own audio analysis of the wave files. The full list of features can be found [here](https://developer.spotify.com/documentation/web-api/reference/tracks/get-audio-features/). Some of [this analysis](https://developer.spotify.com/documentation/web-api/reference/tracks/get-audio-analysis/) is also available on their API, and was used in order to engineer two new features for my models: 

* number of song sections 
* average duration of song sections

# Feature Engineering

Three classification models were fit and compared by F1 score on test data. Hyperparameters were tuned using GridSearch CV. 

![model comparison](/images/model_comparison.png)


Of the three models, two of them (decision tree and random forest) were used to compare the effects of two features that were engineered from Spotify's audio analysis data. These features are
1. Number of musical sections (verse, chorus, bridge, etc.)
2. Average length of musical sections

I believe these features will help distinguish between the genres because salsa and bachata differ greatly in these regards, but the Spotify API does not inherently provide these audio features.

We define the most effective model here using the F1 score, as neither type 1 nor type 2 errors are more significant than the other in the context of picking the right type of dance to a song. The results of the model show that adding the enginnered features does not significantly improve the F1 score. This becomes clear when we examine the distribution of the engineered features between salsa and bachata.

![no_of_sections](/images/no_of_sections.png)

![avg_section_len](/images/avg_section_len.png)

Each feature has nearly indistinguishable distributions, so it is no wonder the models cannot tell them apart. I am lead to believe that this issue is due to Spotify's audio analysis algorithms. I personally compared Spotify's designated section start times and durations to what I—as a musician—would classify. Rarely were they accurate. I attribute this to the fact that salsa songs do not have a clear verse/chorus distinction like bachata, which probably throws Spotify's algorithms off, resulting in incorrect section analysis. 

# Model Evaluation

Seeing that the best performing model is the grid search-optimized random forest without any engineered features, we will now evaluate its efficacy and limitations in more detail.

![confusion matrix](/images/confusion_matrix.png)

The confusion matrix of the random forest model shows us that, although the model performs quite well, it incorrectly misclassifies salsa songs as bachata more often than the other way around. Examining the magnitude of feature importances gives us some insight as to why this is.

![feature importance](/images/feature_importance.png)

Tempo, duration, danceability, and energy appear to be the top distinguishing features between salsa and bachata songs. I hypothesized that the incorrectly classified songs would likely have tempos and durations that are more characteristic of the other genre. For instance, we see from the tempo distributions that bachata has a higher mean tempo.

![tempo dist](/images/tempo_dist.png)

I therefore expect incorrectly classified salsa songs to have higher tempo than the average for salsa. Below is a comparison of the average tempo of songs for the entire data set versus the average tempo of the incorrectly classified songs.

![incorrect tempo](/images/incorrect_tempo.png)

The average tempo for bachata in the full data set is higher than that of salsa. However, the average tempo of salsa songs that were incorrectly classified as bachata is **above** that of the average for bachata in the full data set. This means that the greatest predictor for the model, tempo, was leading it to strongly believe the song is actually bachata.

I should note that in reality, salsa songs are much faster than bachata. Thus, we find another error in Spotify's audio analysis algorithms - it actually incorrectly assigns many song tempos to half time. For example, this means they classify songs that might be in the range of 180 - 220 bpm as being 90 - 110 bpm. Fortunately, it's still not a huge issue as we see the model achieves an F1 of roughly 94%. That being said, the model could be improved by either writing my own algorithm to analyze tempo and other features, or by Spotify improving its own algorithms.

Similar issues are present with the other top predictors. In general, I believe they would all be improved by Spotify improving its audio analysis algorithms. Is this really necessary though if we already have such a robust model? For our purposes, maybe not. However, if I were to expand this to a multi class problem it would be imperative for all of the audio features to be correct.

