# Great Data Analysis

*The habits of careful analysts, re-versioned for the agentic era.*

In 2019, Patrick Riley published Good Data Analysis, a guide with the habits of Google's best analysts. I come back to it often because almost all of it still applies. What changed is who does some pieces of the work.

In 2026, an agent writes the SQL, runs it, builds the chart, and hands you a conclusion in seconds. Analysis is now almost free to produce, but getting it right costs the same as before. Wrong answers arrive faster, and they look good. This makes Riley's guide more relevant, not less: when an agent does the work, what is left for the analyst is exactly what the guide was about – validation, skepticism, and judgment.

This is a re-version. I kept the core, cut it down, and added a fourth section highly relevant today: how to hand analysis to agents without losing control.

- **[Technical](#technical)** – how to examine data
- **[Process](#process)** – how to run an analysis
- **[Mindset](#mindset)** – how to be right more often
- **[Agents](#agents)** – how to delegate without losing control

## Technical

### Look at distributions, not summaries

A mean or a median hides the interesting parts: two populations mixed together, heavy tails, strange clusters. Plot the histogram or the CDF before you report an average. A "4-minute average session" changes meaning when you see it is two humps: humans around 40 seconds and a bot farm around 30 minutes.

```
 sessions
    │
    │   █
    │  ███
    │  ███                                  ██
    │ █████                                ████
    │ █████                                ████
    │███████▄▄                          ▄▄██████▄▄
    └──────────────────────────────────────────────▶ duration
     0s  40s                               30m
       humans                            bot farm

     mean: 4 minutes. nobody is at 4 minutes.
```

### Look at the outliers

Outliers often point to a problem in the analysis itself. A page with impossible click-through is usually double-counting. A page with zero clicks is usually a broken tag. You can exclude outliers or group them as "unusual", but first understand why they are there. Some you will never explain – put a time limit on the hunt.

### Noise does not average itself away

"We have so much data, the noise cancels out" is not true. Every number you publish needs some measure of confidence: an interval, a p-value, or at least the day-to-day variation of the metric.

### Look at raw examples

You cannot trust analysis code – yours or an agent's – until you have seen real rows go through it. Summaries hide details; single examples keep you honest. Sample with intention: a few from every class if you classify, the extremes and the middle if you measure.

### Slice

Split the data by device, channel, country, browser, day. If the effect can differ between groups, slicing is how you find out. If it should not differ, consistency across slices is a cheap check that you measure the right thing. When you compare two groups, watch for mix shifts: if the groups have different slice weights, Simpson's paradox can flip your conclusion.

```
           desktop   mobile   overall
 before      2.0%      1.0%      1.8%    (mix 80/20)
 after       2.2%      1.2%      1.5%    (mix 30/70)
              ↑         ↑         ↓

     every slice improved. the mix moved.
```

### Ask if it matters, not only if it is significant

With enough data, everything is statistically significant. The real question is whether a 0.1% difference changes any decision. The opposite trap also exists: with little data, "not significant" does not mean "no effect". Ask how big an effect could still hide inside your confidence interval.

```
                  0 = no effect
                  │
 A                ●                 +0.1%  "significant", too small to matter
 B         ├──────┼───●──────────┤  +4%    "not significant", could be large
                  │
      −10%        0       +10%      +20%

 ● = estimate   ├──┤ = 95% confidence interval
```

### Check consistency over time

Systems drift. Tracking that was verified at launch breaks quietly in month three, and nobody checks again. Looking at the data day by day catches this, and it shows you the natural variation of the metric. When one day looks strange, do not delete it – first find out why.

```
 events
   │ ▄▆▅▇▆▅▆▇▅▆▇▆▅▆
   │ ██████████████
   │ ██████████████ ▂▃▂▂▃▂▃▂▂▃▂▂  ← the tag broke. nobody was looking.
   └──────────────────────────────▶ days
     launch: verified   month three: unchecked
```

### Count what you filter

Almost every analysis starts with exclusions: internal traffic, bots, spam, users out of scope. Say what you filter and count what each filter removes. The cleanest way is to compute your metrics for the excluded population too. In my traffic reporting, the spam share is a headline number, not a hidden WHERE clause.

```
                                   % of raw
 raw pageviews          1,000,000      100%
   – internal traffic      12,400      1.2%
   – known bots           214,000     21.4%
   – spam rule             97,300      9.7%
 reported                 676,300     67.6%

 every minus is a decision. count them all.
```

### Define your ratios

The important choices hide in the denominator. "Sessions per user": users with a session, users seen this month, or all registered accounts? Conditional metrics need the same care: "time to click" really means "time to click, when there was a click", and that condition can differ between the groups you compare.

```
 "sessions per user"

    sessions / users with a session      3.1
    sessions / users active this month   1.9
    sessions / all registered accounts   0.4

 same name, three answers.
```

## Process

### Separate validation, description, and evaluation

Three stages, each with more room for debate:

1. **Validation** – is the data collected correctly, and does it mean what I think it means?
2. **Description** – what does it say? ("Sessions from paid social fell 12% week over week.")
3. **Evaluation** – so what? Is this good or bad, and for whom?

Description is where people can agree; evaluation is where they argue. If you mix description and evaluation, you will read the data as support for the conclusion you already had. You will jump between stages while you work – just always know which one you are in.

### Understand how the data was collected before reading it

If it comes from an experiment, read the configuration and try the feature yourself. If it comes from new tracking, learn how the events fire. Check the calendar for holidays and launches. My standing example: GA4's BigQuery export closes about two days late, so "yesterday" in the warehouse is not the same "yesterday" as in the UI.

### Check what should not have changed

Before you answer your question, rule out changes you did not expect: user counts, error rates, segments the change should not touch. If those moved, your experiment (or your pipeline) has a bigger problem than your hypothesis.

### Standard metrics first, custom second

New features come with tempting new metrics. Look at the boring ones first – sessions, clicks, revenue – even if you expect no change there. Standard metrics have years of scrutiny behind them; your custom metric is new and unproven. When they disagree, the custom metric is usually the wrong one.

### Measure twice, differently

For anything new, compute the same number by two routes, ideally from two data sources. If they agree, that does not prove you are right. But when they disagree, you almost always find a bug: in logging, in filters, or in your understanding.

```
 route A: BigQuery export ──▶ 4.2M ┐
                                   ├── Δ 9%. the bug lives here.
 route B: GA4 Data API    ──▶ 4.6M ┘
```

### Check for reproducibility

A real effect shows up across populations, across time, and across random subsamples. A model that breaks with small changes in the data has not captured anything real about the process behind it.

### Compare against what was measured before

If past analyses say mean page load is 2 seconds and you get 5, you may be right – but assume you are wrong until you can prove it. You do not need an exact match with history, just roughly the same range. Most surprising numbers turn out to be errors, not discoveries.

### Point new metrics at old truths first

A new metric earns trust by confirming what you already know: your best features should score well, your known failures should score badly. Only after that can it tell you something new. If it never matched a known result, do not trust it with an unknown one.

### Make hypotheses, then look for evidence against them

Analysis is iterative: you see an anomaly, and a theory suggests itself. The theory is not the finding. Ask what else must be true if the theory is right, then check. A learning effect should be strongest for heavy users. A launch effect should touch only the launched population, at the expected size. Good analysis tells a story – so tell it to yourself first, then try to break it.

### Iterate end-to-end

Get a rough answer through the whole pipeline before you perfect any single stage. The view from the end changes what you want the beginning to do. Note the shortcuts you took – filters skipped, strange rows ignored – instead of fixing everything up front. A full first pass now costs minutes, so there is no excuse for a week polishing stage one.

### Watch for metrics fed back into the system

If clicks feed the ranking system, more clicks cannot prove users are happier: the system was told to produce clicks. Never judge a change by a metric the change manipulates. Be careful even slicing on fed-back variables – the mix shifts become impossible to reason about.

```
       ┌──────────────────┐
       ▼                  │
    ranking ──▶ clicks ───┘

    clicks trained the ranking.
    clicks cannot judge it.
```

## Mindset

### Start with questions, not data or tools

There is always a reason someone wants an analysis. Turn it into a question before touching data. Analysis without a question goes nowhere, and this failure got cheaper: an agent will happily produce endless exploration with no direction. The old version of the trap still exists too – a favorite technique looking for problems it fits.

### Be believer and skeptic at once

When you find something interesting, ask yourself two things: what other evidence would show this is real, and what would prove it wrong? The skeptic side matters most when the person who asked wants a specific answer.

### Correlation still is not causation

With enough metrics and enough experiments, some signals align by chance. Before you claim "A causes B", or even "A is a good proxy for B", ask how you would validate it, and whether a hidden C drives both. Be clear with your audience about which claims you can make and which you cannot.

```
        C (unseen)
       ╱ ╲
      ▼   ▼
      A   B

  A moves with B. neither moves the other.
```

### Peers first, stakeholders second

Show your analysis to another analyst before you show it to the person who asked for it. The stakeholder wants a specific answer; a peer only wants the analysis to be correct. Early in the work, a peer points you to traps and past work on the topic. At the end, a peer spots the strange things you stopped seeing. An agent review is a useful filter before you take a peer's time, but it is not a replacement: the peer knows context that nobody wrote down.

### Say "I don't know" early, and own mistakes fast

Admitting the limits of what you know feels like weakness, but it builds credibility over time. Finding your own error and reporting it before someone else does is one of the few reliable ways an analyst earns trust.

## Agents

The original guide assumed that doing the analysis was the expensive part. That is no longer true. This section is what I learned from running analysis through agents every day. Anthropic groups these skills into four and calls it [AI fluency](https://www.anthropic.com/ai-fluency): delegation, description, discernment, and diligence. The items below are the analyst's version of those four.

### Plausible is the default output

A language model is good at producing what an answer should look like. For prose, that is often enough. For analysis, it is the failure mode. An agent's number arrives with the same confident format whether it is right or wrong. Calibrate for that: fluency is not evidence. Anthropic automated 95% of its internal analytics queries and still calls silent failures – wrong answers that nobody questions – the hardest open problem.

```
 a right answer:  "Sessions fell 12%, driven by paid social."
 a wrong answer:  "Sessions fell 12%, driven by paid social."

 they look identical. that's the problem.
```

### Correctness lives in the context

Most agent errors are not SQL bugs; they are meaning bugs. The agent did not know that a flag arrives as a string, that the export lags two days, that the source table mixes real campaign tags with synthetic values. It cannot know what nobody told it. Document your schema's meanings, definitions, and traps once, give that to every agent, and every future analysis inherits the fix. Undocumented meaning is the biggest source of confident wrong answers. This is measurable: when Anthropic gave its internal analytics agent documented context, accuracy went from 21% to 95%, while raw access to thousands of past queries moved it by less than one point. And documentation is not write-once: one month without maintenance and their accuracy fell to 65%.

### Ask for the work, not just the answer

Ask for three things with every result: the exact query that ran, row counts through each filter step, and a few raw examples. This is the old advice – count your filtering, look at examples – turned into a rule for delegation. An answer that cannot show its work is just a claim.

### Get two answers by two routes

"Measure twice" used to be expensive; now a second independent computation costs one sentence. Fresh agent, no shared context, ideally a different source or method. When the numbers agree, you learned a little. When they disagree, you probably caught a bug before publishing it.

### Never let the agent check its own work

An agent that reviews its own analysis carries the same assumptions and will approve them. Verification must be independent: at minimum a fresh context, better a different route, best a human who reads the work. Self-review catches typos, not wrong assumptions. Anthropic runs an adversarial agent against its analytics answers: about a third more tokens for six more points of accuracy.

### Spend the saved time on validation

When analysis gets ten times cheaper, the number of analyses grows on its own: once agents answer directly, everyone asks. Your extra time should not go there. The scarce thing was never the number of analyses; it was the correct ones. Spend the saved time on the checks in this guide. At scale, build the checks into the system: one agreed definition per metric, tests that run on every change, answers that state their source.

### The question and the so-what stay yours

Agents take over the middle of the job: you give a question, they return a description. The two ends stay with you. Choosing what is worth asking requires knowing the business. Deciding what the answer means requires owning the consequences. Riley's three stages map onto this cleanly: validation you enforce, description you delegate, evaluation you keep.

```
 the question ──▶ [ the analysis ] ──▶ the so-what
     yours           the agent's           yours
```

### You can't credibly orchestrate what you can't do yourself

Everything in this section assumes a reviewer who could, in principle, do the work themselves. You can only spot the meaning bug if you know the schema. You can only judge the filters if you have written filters. You can only tell plausible from true if you learned the difference the slow way. This is why the first three sections still matter: the skills you no longer use daily are the qualification for supervising the agent that does. An analyst who cannot do the analysis cannot check it.

## Closing

Riley ended with this: careful work is invisible. Nobody who makes decisions from your analysis sees that you checked population sizes or validated the effect across browsers. In 2026 it goes further: even the analysis is invisible, produced in seconds by a machine. The only visible thing left is whether you were right. When anyone can generate an analysis by asking for one, being right is the whole job.

## Attribution

Adapted from [Good Data Analysis](https://developers.google.com/machine-learning/guides/good-data-analysis) by Patrick Riley (Google Machine Learning Guides, last major update June 2019), licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). This version is rewritten, shorter, moved to web analytics, and extended with the Agents section. Same license.

The numbers in the Agents section come from [How Anthropic enables self-service data analytics with Claude](https://claude.com/resources/articles/how-anthropic-enables-self-service-data-analytics-with-claude): the same habits at company scale – 95% of queries automated, with accuracy driven by documented context, adversarial review, and humans who maintain both.
