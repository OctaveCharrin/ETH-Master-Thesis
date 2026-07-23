# Rules for Academic Writing

This is a list of writing rules that are unknown to and therefore violated by many bachelor, master, and PhD students. This is *not* a comprehensive list of rules, just those that come up most frequently. Please refer to this list when receiving feedback by Adrian or one of the senior group members.

## 0. Resources

* [The Chicago Manual of Style](https://www.chicagomanualofstyle.org/home.html) (CMOS): 
  * basis for our conventions
  * many and very detailed rules
  * online access through ETH VPN
* [Writing for Computer Science](https://drive.google.com/file/d/10DvLRofhOCMS_rckJxkglMrJuQXxX93i/view): detailed book
* [The Elements of Style](http://www1.bartleby.com/141/): important basic rules for good writing
* [Group-meeting slides on typography and style](https://gitlab.inf.ethz.ch/OU-PERRIG/group-meeting-materials/blob/master/materials/Markus2019-Typography.pdf)
* [Group-meeting slides with general tips and tricks including style advice](https://gitlab.inf.ethz.ch/OU-PERRIG/group-meeting-materials/blob/master/materials/Laurent2019-tips-and-tricks.pdf)

## A. Content and Structure

 1. Replace an assumption by an observation. It's much easier to disagree with an assumption than with an observation!
 2. Always keep the reader informed on where in the paper they are, where the paper is heading toward, always make it clear what else is expected, what is still coming up.
 3. Make sure that any mechanism is concisely explained, so that results are repeatable.
 4. State the main result upfront, then back it up with the text. Poor writing is to explain things in a lot of text and the main point doesn't really jump out. For example, in poorly structured text the reader has to pay careful attention to assemble the train of thought as they are reading the section.
 5. Standard paper structure (not all are present in every paper and some may be combined):
    * Abstract
    * Introduction
    * Background (*if needed*)
    * Problem Definition
    * Attacker Model (*not needed in this paper*)
    * Assumptions (*sometimes combined with the previous two sections*)
    * Approach/System Design/...
    * Analysis (theoretical)
    * Evaluation (practical/experimental)
    * Discussion (*sometimes omitted*)
    * Related Work
    * Conclusion
    * Acknowledgments (*only in camera-ready version*)
 6. Abstract:
    * Briefly motivate problem domain, why is it an important domain?
    * What problem does the paper solve?
    * What is the main contribution? -> The abstract should convince a reader to read the paper, not necessary to explain anything, just provide an incentive to read
    * Keep the abstract short! Should be fewer than 15 lines.
 7. Introduction:
    * Motivate problem, show that it's an important and difficult problem 
      * Solve a very specific problem
    * Paint the research landscape, explain deficiency of current state of the art (without being rude), explain what aspect your research addresses. Explain how the current paper fits into the research landscape. What is the ultimate research goal in this area? How does the current paper help to get us closer towards that goal?
    * Explain what the main research challenge is, why is it a difficult and important problem? This is very important, if the audience agrees that the challenge is difficult (they don't know how to solve it) and important, the paper is almost already accepted. State interesting questions that the paper addresses.
    * Provide a very explicit, verifiable claim for a metric for approach (we propose system X with property Y; Y must be easy to measure and clear to see merit w.r.t. related work). If one can show that we made verifiable progress on a relevant problem, then the paper cannot be rejected :-)
    * Explain KEY CONCEPTS / INSIGHTS that the paper introduces
    * Pose a list of QUESTIONS! Readers love puzzles, and ideally, the paper contains several questions that the reader will try to answer but can't, then once the answer is in the paper the reader says: great!
    * List of CONTRIBUTIONS
 8. Problem Definition:
    * Clear and concise problem formulation
    * Present specific quality metric for evaluation
 9. Approach/System Design/...:
    * Repeatable, specific description
    * Provide intuition, key idea
    * State what the problem is that you want to address in that section
    * Describe all parts of life cycle: setup, run, maintenance, etc.
    * Explain with an example (together with the intuition and description, the scheme should have been explained 3 times from different perspectives)
    * Did we really fully explore the design space? 
      * Why are simpler solutions inappropriate?
      * Explore design alternatives!
      * Provide intuition on why certain design choices were taken, why alternatives were rejected
      * Describe a "strawman" approach, show why it's inadequate
10. Analysis:
    * Overhead (computation and communication)
    * Practicality
    * Security analysis
11. Evaluation:
    * Compare with related work!
    * Deployment issues (legacy issues?)
12. Related Work:
    * Analyze research landscape, how does the work fit in?
    * Present work that others may think to be related and explain why it isn't related
13. Conclusion:
    * What have you learnt from the research?
    * What are surprising findings from the work?
    * What future work is possible?
    * Some additional insights.
    * *The conclusion should be very different from the abstract!*
14. Discussion:
    * It should describe wider meaning, importance, and relevance of the paper and implications for the wider ecosystem.
    * Provide a more high-level interpretation of the evaluation results.
    * How does your paper relate to the related work?
    * Are there deployment or other practical issues and how are they overcome?

## B. Language and Phrasing

 1. Choose either American (default) or British English and use it consistently.
    * Only use British English with a good reason (e.g., British website or journal).
 2. Use phrases such as "we find that", "we discovered that".
 3. Use *because* often, people seem to believe whatever comes thereafter.
 4. Be careful with the terms *correct*, *optimal*, or *proof*! People have varying opinions of correctness, so it's likely that someone misunderstands it. Especially theory people are very particular about this term.
 5. Avoid ["weasel" words](https://en.wikipedia.org/wiki/Weasel_word), as they make the writing ambiguous / non-specific.
 6. It's best to avoid general / fuzzy verbs with a multitude of meanings, such as *get*, *have*, *be*, *do*, *like*, *give*, *come*, *make*. More specific verbs exist with a more precise meaning.
 7. Replace the word "very" whenever possible; there are several lists available online, for example [here](https://www.grammarcheck.net/very/) or [here](https://www.mentalfloss.com/article/82484/replace-word-very-one-these-128-modifiers).
 8. Do not use unnecessarily complicated words / phrases:
    * in order to -> to
    * utilize -> use
 9. The words *thus*, *therefore*, and *hence* have [different meanings](https://painintheenglish.com/case/4452/).
10. Keep sentences reasonably short. In a two-column layout, they should not be longer than 5 lines.
11. Avoid colloquial terms, use purely technical terminology. Examples to avoid: "let's", "has been around", "a cool concept", "a neat approach".
12. Avoid figurative speech that is incorrect if taken literally. Example "TLS is introduced on top of communication" (TLS is not "on top", but "utilized" or "based on"). Example "This paper introduces" (the paper cannot "introduce" anything, but "in this paper, we introduce", the authors can introduce something but an inanimate object like a paper cannot).
13. Avoid general / fuzzy verbs with a multitude of meanings: "go", "have", "do", "be", "get", "like", "give", "come", "make". More specific verbs usually exist with a more precise meaning.
14. Be careful with [albeit](https://www.grammarly.com/blog/albeit/), it *cannot* introduce independent clauses.

## C. Grammar and Style

 1. Always use the *Oxford comma*: in a list of more than two items, there should be a comma before the "and" or "or" [[CMOS 6.19](https://www.chicagomanualofstyle.org/book/ed17/part2/ch06/psec019.html)].
    * *Bad*: a, b and c; a, b or c.
    * *Good*: a, b, and c; a, b, or c.
 2. In general, introductory clauses should be offset with a comma (as in this sentence).
    * This applies in particular to if clauses.
 3. The words *notation*, *data*, *research*, *information* are always singular, never plural
    * "data" is sometimes used as purely plural word (plural of "datum"); however, then it should be used as such consistently.
 4. Proper nouns should be capitalized.
    * Rule of thumb: you can use it only with "the", not with "a".
    * Examples: *the* Internet, *the* Border Gateway Protocol, ...
    * Tip: check capitalization on Wikipedia.
 5. Only introduce new abbreviations when they are afterwards used at least 3-5 times. [[CMOS 10.3](https://www.chicagomanualofstyle.org/book/ed17/part2/ch10/psec003.html)]
 6. Introduce an abbreviation by stating its long form followed by the abbreviation in parentheses; for example, "a denial-of-service (DoS) attack". [[CMOS 10.3](https://www.chicagomanualofstyle.org/book/ed17/part2/ch10/psec003.html)]
    * Even when the abbreviation has capitalized letters, the full expression should only be capitalized when it is considered a proper noun (see above) [[CMOS 10.6](https://www.chicagomanualofstyle.org/book/ed17/part2/ch10/psec006.html)]
    * *Good*: "The Border Gateway Protocol (BGP) does not defend against denial-of-service (DoS) attacks."
    * After the first introduction of an abbreviation, use it consistently (instead of alternating between long form and abbreviation).
    * If you use the long form as a plural, also the acronym should have the plural form.
 7. Do not introduce abbreviations in the abstract unless you use them multiple times in the abstract itself.
 8. Expressions that are derived from names should be capitalized: Bloom filter, Boolean variable, Merkle tree.
 9. A *hyphen* (- in LaTeX) should generally be used in the following cases: [[CMOS 5.92](https://www.chicagomanualofstyle.org/book/ed17/part2/ch05/psec092.html), [CMOS 7.81](https://www.chicagomanualofstyle.org/book/ed17/part2/ch07/psec081.html)ff]
    * hyphenation (at a line break; this is done automatically);
    * some composed words (pre-image);
    * compound modifiers (also known as *phrasal adjectives*): multiple words that modify another word should be joined by a hyphen, such as "hash-based signature". 
      * Here, "hash based" modifies "signature" and therefore the two words need to be connected with a hyphen.
10. An *en dash* (-- in LaTeX) is used for ranges of numbers (5--7). [[CMOS 6.78](https://www.chicagomanualofstyle.org/book/ed17/part2/ch06/psec078.html)]
    * In British English and German it is also used (with a white space before and after) for a suspension in sentences -- such as here.
    * There are several other less common usages. [[CMOS 6.80](https://www.chicagomanualofstyle.org/book/ed17/part2/ch06/psec080.html)ff]
11. An *em dash* (--- in LaTeX) is used for creating a suspension in the sentence, but without a space---such as here. [[CMOS 6.85](https://www.chicagomanualofstyle.org/book/ed17/part2/ch06/psec085.html)ff]
12. Citations should be used such that a sentence is complete and correct without them.
    * *Bad*: The authors of [1] find that computers are great.
    * *Good*: Turing et al. find that computers are great [1].
13. If you use a colon to introduce a list, the previous sentence should be complete.
    * *Bad*: We build our system on: a, b, and c.
    * *Good*: We build our system on the following components: a, b, and c.
14. Capitalization after a colon: [[CMOS 6.63](https://www.chicagomanualofstyle.org/book/ed17/part2/ch06/psec063.html)]
    * If the colon introduces at least two full sentences, capitalize the first word.
    * If the colon introduces a single complete or an incomplete sentence, do not capitalize the first word (unless it should be capitalized anyway). 
      * (For a single sentence, capitalization is also allowed but not capitalizing lets you emphasize that only one sentence is introduced by the colon.)
15. Phrases such as "that is", "namely", "for example" in a sentence should be preceded by a comma, semicolon, em dash, or a parenthesis and followed by a comma; for example, as shown in this sentence. [[CMOS 6.51](https://www.chicagomanualofstyle.org/book/ed17/part2/ch06/psec051.html)]
    * This also applies to the corresponding abbreviations "i.e." (*id est*, "that is") and "e.g." (*exempli gratia*, "for example").
16. Footnote markers should be placed *after* other punctuation except dashes. [[CMOS 14.26](https://www.chicagomanualofstyle.org/book/ed17/part3/ch14/psec026.html)]
17. In titles, capitalize every word except articles (a, an, the, ...), coordinating conjunctions (and, but, or, for, nor), and prepositions (on, at, to, from, by, ...). [[CMOS 8.161](https://www.chicagomanualofstyle.org/book/ed17/part2/ch08/psec161.html)]
    * For hyphenated words, capitalize both words unless the first part is merely a prefix and cannot stand on its own; for example, "Path-Selection Mechanism" but "Inter-domain Routing".
18. A dependent clause should *not* be offset by a comma when it is essential/restrictive/defining. If it is nonessential/parenthetical/nonrestrictive, it must be offset by a comma. [[CMOS 6.25](https://www.chicagomanualofstyle.org/book/ed17/part2/ch06/psec025.html)]
    * The word *which* can be used for both; *that* should only be used with restrictive clauses and thus never be offset by a comma. [[CMOS 6.27](https://www.chicagomanualofstyle.org/book/ed17/part2/ch06/psec027.html)]
19. Words like "however" and "therefore" should be offset by commas and/or semicolons. [[CMOS 6.49]](https://www.chicagomanualofstyle.org/book/ed17/part2/ch06/psec049.html)

## D. Typography and LaTeX

1. In math mode, only variables should be italic, everything else should be upright (\\mathrm{}):
   * indices should be upright unless they refer to a variable;
   * functions should be upright;
   * mathematical constants should be upright.
2. If a variable consists of more than a single letter, wrap it in "\\mathit{}" as otherwise it is interpreted as a product of multiple letters with weird spacing
3. Units should be typeset in upright font and separated from values by a short space. The [siunitx](https://ctan.org/pkg/siunitx) package is very helpful.
4. Figures have their caption below, tables above. [[CMOS 3.54](https://www.chicagomanualofstyle.org/book/ed17/part1/ch03/psec054.html)]
5. Tables should ideally only use horizontal rules. This can be done easily using the [booktabs](https://ctan.org/pkg/booktabs) package. [[CMOS 3.53](https://www.chicagomanualofstyle.org/book/ed17/part1/ch03/psec053.html)]
6. Try to only use equation environments defined in the [amsmath](https://ctan.org/pkg/amsmath) package. Others (like *eqnarray*) can cause inconsistent spacing.
7. Make sure internal references are consistent. You can use the [cleveref](https://ctan.org/pkg/cleveref) package with its commands \\cref and \\Cref for that.
8. Make sure to correctly typeset [quotation marks](https://tex.stackexchange.com/questions/531/what-is-the-best-way-to-use-quotation-mark-glyphs).
9. Make sure your [parentheses in math mode are large enough](https://www.overleaf.com/learn/latex/Brackets_and_Parentheses).