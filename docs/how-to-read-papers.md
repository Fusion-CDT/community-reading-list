---
comments: true
icon: "lucide/book-open"
---

# How to read papers

Nobody is really taught how to read a research paper; most of us pick it up by trial and error. A few habits make it quicker, and make it easier to judge how far to trust what you read. None of this is a set of rules. Take what's useful.

## Read in passes

You don't have to read a paper from start to finish in one go, and most papers don't deserve it. A common approach ([Keshav, 2007](https://doi.org/10.1145/1273445.1273458)) is to read in up to three passes, stopping whenever you have what you need:

1. **Skim (10 minutes):** the title, abstract, introduction, section headings, figures and conclusions. You should be able to describe roughly what the paper claims, what kind of paper it is (e.g. original research or a review; see below), and whether it's relevant to you.
2. **Read for the argument (an hour or so):** the main text, without getting stuck on every derivation or technical detail. Work out how the evidence supports the claims, and note the references you'll want to follow up.
3. **Work through it:** redo the key derivations, check the assumptions, and think about how you'd reproduce the results. This is only worth it for the few papers your own work builds on or meaningfully relates to.

For more on this approach, Adler and Van Doren's [_How to Read a Book_](https://www.waterstones.com/book/how-to-read-a-book/mortimer-j-adler/charles-van-doren/9780671212094) makes the same case at more length (for books rather than papers).

## Know what kind of paper it is

Different kinds of paper deserve different kinds of trust:

- **Original research** reports new results. It's peer reviewed, but review checks that a paper is plausible, not that it's right.
- **Reviews** summarise a field. They (and PhD theses) are usually the best place to start, but see [below](#reading-reviews).
- **Tutorials and lecture notes** aim to teach, so they simplify, and may not mention open questions.
- **Roadmaps and perspectives** argue for a direction or for funding. They're useful for seeing what a community thinks matters, but they're written to persuade.
- **Preprints** (e.g. on arXiv) haven't been peer reviewed yet. Check whether a published version exists, and whether it changed.

## Questions to ask as you read

- **What exactly is claimed?** Often less than the abstract suggests. Look for the hedges in the conclusions.
- **What's the evidence?** Experiment, simulation or theory, and is it enough to support the claim?
- **Where does it apply?** Every result has assumptions and a regime of validity: an ordering, a geometry, a parameter range, a particular machine or code. A result from one tokamak, or from linear simulations, may not carry over to another device or to nonlinear behaviour.
- **What's it compared against?** A new model that "agrees well with experiment" might only be compared on the cases where it works. Look for error bars, uncertainties and validation.
- **What would change the conclusion?** If you can think of an obvious alternative explanation, check whether the authors have ruled it out.

## Reading reviews

Reviews are written by people with views of their own, usually experts in one part of the field. That's what makes them valuable, but it also means they're selective:

- Authors often cite their own group's work more than others'. This isn't necessarily bias, as they know it best, but it shapes the picture you get.
- A review may present one side of an open question as settled, or leave out approaches the authors don't favour.
- Fields move on. Check the date, and look for more recent work citing the review.

It helps to read two reviews of the same topic from different groups (if they exist), and to follow important claims back to the original papers rather than relying on the review's summary of them.

## When you're stuck

- **Follow the references back.** Papers assume the background their community shares. An older review, a textbook chapter, or a tutorial on this site may fill the gap.
- **Ask.** Your supervisor, other students and journal clubs are good for "is this paper any good?" as well as "what does this mean?".
- **Keep notes.** A few lines on what a paper claims, how it supports it and what you doubt will save you re-reading it later. A reference manager such as [Zotero](https://www.zotero.org/) helps.

If a paper was worth the effort, consider [writing a note](https://github.com/Fusion-CDT/community-reading-list/blob/main/CONTRIBUTING.md) about it for this list, so the next person gets a head start.
