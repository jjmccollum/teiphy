---
title: 'teiphy: A Python Package for Cconverting TEI XML Collations to NEXUS and Other Formats'
tags:
  - Python
  - phylogenetics
  - text encoding
  - TEI
  - NEXUS
authors:
  - name: Joey McCollum
    orcid: 0000-0002-5647-0365
    affiliation: 1
  - name: Robert Turnbull
    orcid: 0000-0003-1274-6750
    affiliation: 2
affiliations:
 - name: Institute for Religion and Critical Inquiry, Australian Catholic University, Australia
   index: 1
 - name: Melbourne Data Analytics Platform, University of Melboune, Australia
   index: 2
date: 3 September 2022
bibliography: docs/references.bib
---

# Summary

Textual scholars have been using phylogenetics to analyze manuscript traditions since the early 1990s [@roh_report_1992].
Many standard phylogenetic software packages accept as input the NEXUS file format [@msm_nexus_1997]. 
The `teiphy` program takes a collation of texts encoded using the Text Encoding Initiative (TEI) guidelines and converts it to a NEXUS format
so that it can be used for phylogenetic analysis.
The package can also convert to other formats such as Stephen C. Carlson's [`STEMMA`](https://github.com/stemmatic/stemma) format or to a NumPy array [@numpy_2020].

# Statement of Need

The TEI aims to provide an international standard for digital encoding textual information for the humanities [@ism_tei_1995]. 
The TEI guidelines describe an XML format for encoding a critical apparatus [@tei_critical_apparatus].
Due to its rich and well-documented set of elements for expressing a wide range of features in manuscript transcriptions, collations, and critical editions,
TEI XML has become the _de facto_ format for textual data in the digital humanities [@fischer_representing_2020]. 
Its expressive power has proven increasingly valuable since its release, as scholars have learned—sometimes the hard way—that digital transcriptions and collations should

1. preserve as much detail as they can from their material sources, including paratextual features; 
2. reproduce the text of their sources as closely as possible, with editorial regularizations to things like orthography, accentuation, and scribal shorthand encoded alongside rather than in place of the source text; and
3. describe uncertainties about what a source read as accurately as possible, allowing for degrees of uncertainty and multiple choices for disambiguations if necessary.

Such principles have much bearing on the editing of critical texts, a task fundamental to both digital humanities and classical philology.
Within the digital humanities, phylogenetic algorithms have been popular approaches to this task.
Taking the most arduous part of reconstructing a textual tradition and delegating it to a computer proved to be a promising technique, and its successful demonstration with a portion of _The Canterbury Tales_ was a milestone in the development of the field [@bhbr_phylogeny_1998].
Soon after this, the same methods were applied more comprehensively to the tradition of _Lanseloet van Denemerken_ in a work that would formalize many practical rules for computer-assisted textual criticism [@salemans_building_2000].
Since then, phylogenetic methods have quickly evolved [@felsenstein_inferring_2004], and textual critics have adapted the improvements and even added their own innovations to make the process more suitable for their purposes [@swh_vorlage_2002; @swh_pathways_2004; @carlson_text_2015; @edmondson_analysis_2019; @turnbull_history_2020; @hyytiainen_acts_2021].

As their name might suggest, phylogenetic methods originated in the setting of evolutionary biology.
They have a natural place in textual criticism given the deep analogy between the two fields: a sequence alignment, which consists of taxa, sites or characters, and the states of taxa at those characters, corresponds almost identically to a collation, which consists of witnesses to the text, locations of textual variation (which we will call “variation units” from here on), and the variant readings attested by witnesses at those points.

Most phylogenetic software, however, expects inputs not in TEI XML format, but in NEXUS format [@msm_nexus_1997].
This format was conceived with versatility in mind, and this design choice has been vindicated in its applicability with textual data, but NEXUS is not equipped or meant to express the same kinds of details that TEI XML is.
Conversely, for those interested primarily in working with the collation as an alignment, TEI XML is overkill.
Thus, a great chasm has been fixed between the two formats, and the only way to cross over it is by conversion.

The problem is compounded by the fact that other tools for phylogenetic and other analyses anticipate input formats other than NEXUS.
A noteworthy alternative is Hennig86, which is the format of choice for the TNT phylogenetic software [@farris_hennig86_1988; @gc_tnt_2016].
While this format does not allow for as much flexibility in the input as NEXUS does (e.g., it does not support ambiguities that can be disambiguated as some states and not others), TNT's remarkable performance in tree search makes support for this format a desirable option on practical grounds.

Another format of value for text-critical phylogenetics is the input format associated with the [`STEMMA` software](https://github.com/stemmatic/stemma) developed by Stephen C. Carlson for his phylogenetic analysis of the Epistle to the Galatians [@carlson_text_2015].
Carlson's software expands on traditional maximum parsimony-based phylogenetic algorithms with rules to account for contamination or mixture in the manuscript tradition.
While it has so far only been applied to books of the New Testament, it is just as applicable to other traditions, and a way of converting TEI XML collations of other texts to a format that can be used by this software could help bridge this gap.

Other basic machine-learning approaches to textual criticism, which are frequently based on clustering and biclustering algorithms [@thorpe_multivariate2002; @finney_discover_2018; @mccollum_biclustering_2019], expect the collation data to be encoded as a matrix with a row for each variant reading and a column for each witness.
Thus, a means of converting the essential data from TEI XML collation to a NumPy array [@numpy_2020] and other related formats is a need for applications like these.

# Design

While the conversion process is a straightforward one for most collation data, lacunae, retroversions, and other sources of ambiguity occasionally make a one-to-one mapping of witnesses to readings impossible, and in some cases, one disambiguation may be more likely than another in a quantifiable way.
Mechanisms for accommodating such situations exist in both TEI XML and NEXUS, and for likelihood-based phylogenetic methods, “soft decisions” about the states at the leaves and even the root of the tree can provide useful information to the inference process.
For these reasons, we wanted to ensure that these types of judgments, as well as other rich features from TEI XML, could be respected (and, where, necessary, preserved) in the conversion process.

Collations should preserve as much detail as possible, including information on how certain types of data can be normalized and collapsed for analysis. Since one might want to conduct the same analysis at different levels of granularity, the underlying collation data should be available for use in any case, and only the output should reflect changes in the desired level of detail.
Likewise, as noted in the previous section, uncertainty about witnesses' attestations should be encoded in the collation and preserved in the conversion of the collation.

For text-critical purposes, differences in granularity typically concern which types of variant readings we consider important for analysis.
At the lowest level, readings with uncertain or reconstructed portions are almost always considered identical with their reconstructions (provided these reconstructions can be made unambiguously) for the purpose of analysis.
Defective forms that are obvious misspellings of a more substantive reading are often treated the same way.
Even orthographic subvariants that reflect equally “correct” regional spelling practices may be considered too common and of too trivial a nature to be of value for analysis.
Other readings that do not fall under these rubrics but are nevertheless considered manifestly secondary (due to late and/or isolated attestion, for instance), may also be considered uninformative “noise” that is better left filtered out.

# Use Case

Due to the availability of extensive collation data for the Greek New Testament, and because this project was originally developed for use with such data, we tested this library on a collation of the book of Ephesians in over 200 textual witnesses (including manuscripts, correctors' hands, translations to other languages, and quotations from church fathers).
The manuscript transcriptions used for this collation were those produced by the University of Birmingham's Institute for Textual Scholarship and Electronic Editing (ITSEE) for the International Greek New Testament Project (IGNTP); they are freely accessible at [https://itseeweb.cal.bham.ac.uk/epistulae/XML/igntp.xml](https://itseeweb.cal.bham.ac.uk/epistulae/XML/igntp.xml).
To achieve a balance between variety and conciseness, we restricted the collation to a set of forty-two variation units in Ephesians corresponding to variation units in the United Bible Societies Greek New Testament [@ubs5], which highlights variation units that affect substantive matters of translation.
As a result, this collation is by no means complete, and some witnesses are lacunose for the entirety of the collation.
Still, it is complete enough to serve as a sufficient example of the types of details outlined in previous sections.

In our example collation, witnesses are described in the `listWit` element under the `teiHeader`.
Because most New Testament witnesses are identified by numerical Gregory-Aland identifiers, these witnesses are identified with `@n` attributes; the recommended practice is to identify such elements by `@xml:id` attributes, but this software is designed to work with either identifying attribute (preferring `@xml:id` if both are provided), and we have left things as they are to demonstrate this feature. 

Each variation unit is encoded as an `app` element with a unique `@xml:id` attribute.
Within a variation unit, a `lem` element without a `@wit` attribute presents the main text, and it is followed by `rdg` elements that describe variant readings (with the first `rdg` duplicating the `lem` reading and detailing its witnesses) and their attestations among the witnesses.
(Situations where the `lem` reading is not duplicated by the first `rdg` element, but has its own `@wit` attribute, are also supported.)
For conciseness, we use the `@n` attribute for each reading as a local identifier; the recommended practice for readings that will be referenced elsewhere is to use the `@xml:id` attribute, and this software will use this as the identifier if it is specified, but we have only specified `@xml:id` attributes for `rdg` elements referenced in other variation units to demonstrate the flexibility of the software.
For witnesses with missing or ambiguous readings at a given variation unit, we use the `witDetail` element.
For ambiguous readings, we specify their possible disambiguations with the `@target` attribute and express our degrees of certainty about these disambiguations using `certainty` elements under the `witDetail` element. 

The [TEI XML file](https://github.com/jjmccollum/teiphy/blob/main/example/ubs_ephesians.xml) for this example is available in the examples directory in the GitHub repository. Instructions for converting this file using ``teipy`` and analyzing it with several different phylogenetic packages are provided in the documentation. Functional tests where this example file is converted and run through IQ-TREE [@10.1093/molbev/msaa015], MrBayes [@10.1093/bioinformatics/btg180], and STEMMA [@@carlson_text_2015] are part of the continuous integration (CI) pipeline. An example of the tree inferred with IQ-TREE with support values from 1000 bootstrap replicates is shown in figure 1.

![A phylogenetic tree from the Ephesians example file created using IQ-TREE.](docs/img/iqtree.pdf)

# Availability

The software can be installed through the Python Package Index (PyPI), and the source code is available under the MIT license from the [GitHub repository](https://github.com/jjmccollum/teiphy). 
The automated testing suite has 100% coverage.

# Acknowledgements and Funding

The authors wish to thank Stephen C. Carlson for his feedback on this project. This work was supported by an Australian Government Research Training Program (RTP) Scholarship.

# References
