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

![no_of_sections](/images/no_of_sections.png) ![avg_section_len](/images/avg_section_len.png)

Each feature has nearly indistinguishable distributions, so it is no wonder the models cannot tell them apart. I am lead to believe that this issue is due to Spotify's audio analysis algorithms. I personally compared Spotify's designated section start times and durations to what I—as a musician—would classify. Rarely were they accurate. I attribute this to the fact that salsa songs do not have a clear verse/chorus distinction like bachata, which probably throws Spotify's algorithms off, resulting in incorrect section analysis.

# Model Evaluation

Seeing that the best performing model is the grid search-optimized random forest without any engineered features, we will now evaluate its efficacy and limitations in more detail.

![confusion matrix](/images/confusion_matrix.png)

The confusion matrix of the random forest model shows us that, although the model performs quite well, it incorrectly misclassifies salsa songs as bachata more often than the other way around. Examining the magnitude of feature importances gives us some insight as to why this is.

![feature importance](/images/feature_importance.png)

Tempo is by far the most important feature for the model. This is no surprise, as tempo is one of the most obvious and stark differences between the genres. The other musical differences, such as instrumentation, are not as easily discerned by the audio features Spotify provides through its API.

I predict the incorrectly classified salsa songs will  exhibit traits of bachata songs in most features, and vice versa with bachata. I'll examine tempo and duration because they are the two most important features for the model and they also are two of the most interpretable features.

In order to evaluate my prediction, I compare average values of the features of songs that were incorrectly predicted to average values of features in the training set.

#### Tempo Comparison

![incorrect tempo](/images/incorrect_tempo.png)

The mean salsa tempo of the training set is closer to the  cluster of salsa tempos around 90 bpm, whereas the mean of incorrectly predicted salsa tracks is almost exactly equal to the mean bachata tempo from the training set. It is no wonder the model would think that a song with a tempo right in the bachata region would make an incorrect classification.

Additionally, it appears that salsa has a lower average tempo than bachata. However, salsa is actually known to have a much higher tempo than bachata in real life. The discrepancy here must be attributed to Spotify API's tempo analysis. I have found after listening to several songs in the 90-100 salsa bpm range that many songs with a tempo above 160 have been incorrectly quantified at half tempo by Spotify API's analysis. In reality, we should see many more data points accompanying the small cluster of points that are roughly centered around 178 bpm. I am curious about songs in the range of about 115 - 140 bpm though. My first instinct to fix this problem would just be to double the tempo of every salsa song that has a tempo below 160 bpm, which looks like a good cutoff. However, by doing this we would have to consider the ramifications of the following:

1. Not every song in the salsa data set is actually salsa. Songs are assigned genres at the album level. Often times salsa artists include one or even more "cha cha cha" songs in their albums to add variety. The main distinction between cha cha cha songs and salsa is the tempo. I could research the range of tempos for cha cha cha songs, remove data points within that range from our data set, and run the models again.


2. It turns out salsa artists also like to dabble in other genres and from time to time will even include a reggaeton song or merengue (or even bachata!) which have a wide range of tempos. It is unfortunate the genres are assigned at the album level because there is really no way other than looking through individual tracks in an album to identify non-salsa and non-bachata songs. This would require too much work given the large data set, but would be possible if one were really interested in training an accurate model.

The issue of addressing incorrectly assigned tempos here is a delicate one. There are many things to consider, and ultimately the model performs well enough as it is now. I will leave this to be addressed as a future direction in the interest of time.

#### Duration Comparison

Let's continue and evaluate the comparison in track duration.

![incorrect duration](/images/incorrect_duration.png)

Again, we see the incorrectly predicted salsa songs have an average tempo that more closely resembles that of a bachata song. There is probably nothing that really can be done here, because these values are not extrapolated by any Spotify API metrics. They are simply an inherent property of the song.

# Conclusion & Future Directions

Utlimately, the model performs quite well. In general, the main limitations of the random forest model are due to the data. We see from histograms comparing salsa and bachata properties that only a couple features really exhibit distinguishable distributions. To improve the model, I could attempt to engineer more features, is this really necessary though if the model is already so robust? Maybe not.

I only compared three types of classification models here. It would have been good to see how the data would be handled by other models such as XGBoost, SVM, etc. Additionally, I am interested in expanding this to a multi class problem. The original idea behind this project was to build a model that would help you distinguish between salsa and bachata songs at a dance venue. However, often times latin clubs will play what is known as "Latin mix", which consists of not just salsa and bachata but also merengue and reggaeton. Again, the four genres are quite distinct to the trained ear, but maybe not so much to a newcomer. I am interested in seeing how machine learning models could distinguish between the four genres.
