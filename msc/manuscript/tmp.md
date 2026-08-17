Yes. Looking directly at the two notebooks, I think the source of the confusion is that **both are comparing policy and sentiment semantically**, but they do it at very different levels.

The simplest way to see it is:

> **Pipeline 1 = detect explicit causal statements first, then measure semantic coverage.**
> **Pipeline 2 = read the evidence directly, interpret the relationship between policy and sentiment, then verify that interpretation.**

And one important correction: the first pipeline is not purely rule-based end-to-end. It is **rule-based causal extraction + embedding-based semantic matching**.

---

## 1. The two pipelines in one picture

### Pipeline 1 — causal NLP

Your `1_semantic_causal_claim_coverage...ipynb` essentially does:

```text
Clean sentences
       ↓
Rule-based causal cue detection
       ↓
cause ──relation──> effect
       ↓
Sentence embeddings
       ↓
Top-3 nearest causal claims in other corpus
       ↓
Similarity
       ↓
Coverage deficit = 1 - similarity
       ↓
Topic / country / global statistics
```

For example:

```text
"Teacher training can reduce inappropriate use of AI."
```

The rule sees **"reduce"** and produces:

```text
Cause:
Teacher training

Relation:
reduces_or_prevents

Effect:
inappropriate use of AI
```

Only sentences that survive this extraction stage become causal claims.

Your notebook extracted:

* **3,930 policy causal claims**
* **761 sentiment causal claims**

and then compared those claims using multilingual Sentence-BERT.

---

### Pipeline 2 — agentic semantic gap

Your `3_agentic_semantic_gap_analysis...ipynb` does something fundamentally different:

```text
Clean sentences
       ↓
Take policy + sentiment evidence directly
       ↓
Build balanced evidence package
       ↓
Agent reads the evidence
       ↓
"What is aligned / missing / conflicting?"
       ↓
Candidate semantic finding
       ↓
Second agent independently verifies it
       ↓
Evidence-ID / confidence / faithfulness checks
       ↓
Repeat analysis
       ↓
Stability check
       ↓
Human review
```

There is **no regex causal extraction before the agent**.

That is the crucial difference.

---

# 2. Let's use exactly the same example through both pipelines

Imagine the corpus contains these four sentences.

### Policy

**P1**

> Teacher training can reduce inappropriate use of generative AI.

**P2**

> Schools should publish clear guidance for AI-assisted assessment.

### Sentiment

**S1**

> Teachers are reluctant to use AI in assessment when school guidance is unclear.

**S2**

> Many teachers say they have received little practical training in generative AI.

Now watch what happens.

---

# 3. Pipeline 1 step by step

## Step 1 — look for predefined causal language

The first pipeline does **not initially ask what the sentence means**.

It asks something closer to:

> Does this sentence contain one of my causal linguistic patterns?

Your notebook contains patterns such as:

```text
lead to
result in
cause
contribute to
increase
reduce
prevent
enable
support
require
depend on
risk
improve
...
```

including French equivalents.

---

## Step 2 — P1 passes

Consider:

> **Teacher training can reduce inappropriate use of generative AI.**

The rule finds:

```text
reduce
```

So:

```text
Teacher training
       ↓
reduces_or_prevents
       ↓
inappropriate use of generative AI
```

Good.

P1 becomes a causal claim.

---

## Step 3 — P2 probably disappears

Now:

> **Schools should publish clear guidance for AI-assisted assessment.**

There isn't an explicit causal cue such as:

```text
causes
reduces
leads to
enables
requires
...
```

The sentence is clearly important from a policy perspective.

But it isn't written as:

> Clear guidance **reduces** assessment problems.

or:

> Clear guidance **enables** responsible AI assessment.

Therefore the causal extractor may return:

```text
No causal relation found
```

and P2 does not become part of the causal-claim comparison.

This is important.

---

## Step 4 — S1 probably disappears too

> **Teachers are reluctant to use AI in assessment when school guidance is unclear.**

A human immediately understands something like:

```text
unclear guidance
        ↕
reluctance to use AI
```

But your patterns do not generally treat:

```text
when
```

as one of the causal relation operators.

So again:

```text
No extracted causal claim
```

The semantic information exists in the original sentence, but the causal pipeline may never pass it to the semantic comparison stage.

---

## Step 5 — S2 probably disappears

> **Many teachers say they have received little practical training in generative AI.**

This is highly relevant to P1.

P1 says:

```text
training is useful/important
```

S2 says:

```text
teachers report insufficient training
```

But S2 contains no explicit:

```text
causes
reduces
leads to
enables
...
```

So it may not become a causal claim either.

---

# 4. What is left?

Potentially only:

```text
P1:
Teacher training
    --reduces_or_prevents-->
inappropriate AI use
```

So instead of comparing all four meaningful sentences, Pipeline 1 could effectively be comparing:

```text
P1
```

against whatever causal sentiment claims happened to survive elsewhere in the corpus.

Then Sentence-BERT finds its top three nearest neighbours.

Suppose their similarities were illustratively:

```text
0.72
0.67
0.61
```

Then:

[
\text{mean similarity} =
\frac{0.72+0.67+0.61}{3}
=0.667
]

and therefore:

[
\text{coverage deficit}=1-0.667=0.333
]

Pipeline 1 tells you:

> **This policy causal claim has approximately 0.333 semantic coverage deficit against sentiment causal claims.**

Useful.

But it doesn't naturally tell you:

> Teachers actually share the policy's emphasis on training, but report that practical training is insufficient.

That requires a more interpretive comparison.

---

# 5. Now give exactly the same four sentences to Pipeline 2

This is where the difference becomes obvious.

The agentic notebook does **not require P1/P2/S1/S2 to contain causal keywords**.

All four clean sentences can be evidence.

The agent receives something conceptually like:

```text
POLICY EVIDENCE

P1: Teacher training can reduce inappropriate use...
P2: Schools should publish clear guidance...

SENTIMENT EVIDENCE

S1: Teachers are reluctant ... when guidance is unclear.
S2: Many teachers ... received little practical training...
```

Now the task isn't:

> Find `reduce`, `cause`, `enable`, etc.

It is:

> Compare the meaning represented by the policy evidence with the meaning represented by the sentiment evidence.

---

# 6. Observable decision trace of the agent

Without relying on a keyword rule, it can identify that:

```text
P1 → training is an important policy mechanism
S2 → teachers report insufficient training
```

These are semantically related even though S2 contains no causal cue.

And:

```text
P2 → policy calls for clear assessment guidance
S1 → teachers report difficulty where guidance is unclear
```

Again, the wording is different, but the concepts correspond.

So the agent could produce something like:

```text
classification:
partial_alignment

gap_label:
Teacher training and practical guidance

policy evidence:
P1, P2

sentiment evidence:
S1, S2

explanation:
Policy emphasises teacher training and clear guidance,
while sentiment evidence expresses corresponding needs
but indicates that practical training and guidance may
remain insufficient.
```

Notice how much richer that conclusion is than:

```text
coverage deficit = 0.333
```

---

# 7. But the agent isn't allowed simply to invent this

This is another major difference in your second notebook.

There is a **second DeepSeek pass**.

The verifier gets the evidence in a reordered form and checks:

```text
Did the finding cite real evidence IDs?

Does the policy evidence actually support it?

Does the sentiment evidence actually support it?

Was counterevidence ignored?

Is the classification justified?

Is the explanation faithful?

Is it incorrectly assuming that absence
from this small batch means absence from
the whole corpus?
```

Then it returns:

```text
accept
revise
or
reject
```

Your Python code subsequently performs additional deterministic checks.

For a substantive finding such as `policy_gap`, `sentiment_gap`, or `partial_alignment`, it requires evidence from **both corpora**.

Then you require confidence, evidence faithfulness, repeated runs, and stability before retaining it.

So the architecture is really:

```text
LLM reasoning
      ↓
LLM critic
      ↓
deterministic validation
      ↓
repeatability test
      ↓
human review
```

That is much more than simply asking an LLM a question.

---

# 8. A second example shows why this matters even more

Consider these two sentences:

### Policy

> Teacher training reduces inappropriate AI use.

### Sentiment

> Lack of teacher training increases inappropriate AI use.

A simple lexical comparison sees:

```text
teacher training
inappropriate AI use
```

in both.

The rule-based extractor sees approximately:

```text
POLICY:
training
   --reduces-->
misuse

SENTIMENT:
lack of training
   --increases-->
misuse
```

And Sentence-BERT will probably regard them as semantically close.

But what does that similarity mean?

They are not contradictory.

They actually express **compatible mechanisms**:

```text
more training → less misuse

lack of training → more misuse
```

An embedding similarity score doesn't explicitly establish that logical relationship.

An agent can interpret the polarity and say:

> These are aligned rather than contradictory.

That is another thing the agentic layer can contribute.

---

# 9. There is also a concrete weakness visible in your first notebook

This is quite revealing.

One of the strongest coverage gaps produced by Pipeline 1 was:

> “Fideliz Apilado, Laicia Gagnier, ... also **supported the production of the publication**.”

It received a coverage deficit of about **0.761**.

Why did it enter a causal analysis?

Because:

```text
supported
```

is one of the linguistic cues associated with:

```text
enables_or_supports
```

Syntactically, the rule fires.

But semantically, this is an **acknowledgement about people supporting production of a publication**, not a substantive AI-education causal claim.

That example illustrates the distinction beautifully:

```text
Rule system:
"I recognise the linguistic construction 'X supported Y'."

Agentic semantic system:
"Yes, but is this actually evidence of a meaningful
policy–sentiment issue?"
```

The rule is looking primarily at **form**.

The agent is evaluating **task-level meaning**.

---

# 10. So how does agentic improve causal NLP?

I would not say:

> “Agentic replaces the causal NLP pipeline.”

That would actually be scientifically inaccurate given these notebooks.

Your agentic prompt explicitly says:

> **Do not infer true real-world causality.**

So Pipeline 2 is not a better causal-inference engine.

It is better viewed as a **semantic reasoning and validation layer** around the causal NLP analysis.

The improvement is:

| Problem in causal pipeline                                   | What agentic reasoning can add                                       |
| ------------------------------------------------------------ | -------------------------------------------------------------------- |
| Requires predefined causal cues                              | Can understand relevant statements without those exact cues          |
| Explicit causality only                                      | Can capture implicit semantic relationships                          |
| One sentence → first valid causal relation                   | Can reason across several pieces of evidence                         |
| Nearest-neighbour similarity is just a number                | Can explain *why* two corpora align or differ                        |
| Similar vocabulary may hide contradiction                    | Can interpret negation, polarity and framing                         |
| Unrelated use of “support”, “reduce”, etc. may trigger rules | Can judge task-level relevance                                       |
| Gap = large semantic distance                                | Gap becomes `policy_gap`, `sentiment_gap`, `partial_alignment`, etc. |
| Little treatment of counterevidence                          | Agent explicitly considers counterevidence                           |
| Deterministic output but limited interpretation              | Agent + verifier + repeated runs test semantic robustness            |

---

# 11. The most important conceptual distinction

I think this is the sentence that makes the two finally separate:

### Pipeline 1 asks:

> **“For every causal claim I was able to recognize, how well can I find a semantically similar causal claim in the other corpus?”**

### Pipeline 2 asks:

> **“Looking at policy and sentiment evidence together, what substantive alignment or gap can actually be justified by the text?”**

Those are **not the same research question**.

Pipeline 1 is primarily a **measurement pipeline**.

Pipeline 2 is primarily an **interpretation + verification pipeline**.

---

# 12. And I would actually combine them slightly differently

If Mariem's objective is to show that the agentic approach **improves the rule-based causal NLP analysis**, I wouldn't make Pipeline 2 completely independent forever.

I would eventually use:

```text
                    ALL CLEAN SENTENCES
                           │
              ┌────────────┴────────────┐
              ↓                         ↓
     Rule-based causal NLP       Semantic retrieval
              ↓                         ↓
   explicit causal claims      implicit/relevant evidence
              └────────────┬────────────┘
                           ↓
                    AGENTIC ANALYST
                           ↓
          alignment / contradiction / gap
                           ↓
                    AGENTIC VERIFIER
                           ↓
               deterministic validation
                           ↓
                     human review
```

That gives you the best argument scientifically.

The causal pipeline supplies **traceability, exhaustive deterministic scanning and explicit causal structure**.

The agentic layer supplies **semantic recall, interpretation, counterevidence handling and explanation**.

And the verifier prevents the agent from becoming a free-form replacement for the deterministic method.

### In one sentence

**The rule-based pipeline tells you *where the causal-language coverage appears weak*; the agentic layer can tell you *whether that apparent weakness is a genuine semantic policy–sentiment gap, what kind of gap it is, and which evidence actually supports that conclusion*.**

That, to me, is the clearest way to explain why the second approach adds something genuinely new rather than just doing the same calculation with an LLM.
