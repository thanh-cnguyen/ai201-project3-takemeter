# TakeMeter — planning.md

---

## Objective

TakeMeter will classify posts and comments from **r/LetsTalkMusic** based on how developed, supported, or discussion-oriented the post is. Instead of judging whether an opinion is “right,” the classifier will evaluate the structure of the take: whether it is evidence-based, reasoned, or mainly asking the community for input.

---

## Community

I chose [**r/LetsTalkMusic**](https://www.reddit.com/r/LetsTalkMusic/) because it is a text-heavy music discussion community where users post reviews, opinions, questions, historical analysis, and listening reflections. These posts vary in how much evidence and reasoning they include, which makes the subreddit a good fit for a discourse-quality classification task.

---

## Labels

- `evidence_based_take`
- `reasoned_opinion`
- `community_prompt`

### evidence_based_take

**Definition:**  
A post that makes a clear claim about music and supports it with specific evidence such as songs, albums, lyrics, production details, chart history, genre history, music theory, or concrete comparisons.

**Inclusion criteria:**  
Use this label when the author is not just stating an opinion, but building an argument with evidence.

**Exclusion criteria:**  
Do not use this label if the post only names songs or artists without explaining how they support the claim.

**Clear examples:**  
1. [“James Brown has a strong argument for being the most influential figure in popular music and doesn't get enough credit for it”](https://www.reddit.com/r/LetsTalkMusic/comments/1tewic0/james_brown_has_a_strong_argument_for_being_the/)  
2. [“Britain's most successful singles band had just one hit in America”](https://www.reddit.com/r/LetsTalkMusic/comments/1u4qhax/britains_most_successful_singles_band_had_just/)

**Boundary / edge case:**  
This can overlap with `reasoned_opinion` when a post includes examples but still mainly feels like personal taste.

**Decision rule:**  
Use `evidence_based_take` only if the examples are central to proving the claim. If the examples are mostly decorative, use `reasoned_opinion`.


### reasoned_opinion

**Definition:**  
A post that gives a personal opinion about music and explains the reasoning, but relies mostly on subjective interpretation rather than strong evidence.

**Inclusion criteria:**  
Use this label when the author explains why they feel a certain way about an artist, album, song, genre, or trend.

**Exclusion criteria:**  
Do not use this label if the post has little explanation beyond praise, dislike, shock, or a one-line reaction.

**Clear examples:**  
1. [“Lyrics are massively overvalued in how people judge music”](https://www.reddit.com/r/LetsTalkMusic/comments/1tfmp9w/lyrics_are_massively_overvalued_in_how_people/)  
2. [“I do not understand wanting to hear an album again for the first time”](https://www.reddit.com/r/LetsTalkMusic/comments/1u44dqt/i_do_not_understand_wanting_to_hear_an_album/)

**Boundary / edge case:**  
This can overlap with `evidence_based_take` when the post includes examples, artists, or albums but still relies mostly on personal interpretation.

**Decision rule:**  
Use `reasoned_opinion` if the author gives at least one meaningful reason but does not use specific evidence as the main support for the claim. Use `evidence_based_take` only when the examples are central to proving the argument.


### community_prompt

**Definition:**  
A post that mainly asks the community for recommendations, lists, memories, favorites, examples, or personal experiences instead of developing its own argument.

**Inclusion criteria:**  
Use this label when the post is designed to generate responses from other users.

**Exclusion criteria:**  
Do not use this label if the author asks a question after making a substantial argument; in that case, label the post based on the argument.

**Clear examples:**  
1. [“What was the last CD you bought and why?”](https://www.reddit.com/r/LetsTalkMusic/comments/1u5kinp/what_was_the_last_cd_you_bought_and_why/)  
2. [“How do you organise your playlist?”](https://www.reddit.com/r/LetsTalkMusic/comments/1u57xsy/how_do_you_organise_your_playlists/)

**Boundary / edge case:**  
This can overlap with `reasoned_opinion` when the author gives their own view before asking the question.

**Decision rule:**  
Use `community_prompt` if the question is the main content. If the author’s own argument is substantial, use `reasoned_opinion` or `evidence_based_take`.

---

## Hard Edge Cases

### Evidence-based take vs. reasoned opinion

Some posts mention specific artists, albums, songs, or examples, but still mainly rely on personal interpretation. I will label a post as `evidence_based_take` only when the examples are central to proving the claim. If the examples mainly illustrate the author’s taste or feelings, I will label it as `reasoned_opinion`.

### Reasoned opinion vs. community prompt

Some posts begin with the author’s opinion and then ask the community a question. I will label the post as `community_prompt` only when the main purpose is to collect responses from other users. If the author develops a substantial argument before asking the question, I will label it as `reasoned_opinion` or `evidence_based_take`.

### Short unsupported reactions

Some comments may only express quick praise, dislike, or agreement without explanation. Since I removed the `low_effort_reaction` label to keep the taxonomy grounded in `r/LetsTalkMusic`, I will avoid using extremely short unsupported reactions as training examples when possible. If a short comment includes at least one meaningful reason, I will label it as `reasoned_opinion`.

---

## Data Collection Plan

I will collect at least 200 public posts and comments from **r/LetsTalkMusic**. I will save the data in a single CSV file with the columns `text`, `label`, `source_type`, `permalink`, and `notes`.

My target distribution is roughly balanced across the three labels:

* `evidence_based_take`: about 65–75 examples
* `reasoned_opinion`: about 65–75 examples
* `community_prompt`: about 65–75 examples

If one label is underrepresented after collecting 200 examples, I will collect additional examples for that label before training. I will avoid letting any one label exceed 70% of the dataset because that could cause the model to over-predict the majority class.

---

## Evaluation Metrics

I will evaluate both the fine-tuned model and the zero-shot baseline using overall accuracy and per-class F1 score. Accuracy is useful because it gives a simple view of how often the model predicts the correct label, but it is not enough by itself because the dataset may not be perfectly balanced across labels.

Per-class F1 is important because it shows whether the model performs well across all three labels instead of only learning the most common one. I will also review the confusion matrix to identify which label pairs are most often confused, such as `evidence_based_take` being predicted as `reasoned_opinion`.

---

## Definition of Success

I will consider the fine-tuned classifier successful if it reaches at least **70% overall accuracy** on the test set and at least **0.65 F1 score for each label**. These thresholds are realistic for a subjective 3-label classification task with around 200 examples, while still requiring the model to perform better than random guessing or majority-class prediction.

I will also consider the project successful only if the fine-tuned model performs better than the zero-shot Groq baseline on the same test set. If the model has high accuracy but very low F1 for one label, I will not treat it as fully successful because that would mean it is failing to learn one of the label boundaries.

For a real community tool, this classifier would be “good enough” if it could help organize posts by discourse type for review or analysis, but not if it were used as an automatic moderation system. Ambiguous music opinions still need human judgment.

---

## AI Tool Plan

### Label stress-testing

I will use AI tools to test whether my label definitions are clear. I will ask the AI to generate borderline examples between `evidence_based_take`, `reasoned_opinion`, and `community_prompt`. If the generated examples are difficult to classify consistently, I will revise the definitions and decision rules before labeling the full dataset.

### Annotation assistance

I may use an AI tool to pre-label a small batch of examples, but I will manually review and correct every label before adding it to the final dataset. If I use AI pre-labeling, I will track it in the `notes` column with a note such as `AI pre-label reviewed`. I will disclose this workflow in the README AI usage section.

### Failure analysis

After evaluating the fine-tuned model, I will give the wrong predictions to an AI tool and ask it to identify possible error patterns. I will verify those patterns myself by rereading the examples and comparing them against the confusion matrix before writing the final README analysis.

---


