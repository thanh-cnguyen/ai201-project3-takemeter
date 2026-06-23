# TakeMeter

TakeMeter is a fine-tuned text classifier that labels posts and comments from **r/LetsTalkMusic** based on the structure of the take. Instead of judging whether an opinion is correct, the classifier evaluates whether the text is evidence-based, reasoned, or mainly asking the community for input.

## Project Overview

Online music communities contain many different kinds of discussion: historical arguments, subjective opinions, recommendation requests, review-style posts, and broad questions about listening habits. For this project, I built a classifier that categorizes music discourse from `r/LetsTalkMusic` into three labels:

* `evidence_based_take`
* `reasoned_opinion`
* `community_prompt`

The goal was to test whether a small fine-tuned model could learn the difference between a supported argument, a subjective but explained opinion, and a discussion prompt.

## Community Choice

I chose **r/LetsTalkMusic** because it is a text-heavy music discussion subreddit where users post long opinions, reviews, historical analysis, recommendation questions, and personal reflections. The community is a good fit for a classification task because the posts vary in how much evidence, reasoning, and discussion framing they include.

This community also makes the task challenging because music opinions often mix subjective taste with examples. A post may mention many artists or albums, but that does not always mean it is making an evidence-based argument.

## Label Taxonomy

### `evidence_based_take`

A post or comment that makes a clear claim about music and supports it with specific evidence such as songs, albums, lyrics, production details, chart history, genre history, music theory, or concrete comparisons.

**Clear examples:**

1. “James Brown has a strong argument for being the most influential figure in popular music and doesn't get enough credit for it”
2. “Britain's most successful singles band had just one hit in America”

**Decision rule:**
Use this label only when the examples are central to proving the claim. If the examples are mostly decorative or only illustrate the author’s taste, use `reasoned_opinion`.

### `reasoned_opinion`

A post or comment that gives a personal opinion about music and explains the reasoning, but relies mostly on subjective interpretation rather than strong evidence.

**Clear examples:**

1. “Lyrics are massively overvalued in how people judge music”
2. “I do not understand wanting to hear an album again for the first time”

**Decision rule:**
Use this label when the author gives at least one meaningful reason but does not use specific evidence as the main support for the claim.

### `community_prompt`

A post or comment that mainly asks the community for recommendations, lists, memories, favorites, examples, or personal experiences instead of developing its own argument.

**Clear examples:**

1. “What was the last CD you bought and why?”
2. “How do you organise your playlist?”

**Decision rule:**
Use this label when the main purpose is collecting responses from other users. If the author develops a substantial argument before asking the question, label the example based on the argument instead.

## Dataset and Labeling Process

I collected public posts and comments from **r/LetsTalkMusic** and saved them in a single CSV file:

```text
takemeter_dataset_labeled.csv
```

The final dataset contains **220 labeled examples**.

| Label                 |   Count |  Percent |
| --------------------- | ------: | -------: |
| `evidence_based_take` |      95 |    43.2% |
| `reasoned_opinion`    |      76 |    34.5% |
| `community_prompt`    |      49 |    22.3% |
| **Total**             | **220** | **100%** |

The dataset uses three columns:

```text
text,label,notes
```

I originally considered tracking `source_type` and `permalink`, but I kept the final training dataset simpler for compatibility with the starter notebook. The `notes` column was used to track ambiguous cases, AI-assisted pre-labeling, and manual corrections.

After the first annotation pass, `community_prompt` was underrepresented, so I collected additional examples for that label. I kept the final distribution natural to the subreddit while making sure no single label dominated the dataset.

## Difficult Labeling Examples

### Difficult Example 1: Question with a developed opinion

**Text summary:**
A post asks whether others dislike solo acoustic singer-songwriter performances. The author explains that solo acoustic performances can feel monotonous after 1–2 songs and that they prefer seeing multiple musicians play together.

**Possible labels:**
`reasoned_opinion`, `community_prompt`

**Final label:**
`reasoned_opinion`

**Decision:**
Although the post starts with a question, most of the content is the author’s own explained preference. Because the author gives reasons for the opinion, I labeled it as `reasoned_opinion`.

### Difficult Example 2: Personal opinion with factual support

**Text summary:**
A comment argues that an artist is underrated, mentioning his Motown background, his hit “Let’s Get Serious,” Stevie Wonder’s involvement, and chart performance.

**Possible labels:**
`reasoned_opinion`, `evidence_based_take`

**Final label:**
`evidence_based_take`

**Decision:**
The comment includes a subjective claim that the artist is underrated, but the author supports it with specific career details and chart context. Since the examples are central to the claim, I labeled it as `evidence_based_take`.

### Difficult Example 3: Question with a short hypothesis

**Text summary:**
A post asks whether 80s hits have the most staying power and why they seem memorable. The author briefly suggests that the decade may have been important for formulaic hit-making and recognizable production trends.

**Possible labels:**
`reasoned_opinion`, `community_prompt`

**Final label:**
`community_prompt`

**Decision:**
Most of the post is framed as a series of questions asking the community to explain the staying power of 80s hits. Although the author offers a brief hypothesis, that idea is not developed enough to become the main argument.

## Model and Training Approach

I fine-tuned **`distilbert-base-uncased`** using the Hugging Face `Trainer` API in Google Colab. The starter notebook handled the train/validation/test split, tokenization, training loop, evaluation metrics, and confusion matrix generation.

The final test set contained **33 examples**.

### Key Training Decision

I increased the number of training epochs from **3 to 5**.

In an earlier run, the 3-epoch model over-predicted `evidence_based_take`, especially when posts mentioned specific artists, albums, or songs. I increased training to 5 epochs so the classifier had more passes over the small dataset. The final 5-epoch run reached **0.697 validation accuracy** and produced a final test accuracy of **0.667**.

Main training settings:

| Setting             |                     Value |
| ------------------- | ------------------------: |
| Base model          | `distilbert-base-uncased` |
| Training platform   |              Google Colab |
| Epochs              |                         5 |
| Learning rate       |                    `2e-5` |
| Train batch size    |                        16 |
| Eval batch size     |                        32 |
| Weight decay        |                      0.01 |
| Evaluation strategy |                 per epoch |

## Baseline Approach

The baseline was a zero-shot Groq model prompted with the same label definitions and asked to return exactly one label name.

The project specification recommended using Groq’s `llama-3.3-70b-versatile`. I initially attempted that model, but the run hit Groq’s token-per-day limit before completing the full test set. To keep the comparison complete on all 33 test examples, I used Groq’s **`llama-3.1-8b-instant`** instead.

The baseline and fine-tuned model were evaluated on the same locked test set.

### Baseline Prompt Summary

The Groq prompt defined the three labels:

* `evidence_based_take`
* `reasoned_opinion`
* `community_prompt`

It also included decision rules:

* Use `evidence_based_take` only when examples or evidence are central to proving the claim.
* Use `reasoned_opinion` when the author gives at least one meaningful reason but the support is mostly subjective.
* Use `community_prompt` when the main purpose is collecting responses from other users.
* If a post asks a question but develops a substantial argument, label it based on the argument.

The model was instructed to output only the label name.

## Evaluation Results

The final evaluation compared the zero-shot Groq baseline and the fine-tuned DistilBERT model on the same 33-example test set.

| Model                                             | Accuracy |
| ------------------------------------------------- | -------: |
| Zero-shot Groq baseline (`llama-3.1-8b-instant`)  |    0.697 |
| Fine-tuned DistilBERT (`distilbert-base-uncased`) |    0.667 |

The fine-tuned model did not outperform the zero-shot baseline. The baseline was about **0.03** higher in accuracy.

This means the project did not fully meet my original definition of success, which required the fine-tuned model to outperform the zero-shot baseline. However, the fine-tuned model still learned meaningful label patterns and produced useful failure cases for analysis.

### Fine-Tuned Model Per-Class Metrics

| Label                 | Precision | Recall | F1-score | Support |
| --------------------- | --------: | -----: | -------: | ------: |
| `evidence_based_take` |      0.67 |   1.00 |     0.80 |      14 |
| `reasoned_opinion`    |      0.64 |   0.58 |     0.61 |      12 |
| `community_prompt`    |      1.00 |   0.14 |     0.25 |       7 |
| **Accuracy**          |           |        | **0.67** |      33 |
| **Macro avg**         |      0.77 |   0.58 |     0.55 |      33 |
| **Weighted avg**      |      0.73 |   0.67 |     0.61 |      33 |

### Baseline Per-Class Metrics

| Label                 | Precision | Recall | F1-score | Support |
| --------------------- | --------: | -----: | -------: | ------: |
| `evidence_based_take` |      0.88 |   0.50 |     0.64 |      14 |
| `reasoned_opinion`    |      0.58 |   0.92 |     0.71 |      12 |
| `community_prompt`    |      0.83 |   0.71 |     0.77 |       7 |
| **Accuracy**          |           |        | **0.70** |      33 |
| **Macro avg**         |      0.76 |   0.71 |     0.71 |      33 |
| **Weighted avg**      |      0.76 |   0.70 |     0.69 |      33 |

## Confusion Matrix

The fine-tuned model confusion matrix is saved as:

```text
confusion_matrix.png
```

Text version:

| True label \ Predicted label | `evidence_based_take` | `reasoned_opinion` | `community_prompt` |
| ---------------------------- | --------------------: | -----------------: | -----------------: |
| `evidence_based_take`        |                    14 |                  0 |                  0 |
| `reasoned_opinion`           |                     5 |                  7 |                  0 |
| `community_prompt`           |                     2 |                  4 |                  1 |

The confusion matrix shows that the fine-tuned model recognized `evidence_based_take` very strongly, correctly identifying all 14 test examples in that class. However, it struggled with `community_prompt`, correctly identifying only 1 of 7 examples. Most `community_prompt` errors were predicted as `reasoned_opinion`, suggesting that the model had difficulty recognizing when a post’s main purpose was to ask the community for responses rather than make an argument.

## Error Analysis

The fine-tuned model made **11 wrong predictions out of 33 test examples**.

### Main Failure Pattern 1: Over-predicting `evidence_based_take`

The most common failure pattern was that the model predicted `evidence_based_take` when a post or comment mentioned artists, albums, songs, music eras, or examples. This happened even when the author was mainly giving a subjective opinion.

For example, one true `reasoned_opinion` comment said that music quality is mostly about whether something emotionally moves the listener rather than anything technical or objective. The model predicted `evidence_based_take` with **0.44 confidence**, likely because the comment discussed evaluation criteria for music. However, the author was describing a personal standard, so `reasoned_opinion` was the correct label.

Another true `reasoned_opinion` comment criticized a cover song as emotionally empty and musically boring. The model predicted `evidence_based_take` with **0.39 confidence**, likely because the comment gave specific musical criticism. However, the reasoning was still subjective rather than evidence-based.

### Main Failure Pattern 2: Missing `community_prompt`

The model also struggled to identify `community_prompt`. It often predicted `reasoned_opinion` or `evidence_based_take` when the post included background context before asking the community a question.

For example, a post asked whether 80s hits have the most staying power and why they seem so memorable. The correct label was `community_prompt`, but the model predicted `reasoned_opinion` with **0.35 confidence**. The model likely focused on the author’s brief hypothesis about formulaic hit-making and production trends instead of recognizing that the main purpose was to ask the community for explanations.

Another post asked what a song draws from musically, including possible references to English pub music or traditional music. The correct label was `community_prompt`, but the model predicted `reasoned_opinion` with **0.38 confidence**. The post was asking the community to help identify influences, not making a developed argument.

### Main Failure Pattern 3: Surface cues mattered too much

The model appeared to rely on surface cues such as named artists, historical periods, and long explanations. These cues often appear in `evidence_based_take`, but they also appear in subjective opinions and prompts. This suggests that the model learned some vocabulary patterns from the dataset but did not always learn the deeper difference between evidence, reasoning, and intent.

## Specific Wrong Predictions

### Wrong Prediction 1

**Text summary:**
A user says music quality is mostly about whether it emotionally moves them rather than whether it is technical or objective.

**True label:** `reasoned_opinion`
**Predicted label:** `evidence_based_take`
**Confidence:** 0.44

**Analysis:**
The model likely misclassified this because the comment discusses evaluation criteria for music, which can resemble analysis. However, the author is mainly describing a subjective personal standard, so `reasoned_opinion` is the better label.

### Wrong Prediction 2

**Text summary:**
A user criticizes a cover song as emotionally empty, musically boring, and reliant on vocal tricks.

**True label:** `reasoned_opinion`
**Predicted label:** `evidence_based_take`
**Confidence:** 0.39

**Analysis:**
The model likely treated specific musical criticism as evidence-based analysis. The comment gives reasons, but those reasons are subjective judgments about emotional impact and musical boredom rather than a structured evidence-based argument.

### Wrong Prediction 3

**Text summary:**
A post asks whether 80s hits have the most staying power and asks the community why those songs seem so memorable.

**True label:** `community_prompt`
**Predicted label:** `reasoned_opinion`
**Confidence:** 0.35

**Analysis:**
The model likely focused on the author’s brief hypothesis about production trends and formulaic hit-making. The correct label is `community_prompt` because most of the post is framed as questions asking the community for explanations.

## Sample Classifications

| Text summary                                                                                            | Predicted label       | Confidence | Correct? | Explanation                                                                                                                          |
| ------------------------------------------------------------------------------------------------------- | --------------------- | ---------: | -------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| A post/comment made a claim supported by specific examples and was classified as `evidence_based_take`. | `evidence_based_take` |        N/A | Yes      | This prediction is reasonable because the text used examples as support rather than just naming artists or albums.                   |
| A user says music quality is about whether it emotionally moves them rather than technical standards.   | `evidence_based_take` |       0.44 | No       | The correct label was `reasoned_opinion`; the model likely confused discussion of evaluation standards with evidence-based analysis. |
| A post asks whether 80s hits have the most staying power and asks the community to explain why.         | `reasoned_opinion`    |       0.35 | No       | The correct label was `community_prompt`; the post mainly asks the community for explanations.                                       |
| A comment criticizes a cover song as emotionally empty and musically boring.                            | `evidence_based_take` |       0.39 | No       | The correct label was `reasoned_opinion`; the comment gives subjective reasoning, not a structured evidence-based argument.          |

## Reflection: What the Model Learned vs. What I Intended

I intended the model to learn the structural difference between supported arguments, subjective reasoning, and community prompts. The model partially learned this distinction, especially for `evidence_based_take`, where it achieved high recall.

However, the model also appeared to overfit to surface-level signals. It often treated named artists, songs, eras, or specific examples as signs of `evidence_based_take`, even when those examples were part of a subjective opinion. It also struggled with `community_prompt` posts that included background explanation before asking the community a question.

This shows a gap between my label definitions and what the model learned. I wanted the model to classify based on the author’s intent and how evidence was used, but the model often classified based on visible content features such as length, named examples, and music-specific vocabulary.

To improve this model, I would collect more `community_prompt` examples that include long setups, and more `reasoned_opinion` examples that mention artists or songs without using them as structured evidence. That would help the model learn the hard boundaries more clearly.

## Spec Reflection

One way the spec helped was by forcing me to define the labels before collecting the full dataset. That made the annotation process more consistent because I had decision rules for difficult cases such as question-based posts with long personal arguments.

One way my implementation diverged from the spec was the zero-shot baseline model. I originally attempted to use Groq’s `llama-3.3-70b-versatile`, but the full baseline run hit Groq’s token-per-day limit before completing the test set. To keep the baseline comparison complete on all 33 test examples, I used Groq’s `llama-3.1-8b-instant` instead and documented the change.

## AI Usage

I used AI tools in several parts of the project, but I manually reviewed the final labels and analysis.

### 1. Label taxonomy stress-testing

I used AI assistance to refine the label taxonomy before labeling the full dataset. The AI helped identify that my original `low_effort_reaction` label was difficult to find consistently in `r/LetsTalkMusic`, especially because the subreddit tends to encourage longer discussion posts. I removed that label and kept three labels: `evidence_based_take`, `reasoned_opinion`, and `community_prompt`.

### 2. Annotation assistance

I used AI assistance to pre-label batches of examples. I then manually reviewed the labels, corrected cases that did not match my definitions, and added more `community_prompt` examples when that label was underrepresented. I rejected or corrected AI suggestions when the tool treated any mention of an artist, album, or example as automatically evidence-based.

### 3. Failure analysis

I used AI assistance to review the model’s wrong predictions and identify possible failure patterns. I then verified the patterns myself by comparing the wrong predictions with the confusion matrix. The main pattern I kept was that the model over-predicted `evidence_based_take` when examples or named artists appeared in subjective posts.

## Files in This Repository

```text
planning.md
takemeter_dataset_labeled.csv
evaluation_results.json
confusion_matrix.png
README.md
```

## How to Run

1. Open the TakeMeter starter notebook in Google Colab.
2. Upload `takemeter_dataset_labeled.csv`.
3. Run the data loading and split sections.
4. Fine-tune `distilbert-base-uncased`.
5. Run evaluation on the test set.
6. Run the Groq baseline section.
7. Export `evaluation_results.json` and `confusion_matrix.png`.

## Demo Video

Demo video link: TODO

The demo should show:

* 3–5 posts being classified by the fine-tuned model
* label and confidence visible
* one correct prediction with explanation
* one incorrect prediction with explanation
* brief walkthrough of the evaluation report
