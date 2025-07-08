==================
Advanced Usage
==================

Lacunae, retroversions, and other sources of ambiguity occasionally make a one-to-one mapping of witnesses to readings impossible, and in some cases, one disambiguation may be more likely than another in a quantifiable way.
Mechanisms for accommodating such situations exist in both TEI XML and NEXUS, and for likelihood-based phylogenetic methods, “soft decisions” about the states at the leaves and even the root of the tree can provide useful information to the inference process.
For these reasons, ``teiphy`` ensures that these types of judgments, as well as other rich features from TEI XML, can be respected (and, where, necessary, preserved) in the conversion process.

Collations should preserve as much detail as possible, including information on how certain types of data can be normalized and collapsed for analysis.
Since we may want to conduct the same analysis at different levels of granularity, the underlying collation data should be available for us to use in any case, and only the output should reflect changes in the desired level of detail.
Likewise, as noted in the previous section, uncertainty about witnesses' attestations should be encoded in the collation and preserved in the conversion of the collation.

Analysis at Varying Levels of Detail Using Reading Types
--------------------------------------------------------

For text-critical purposes, differences in granularity typically concern
which types of variant readings we consider important for analysis. At
the lowest level, readings with uncertain or reconstructed portions are
almost always considered identical with their reconstructions for the
purpose of analysis. Defective forms that are obvious misspellings of a
more substantive reading are often treated the same way. Even
orthographic subvariants that reflect equally “correct” regional
spelling practices may be considered too common and of too trivial a
nature to be of value for analysis. Other readings that do not fall
under these rubrics but are nevertheless considered manifestly secondary
(due to late and/or isolated attestion, for instance), may also be
considered uninformative “noise” that is better left filtered out.

In TEI XML, variant reading types are naturally encoded using ``@type``
attribute of the ``rdg`` or ``rdgGrp`` element. To support treating
different types of readings as substantive for the purposes of analysis,
a hierarchical ordering of reading types (e.g., ``subreading``
> ``orthographic`` > ``defective`` > ``reconstructed``) is assumed, so you can “roll
up” readings with types lower in the hierarchy into their “parent”
readings with types higher in the hierarchy. This can be done with a
flat list of ``rdg`` elements alone, as follows:

.. code:: xml

    <app xml:id="B10K2V5U20-24">
        <lem><w>χαριτι</w><w>εστε</w><w>σεσωσμενοι</w></lem>
        <rdg n="1" wit="UBS P46 01 03 06C2 18 33 35 88 424 606 915 1175 1505 1611 1739 1881 2495 syrh Jerome TheodoreOfMopsuestia"><w>χαριτι</w><w>εστε</w><w>σεσωσμενοι</w></rdg>
        <rdg n="1-f1" type="defective" cause="aural-confusion" wit=""><w>χαριτι</w><w>εσται</w><w>σεσωσμενοι</w></rdg>
        <rdg n="1-f1-v1" type="reconstructed" wit="02"><w>χαριτι</w><w>εσται</w><w>σ<unclear>ε</unclear><supplied reason="lacuna">σω</supplied>σμενοι</w></rdg>
        <rdg n="2" wit="Ambrosiaster MariusVictorinus Pelagius"><w>ου</w><w>χαριτι</w><w>εστε</w><w>σεσωσμενοι</w></rdg>
        <rdg n="2-f1" type="defective" cause="aural-confusion" wit="010C 012"><w>ου</w><w>χαριτι</w><w>εσται</w><w>σεσωσμενοι</w></rdg>
        <rdg n="2-f2" type="defective" wit="010*"><w>ου</w><w>χαριτι</w><w>εσται</w><w>σεωσμενοι</w></rdg>
        <rdg n="2-s1" type="subreading" cause="clarification" wit="06*"><w>ου</w><w>τη</w><w>χαριτι</w><w>εστε</w><w>σεσωσμενοι</w></rdg>
        <rdg n="3" wit="copsa copbo"><w>χαριτι</w><w>γαρ</w><w>εστε</w><w>σεσωσμενοι</w></rdg>
    </app>

Alternatively, this can be done in a more precise and hierarchical
fashion using ``rdgGrp`` elements with the appropriate types:

.. code:: xml

    <app xml:id="B10K2V5U20-24">
        <lem><w>χαριτι</w><w>εστε</w><w>σεσωσμενοι</w></lem>
        <rdg n="1" wit="UBS P46 01 03 06C2 18 33 35 88 424 606 915 1175 1505 1611 1739 1881 2495 syrh Jerome TheodoreOfMopsuestia"><w>χαριτι</w><w>εστε</w><w>σεσωσμενοι</w></rdg>
        <rdgGrp type="defective">
            <rdg n="1-f1" cause="aural-confusion" wit=""><w>χαριτι</w><w>εσται</w><w>σεσωσμενοι</w></rdg>
            <rdgGrp type="reconstructed">
                <rdg n="1-f1-v1" wit="02"><w>χαριτι</w><w>εσται</w><w>σ<unclear>ε</unclear><supplied reason="lacuna">σω</supplied>σμενοι</w></rdg>
            </rdgGrp>
        </rdgGrp>
        <rdg n="2" wit="Ambrosiaster MariusVictorinus Pelagius"><w>ου</w><w>χαριτι</w><w>εστε</w><w>σεσωσμενοι</w></rdg>
        <rdgGrp type="defective">
            <rdg n="2-f1" cause="aural-confusion" wit="010C 012"><w>ου</w><w>χαριτι</w><w>εσται</w><w>σεσωσμενοι</w></rdg>
            <rdg n="2-f2" wit="010*"><w>ου</w><w>χαριτι</w><w>εσται</w><w>σεωσμενοι</w></rdg>
        </rdgGrp>
        <rdgGrp type="subreading">
            <rdg n="2-s1" cause="clarification" wit="06*"><w>ου</w><w>τη</w><w>χαριτι</w><w>εστε</w><w>σεσωσμενοι</w></rdg>
        </rdgGrp>
        <rdg n="3" wit="copsa copbo"><w>χαριτι</w><w>γαρ</w><w>εστε</w><w>σεσωσμενοι</w></rdg>
    </app>

This utility is designed to accept both types of input. Readings without
a ``@type`` attribute are assumed to be substantive. In both cases, the
``rdg`` or ``rdgGrp`` elements should be placed according to where their
type falls in the hierarchy; a reconstruction of a defective reading (e.g.,
reading ``1-f1-v1``) should be placed directly after the defective reading
itself (e.g., ``1-f1``). Likewise, for the purposes of resolving
ambiguous readings, no two readings in the same ``app`` element should
be assigned the same ``@xml:id`` or ``@n`` attribute, even if they are
under different ``rdgGrp`` elements.

If you want to collapse certain types of readings under their “parent”
readings, then you can specify this using the ``-t`` argument with any
conversion command invoked through the command-line interface (CLI). So with the
flags

::

   -t reconstructed -t defective -t orthographic -t subreading

the variation unit illustrated above would have only three substantive
readings (``1``, ``2``, and ``3``), while with the flags

::

   -t reconstructed -t defective -t orthographic

it would have four substantive readings (``1``, ``2``, ``2-s1``, and
``3``).

Ambiguities and Judgments of Certainty
--------------------------------------

When you have one or more witnesses with an ambiguous attestation, you may
wish to express which readings the witness(es) in question might have.
The TEI Guidelines
(https://www.tei-c.org/release/doc/tei-p5-doc/en/html/TC.html#TCAPWD)
describe a ``witDetail`` element suitable for this purpose: like the
``rdg`` element, it includes a ``@wit`` attribute (for the one or more
witnesses it describes) and a ``@target`` attribute (which can point to
one or more readings these witnesses might have). For example:

.. code:: xml

    <app xml:id="B10K3V9U6">
        <lem><w>παντας</w></lem>
        <rdg xml:id="B10K3V9U6R1" wit="UBS P46 01C2 03 04 06 010 012 18 33 35 88 424 606 915 1175 1505 1611 1910 2495 vg syrp syrh copsa copbo Chrysostom MariusVictorinus Pelagius TheodoreOfMopsuestia"><w>παντας</w></rdg>
        <rdg xml:id="B10K3V9U6R2" wit="01* 02 424C 1739 1881 Jerome"/>
        <witDetail n="W1/2" type="ambiguous" target="#B10K3V9U6R1 #B10K3V9U6R2" wit="Ambrosiaster"><certainty target="1" locus="value" degree="0.5000"/><certainty target="2" locus="value" degree="0.5000"/></witDetail>
    </app>

Underneath this element, you can optionally include ``certainty``
elements (also depicted in the above example), which can indicate
different probabilities associated with their respective targeted
readings. If these are not specified, then the readings referenced by
the ``witDetail`` element's ``@target`` attribute will be assigned equal
probabilities. While it is recommended that you specify values between 0
and 1 for the ``@degree`` attribute of each ``certainty`` element, this
is not necessary; the values you specify will be normalized in the
conversion.

The example above follows the TEI Guidelines more strictly, in that it
uses the ``@xml:id`` attribute instead of the ``@n`` attribute to assign
URIs to individual readings, and it references these URIs in the
``@target`` attributes of the ``witDetail`` element and the
``certainty`` elements it contains. As a general rule, the values of the
``@wit`` and ``@target`` attributes should technically be
space-separated pointers to unique elements (which, within the XML
collation document, are ``@xml:id`` values prefixed by the ``#``
character). But in practice, this tends to produce very verbose reading
IDs and references, and it is not particularly convenient for certain
conventions regarding witness IDs. (This applies especially to New
Testament textual critics, who use primarily numerical Gregory-Aland IDs
to refer to manuscripts; unfortunately, XML guidelines prohibit
``@xml:id`` values that begin with numbers.) For ease of use, this
software relaxes this assumption and interprets pointers that do not
start with ``#`` as referring to ``@n`` values (both for witnesses or
for readings within the same ``app`` element). So the following more
compact format is also supported, even if it is not strictly valid TEI
XML:

.. code:: xml

    <app xml:id="B10K3V9U6">
        <lem><w>παντας</w></lem>
        <rdg n="1" wit="UBS P46 01C2 03 04 06 010 012 18 33 35 88 424 606 915 1175 1505 1611 1910 2495 vg syrp syrh copsa copbo Chrysostom MariusVictorinus Pelagius TheodoreOfMopsuestia"><w>παντας</w></rdg>
        <rdg n="2" wit="01* 02 424C 1739 1881 Jerome"/>
        <witDetail n="W1/2" type="ambiguous" target="1 2" wit="Ambrosiaster"><certainty target="1" locus="value" degree="0.5000"/><certainty target="2" locus="value" degree="0.5000"/></witDetail>
    </app>

The only condition is that you must use these attributes consistently:
if you label a ``rdg`` element with an ``@xml:id`` attribute, then you
must reference that attribute's value in the ``witDetail`` and
``certainty`` elements; otherwise, you must use and reference the ``@n``
attribute.

For NEXUS output, the character states for each witness are encoded using
``StatesFormat=StatesPresent`` by default, meaning that each non-missing character is
represented by a single symbol or by a set of symbols between braces (in the case of ambiguous readings).
An example of this encoding is the following: ``P46 1003110?001011000200100001000100001{01}0100``.
This setting produces more compact outputs and is the expected states format for PAUP* and most other programs.
The downside is that it cannot accommodate degrees of certainty in ambiguous readings.

If you want your NEXUS output to contain the character states for each witness using ``StatesFormat=Frequency``,
with each character represented by a vector of frequencies for each reading/state, you can do this with the ``--frequency`` option to ``teiphy``.
For unambiguous readings, the corresponding state vector will have a value of 1 for a single
reading/state.
For simple ambiguous readings encoded as ``witDetail`` elements
with the potential readings specified in the ``@target`` attribute, 
the state vector will have a value of 1 for each specified reading/state;
and for ``witDetail`` elements containing ``certainty``
elements with varying ``@degree`` attributes,
the ``@degree`` value for each specified reading will be copied to the state vector.
With this setting in the NEXUS output, the sequence for witness P46 would look as follows:

::

    P46
        (0:0.0000 1:1.0000)
        (0:1.0000 1:0.0000 2:0.0000)
        (0:1.0000 1:0.0000)
        (0:0.0000 1:0.0000 2:0.0000 3:1.0000)
        (0:0.0000 1:1.0000)
        (0:0.0000 1:1.0000)
        (0:1.0000 1:0.0000 2:0.0000 3:0.0000)
        ?
        (0:1.0000 1:0.0000 2:0.0000 3:0.0000 4:0.0000 5:0.0000)
        ...
        (0:0.0148 1:0.9852)
        (0:1.0000 1:0.0000)
        (0:0.0000 1:1.0000)
        (0:1.0000 1:0.0000)
        (0:1.0000 1:0.0000)

For current phylogenetic software that accepts NEXUS input, the ``StatesFormat=Frequency`` setting is not supported,
so for most output formats, ``witDetail`` elements containing ``certainty``
elements with varying ``@degree`` attributes will simply be mapped to ambiguous states
with a 1 for every reading covered by a ``certainty`` element.
For formats that do not even support ambiguities with specified target states, 
ambiguous ``witDetail`` elements, with or without ``certainty`` elements,
will be mapped to missing states (i.e., the ``?`` symbol).
For NEXUS outputs with the default ``StatesPresent`` encoding, you can also include the ``--ambiguous-as-missing`` flag if you want to coerce all ambiguous states to be encoded as missing states.
Since BEAST 2 supports tip likelihoods, ``certainty`` values are preserved in BEAST 2.7 XML outputs by default.

Lacunae and Other Missing Data
------------------------------

In the interest of accounting for all witnesses, a collation might
include placeholder ``rdg`` or ``witDetail`` elements for witnesses that
are entirely lacunose, illegible, or otherwise unavailable (e.g., due to
missing images or irrelevance due to a different reading in an
overlapping passage) at each point of variation. As long as these
placeholders are labeled with ``@type`` elements, you can specify that
they correspond to missing data using the ``-m`` argument with any command
invoked through the CLI.

Consider the following set of variation units:

.. code:: xml

    <!-- a large transposition is encoded as an overlapping unit below -->
    <app xml:id="B10K4V28U18-26">
        <rdg n="1" wit="UBS P46 01 02 03 06 010 012 1175 vg copbo Ambrosiaster Jerome MariusVictorinus Pelagius">
            <ref target="#B10K4V28U18-22">[B10K4V28U18-22]</ref>
            <ref target="#B10K4V28U24-26">[B10K4V28U24-26]</ref>
        </rdg>
        <rdg n="2" wit="18 35 88 424* 606 915 1505 1611 1910 2495 syrh Chrysostom TheodoreOfMopsuestia">
            <ref target="#B10K4V28U24-26">[B10K4V28U24-26]</ref>
            <ref target="#B10K4V28U18-22">[B10K4V28U18-22]</ref>
        </rdg>
        <rdg xml:id="B10K4V28U18-24R3" n="3" wit="33 424C 1739 1881">
            <ref target="#B10K4V28U18-20">[B10K4V28U18-20]</ref>
        </rdg>
        <rdg xml:id="B10K4V28U18-24R4" n="4" wit="copsa">
            <ref target="#B10K4V28U22-24">[B10K4V28U22-24]</ref>
        </rdg>
        <witDetail n="Z" type="lac" wit="04 06C1 06C2 syrp syrhmg"/>
    </app>
    <app xml:id="B10K4V28U18-22">
        <lem><w>ταις</w><w>ιδιαις</w><w>χερσιν</w></lem>
        <rdg n="1" wit="UBS 01* 02 03C2 06C1 06C2 010 012 606 915 1175 1505 2495 copbo Jerome MariusVictorinus TheodoreOfMopsuestia"><w>ταις</w><w>ιδιαις</w><w>χερσιν</w></rdg>
        <rdg n="1-f1" type="defective" cause="aural-confusion" wit="06*"><w>ταις</w><w>ιδιαις</w><w>χιρσιν</w></rdg>
        <rdg n="1-o1" type="orthographic" wit="1611"><w>ταις</w><w>ιδιαις</w><w>χερσι</w></rdg>
        <rdg n="2" wit="P46 01C2 03* 18 35 88 424* 1910 copsa Ambrosiaster Chrysostom Pelagius"><w>ταις</w><w>χερσιν</w></rdg>
        <witDetail n="W1/2-1" type="ambiguous" target="1 2" cause="translation" xml:lang="syr" wit="syrp syrh"><w>ܒܐܝܕܘܗܝ</w></witDetail>
        <witDetail n="W1/2-2" type="ambiguous" target="1 2" wit="vg"><certainty target="1" locus="value" degree="0.3333"/><certainty target="2" locus="value" degree="0.6667"/></witDetail>
        <witDetail n="↑B10K4V28U18-24R3" type="overlap" target="#B10K4V28U18-24R3" wit="33 424C 1739 1881"/>
        <witDetail n="Z" type="lac" wit="04 syrhmg"/>
    </app>
    <!-- this unit should be ignored -->
    <app xml:id="B10K4V28U24-26">
        <lem><w>το</w><w>αγαθον</w></lem>
        <rdg n="1" wit="UBS P46 01 02 03 06 010 012 18 33 35 88 424 606 915 1175 1505 1611 1739 1881 1910 2495 vg syrp syrh copbo Ambrosiaster Chrysostom Jerome MariusVictorinus Pelagius TheodoreOfMopsuestia"><w>το</w><w>αγαθον</w></rdg>
        <witDetail n="↑B10K4V28U18-24R4" type="overlap" target="#B10K4V28U18-24R4" wit="copsa"/>
        <witDetail n="Z" type="lac" wit="04 06C1 06C2 424C syrhmg"/>
    </app>

In the first variation unit, readings ``3`` and ``4`` omit one of the
phrases covered in the next two variation units. (They are assigned
``@xml:id`` values so that they can be referenced from these other
units.) The ``witDetail`` elements in those units with a ``@type`` of
``overlap`` describe the witnesses that attest to no readings there
because of their omission in the overlapping unit. Likewise, the
``witDetail`` with a ``@type`` of ``lac`` indicates which witnesses are
lacunose at each unit. Both types of readings can be treated as missing
characters (which has the default representation ``?`` in NEXUS output)
for the witnesses that attest to them by specifying the following
arguments when invoking any conversion command through the CLI:

::

   -m lac -m overlap

Correctors' Hands
-----------------

Collation data often distinguishes the first hand responsible for a
manuscript from the hands of correctors who introduced changed readings
either into the text or into the margin of the same manuscript. Some
manuscripts include multiple layers of correction, where each corrector
can be assumed to have had knowledge of any previous correctors' notes.
Since the activity of most correctors is sporadic, the average corrector
will effectively be a fragmentary witness in the places where he or she
is cited in the apparatus. But if you wish to assume that each corrector
approved of all the readings from the previous hand that he or she did
not change, then you can “fill out” each corrector's text using the text
of the first hand (for the first corrector) or the filled-out text of
the previous corrector (for all subsequent correctors). Under this
assumption, the placement of the corrector on a phylogenetic tree will
be facilitated by the disambiguation of what would otherwise be the
corrector's “missing” characters.

To enable this behavior, you first have to ensure that the desired
correctors have their own ``witness`` elements in the collation
``listWit`` element and that they have a ``@type`` value of
``corrector``. An example for the first hand and the first two
correctors of Codex Bezae follows:

.. code:: xml

   <witness n="06"/>
   <witness type="corrector" n="06C1"/>
   <witness type="corrector" n="06C2"/>

Then, when you invoke any conversion command through the CLI, make sure that you include the ``--fill-correctors`` argument.

Excluding Fragmentary witnesses
-------------------------------

Fragmentary witnesses with too many missing readings can introduce more noise than signal to a phylogenetic analysis, so it is often helpful to exclude such witnesses from the phylogenetic software inputs you generate.
You can do this using the ``--fragmentary-threshold`` command-line option.
With this option, you must specify a number between 0 and 1 that represents the proportion of extant readings that a witness must have in order to be included in the output.
For the purposes of determining whether a witness meets or falls below this threshold, that witness is considered non-extant/lacunose at a variation unit if the type of its reading in that unit is in the user-specified list of missing reading types (i.e., the argument(s) of the ``-m`` option).
This calculation is performed after the reading sequences of correctors have been filled in (if the ``--fill-correctors flag`` was specified).
A threshold specified with ``--fragmentary-threshold 0.7``, for example, means that a witness with missing readings at more than 30 percent of variation units will be excluded from the output.
By comparison, ``--fragmentary-threshold 1.0`` will exclude any witness that has even one missing reading.

Removing First-hand Siglum Suffixes and Merging Multiple Attestations
---------------------------------------------------------------------

In some instances, the siglum for a manuscript may have a first-hand
suffix added to it when the manuscript was corrected at the unit in
question. In New Testament textual criticism, the first hand in the
presence of correctors is conventionally suffixed with ``*``, and the
first hand in the presence of an alternative reading or the lemma text
in a commentary that evidently supports a different reading is suffixed
with ``T``. Other times, a manuscript might repeat the same text
multiple times with different variations, resulting in multiple
attestations within the same witness. In New Testament textual
criticism, this commonly occurs with lectionaries and catena
commentaries, and the multiple attestations are indicated by the
suffixes ``/1``, ``/2``, etc. The inclusion of these suffixes in the
``@wit`` attribute of a reading is not strictly in accordance with the
TEI Guidelines, but for the sake of convenience, this behavior is
supported by this utility.

For the purposes of analysis, you will usually want to strip the
first-hand suffixes, leaving just the base sigla for the witnesses
themselves. In addition, you may wish to merge multiple attestations of a
passage in the same witness, effectively treating multiple attestations
as ambiguous readings. Both can be accomplished using the ``-s``
argument with any conversion command invoked through the CLI. If you
want to strip first-hand suffixes only, then you can do this via

::

   -s"*" -s T

This will ignore multiple attestations (i.e., treat the units where they
occur as missing characters for the base witnesses with multiple
attestations at those units), unless the sigla with multiple attestation
suffixes are included as distinct ``witness`` elements in the
collation's ``listWit`` element.
Note that the ``*`` character must be passed as an option in a special way (i.e., as ``-s"*"``, with no space after the argument and surrounding quotation marks)
because it is a reserved character on the command line and must be escaped properly.

If you want to strip first-hand suffixes and merge all multiple
attestations, then you can do so via

::

   -s"*" -s"T" -s"/1" -s"/2" -s"/3"

assuming that there are at most three multiple attestations in any unit.

Ascertainment Bias
------------------

To facilitate accurate branch length estimation, ``teiphy`` includes all constant sites (i.e., variation units with only one substantive reading after trivial readings have been merged with their parents) in its output by default.
(The only exception is output for the ``stemma`` program, which is parsimony-based and does not estimate branch lengths.)
If you want only sites with textual variants to be included in your output, then you can ensure that this happens by including the ``--drop-constant`` flag in your command.

Note that if you do exclude constant sites, or if your TEI XML collation only includes locations in the textual tradition where the readings differ, 
then it will be important to correct for ascertainment bias when performing phylogenetic analysis which utilizes the branch lengths 
(such as maximum-likelihood or Bayesian techniques).
This is because when the data is filtered to only include locations where changes have occurred, the analysis can be biased towards longer branch lengths.
There are methods to correct for this, for example, as discussed in Lewis, 2001 :cite:p:`lewis_likelihood_2001`.
Because this correction is amply supported by existing phylogenetic software packages, ``teiphy`` will not perform this correction itself.
You should consult the documentation for your phylogenetic software package to determine how it applies ascertainment bias correction.
For example, `IQ-TREE <http://www.iqtree.org/doc/Substitution-Models#ascertainment-bias-correction>`_ allows users to correct for ascertainment bias by adding ``+ASC`` to the model name.
(Just keep in mind that your input must be free of constant sites for this to work!)

Tree Priors, Clock Models, and Tip Dates
----------------------------------------

For outputs for MrBayes (i.e., NEXUS files generated with the ``--mrbayes`` option) and BEAST (i.e., XML files following the conventions of BEAST 2.7),
tree priors based on birth-death models and strict clock models are used by default.
For MrBayes, the ``clock:birthdeath`` prior is used for the tree, and for BEAST, the ``BDSKY`` (Birth-Death Skyline model) prior is used.
For both formats, the origin of the model is set based on the earliest possible date for the textual tradition, if it is known.
In TEI XML, this is specified in a ``bibl`` element under the ``sourceDesc`` element, as in the following example:

.. code:: xml

    <bibl>
        <title xml:lang="grc">Πρὸς Ἐφεσίους</title>
        <date notBefore="50" notAfter="80"/>
    </bibl>

If an earliest possible date is specified, then the origin for the model is assigned a uniform prior 
between this date and the latest possible date for the tradition 
(which, if is it not specified explicitly, is set according to the earliest witness, or, absent witness dates, the current date).
If no earliest possible date it specified, then the origin for the model is assigned a gamma prior in MrBayes or a log-normal prior in BEAST; 
in either case, the prior distribution is offset according to the latest possible date for the tradition.
The speciation/reproductive number, extinction/become-uninfectious rate, and sampling proportion priors are set to default distibutions by ``teiphy``.

The clock model set in the output file by ``teiphy`` can be selected using the ``--clock`` command-line option.
Presently, the following three models are supported:
* ``strict``: a strict clock model, with the same mutation rate applied at all branches. 
This is the default option.
* ``uncorrelated``: an uncorrelated random clock model, with mutation rates assigned randomly to branches according to a particular distribution.
For MrBayes, this corresponds to the independent gamma rate (IGR) model with a log-normal prior on the mean clock rate and an exponential prior on the variance.
For BEAST, the clock rate's mean and standard deviation both have log-normal priors.
* ``local``: a local random clock model, where branches inherit their parent branch's clock rate subject to random perturbations.
This option is only supported for BEAST outputs.

Finally, for both MrBayes and BEAST, tip dates are calibrated according to the dates specified for witnesses.
These dates can be specified either exactly (in which case the tip date has a fixed distribution) 
or within a range (in which case the tip date has a uniform distribution of the witness's date span),
as in the following examples:

.. code:: xml

    <witness n="18">
        <origDate when="1364"/>
    </witness>
    <witness n="33">
        <origDate notBefore="800" notAfter="900"/>
    </witness>

As part of the Bayesian phylogenetic analysis, the distributions of the tip dates for witnesses with date ranges will also be estimated.

Tip dates are also used by ``teiphy`` in converting TEI XML to inputs to the ``stemma`` program, as ``stemma`` uses date ranges to constrain the relationships between witnesses that it will consider.

Root Frequencies and Substitution Models
----------------------------------------

Since BEAST's XML input format supports phylogenetic analogues of intrinsic probabilities
(i.e., the probability that a given reading is authorial)
and transcriptional probability (i.e., the probability that one reading would give rise to another according to common mechanisms of scribal error or innovation)
in the forms of root frequencies at variation units
and rate variables used in the substitution models of variation units,
``teiphy`` can map TEI XML encodings of these judgments to the appropriate elements in BEAST 2.7 XML.

To encode intrinsic probabilities in a consistent and rigorous way, you can define discrete odds categories with fixed values as analytic tags using code like the following:

.. code:: xml

    <interpGrp type="intrinsic">
        <interp xml:id="RatingA">
            <p>The current reading is absolutely more likely than the linked reading.</p>
            <certainty locus="value" degree="19"/>
        </interp>
        <interp xml:id="RatingB">
            <p>The current reading is strongly 
            more likely than the linked reading.</p>
            <certainty locus="value" degree="4"/>
        </interp>
        <interp xml:id="RatingC">
            <p>The current reading is more likely
            than the linked reading.</p>
            <certainty locus="value" degree="1.5"/>
        </interp>
        <interp xml:id="RatingD">
            <p>The current reading is slightly more likely than the linked reading.</p>
            <certainty locus="value" degree="1.1"/>
        </interp>
        <interp xml:id="EqualRating">
            <p>The current reading and the linked reading 
            are equally likely.</p>
            <certainty locus="value" degree="1"/>
        </interp>
    </interpGrp>

The specified odds values are defined in the ``@degree`` attributes of ``certainty`` elements.
These categories can be used to define the relative probabilities of variant readings in a given variation unit under a ``note`` element in that unit using ``relation`` elements as follows:

.. code:: xml

    <listRelation type="intrinsic">
        <relation active="1" passive="2" ana="#RatingA"/>
        <relation active="2" passive="3" ana="#EqualRating"/>
        <relation active="3" passive="4" ana="#EqualRating"/>
    </listRelation>

In terms of the analytic categories defined above, this list of ``relation`` elements indicates that reading 1 is nineteen times more likely to be authorial than reading 2, and readings 2 and 3 are equally likely.
This results in root frequencies of 0.9048, 0.0476, and 0.0476.
If no such set of relations is specified, then the root frequencies are set according to a uniform distribution by default.

If you wish to incorporate transcriptional probabilities for different classes of scribal changes into your analysis, you may do so by defining analytic tags for rate parameters as follows:

.. code:: xml

    <interpGrp type="transcriptional">
        <interp xml:id="Clar">
            <p>Clarification of the text in terms of grammar, 
            style, or theology.</p>
        </interp>
        <interp xml:id="AurConf">
            <p>Aural confusion concerning letters or dipthongs 
            that came to have the same sound in later Greek.</p>
        </interp>
        <interp xml:id="LingConf">
            <p>Linguistic confusion concerning rules 
            of Greek grammar.</p>
            <p><i>Constructiones ad sensum</i> that reflect 
            changes in grammatical rules over time 
            also fall under this rubric.</p>
        </interp>
        <interp xml:id="VisErr">
            <p>Visual error, such as paleographic confusion 
            of similar letters, haplography, dittography, 
            and other skips of the eye resulting in small omissions. 
            Rarer situations, like duplication or omission 
            of letters related to the presence or absence 
            of an ornamental capital at the start of a line, 
            also fall under this rubric.</p>
        </interp>
        <interp xml:id="Harm">
            <p>Harmonization, either to a parallel passage 
            or to the near context.</p>
        </interp>
        <interp xml:id="Byz">
            <p>The text is brought into conformity 
            with the Byzantine text.</p>
        </interp>
    </interpGrp>

If you wish to specify fixed rates for these transcriptional change classes, then you can do so using ``certainty`` elements 
as in the definitions of the intrinsic odds categories above.
Any classes without fixed rates will have their rates estimated as part of the phylogenetic model.
Transitions between different readings in a given variation unit can then be categorized with one or more of these tags in a ``note`` element in that unit 
(parallel to the ``listRelation`` used to encode the intrinsic probabilities of the readings) as follows:

.. code:: xml

    <listRelation type="transcriptional">
        <relation active="1 2 3" passive="4" ana="#Harm"/>
        <relation active="1" passive="2 3 4" ana="#Clar"/>
        <relation active="2" passive="1" ana="#VisErr"/>
        <relation active="2" passive="3" ana="#Clar #Harm"/>
        <relation active="3" passive="4" ana="#Clar"/>
        <relation active="1 2 4" passive="3" ana="#Byz"/>
    </listRelation>

To allow for more succinct encodings of transitions, multiple possible source and target readings can be specified in the ``@active`` and ``@passive`` attributes of a ``relation`` element,
and more than one analytic tag can be specified in the ``@ana`` attribute;
thus, ``<relation active="1 2 3" passive="4" ana="#Harm"/>`` indicates that reading 1, 2, or 3 could give rise to reading 4 by harmonization, 
``<relation active="1" passive="2 3 4" ana="#Clar"/>`` indicates that reading 1 could give rise to reading 2, 3, or 4 by clarification,
and ``<relation active="2" passive="3" ana="#Clar #Harm"/>`` indicates that reading 2 could give to reading 3 by clarification or harmonization.
When these transitions are tagged in this way, ``teiphy`` will map them to the off-diagonal entries of the substitution matrix for this variation unit, 
summing multiple rates if more than one tag is specified for a transition.
All transitions not covered by a ``relation`` element (e.g., a transition from reading 3 to reading 1, which is not covered in the example above) will be assigned the "default" rate of 1.
Accordingly, if no ``listRelation`` for transcriptional change categories is specified at all, then the substitution model for a variation unit with *k* substantive readings will default to the Lewis Mk model.

In many cases, certain transcriptional explanations are applicable only at certain times.
For instance, assimilation to a popular text that arose at a later point in the tradition's history (modeled with the ``Byz`` class in the above example) would only be available as a transcriptional explanation after this point.
Skips of the eye may be empirically more common for earlier scribes than for later ones.
Certain paleographic confusions may only be possible for earlier scripts or later ones.
Specific orthodox corruptions of sacred texts may have only become plausible after certain theological conflicts or developments had taken place to inspire them.
If you wish to encode such transcriptional possibilities as time-dependent, you can do so by adding ``@notBefore`` and ``@notAfter`` attributes to the corresponding ``relation`` element:

.. code:: xml

    <listRelation type="transcriptional">
        <relation active="1 2 3" passive="4" ana="#Harm"/>
        <relation active="1" passive="2 3 4" ana="#Clar"/>
        <relation active="2" passive="1" ana="#VisErr"/>
        <relation active="2" passive="3" ana="#Clar #Harm"/>
        <relation active="3" passive="4" ana="#Clar"/>
        <relation active="1 2 4" passive="3" ana="#Byz" notBefore="500"/>
    </listRelation>

If you tag certain transcriptional ``relation`` elements in this way, ``teiphy`` will map the ``listRelation`` to an ``EpochSubstitutionModel`` instance consisting of multiple substitution models that apply at the corresponding points in time.

Assigning Weights to Sites (for Weighted Parsimony)
---------------------------------------------------

If you are using ``stemma``, you can assign different weights to variation units so that changes in those units will contribute more or less to the cost of a candidate stemma.
As with intrinsic and transcriptional probabilities, you can do this by defining analytic tags for different variation categories as follows:

.. code:: xml

    <interpGrp type="weight">
        <interp xml:id="Semantic">
            <p>The current variation unit involves semantic changes.</p>
            <certainty locus="value" degree="10"/>
        </interp>
        <interp xml:id="Idiolectal">
            <p>The current variation unit involves idiolectal changes.</p>
            <certainty locus="value" degree="5"/>
        </interp>
        <interp xml:id="Pragmatic">
            <p>The current variation unit involves pragmatic changes.</p>
            <certainty locus="value" degree="2"/>
        </interp>
        <interp xml:id="Aural">
            <p>The current variation unit involves changes due to similar sounds.</p>
            <certainty locus="value" degree="1"/>
        </interp>
    </interpGrp>

As with intrinsic odds categories, you can assign fixed weights to different categories using ``certainty`` elements, where a given category's weight is specified in the ``@degree`` attribute.
In the above example, units characterized by changes of the ``Aural`` category will have the lowest weight (corresponding to changes judged to be most common), while those characterized by ``Semantic`` changes will have the highest weight (corresponding to changes judged to be least common).
Since ``stemma`` only supports integer weights, any floating-point weights specified in this way will be coerced to integers by truncating their fractional part.
If you do not specify any weight for a category, its weight will default to 1.

You can then assign one or more of these categories to each variation unit in your TEI XML collation.
Specifically, for each ``app`` element, you can provide one or more pointers to these categories using the ``@ana`` attribute, as in the following example:

.. code:: xml

    <app xml:id="B10K1V15U26-40" ana="#Pragmatic #Semantic">
        ...
    </app>

In this case, two categories, ``Pragmatic`` and ``Semantic``, are referenced.
If a variation unit is associated with only one category, then variations in it will incur costs scaled by that category's weight.
If it is associated with more than one category, then variations in it will incur costs scaled by the average of those categories' weights.
If a variation unit is associated with no category, then its weight will default to 1.

Note that all changes in a weighted variation unit, regardless of their source and target readings or their direction, will have the same weight.
Assigning varying weights to transitions between specific readings is not supported in ``stemma``.
In a Bayesian phylogenetic setting, this can be done in BEAST 2 using transcriptional relations, as described in the previous section.

Logging for Ancestral State Reconstructions
-------------------------------------------

BEAST 2 offers support for the logging of the reconstructed states (i.e., variant readings) for each site (i.e., variation unit) at varying levels of detail.
The ``AncestralStateLogger`` class (part of the ``BEASTLabs`` package) reconstructs the state of a particular clade (which, for our purposes, is chosen to be the root of the tree) in each tree sampled during the analysis, resulting in a relatively compact output.
The ``AncestralSequenceLogger`` class (part of the ``BEAST_CLASSIC`` package) reconstructs the states of all hypothetical ancestors in each tree sampled during the analysis, which results in a more comprehensive, but also much larger output.
In writing to BEAST 2.7 XML files, ``teiphy`` can include elements for either (or neither) logger based on the ``--ancestral-logger`` argument.
The default option, ``state``, will include an ``AncestralStateLogger`` element in the XML file, while ``sequence`` will include an ``AncestralSequenceLogger`` element, and ``none`` will not include any logging elements for ancestral states.

Overriding or Supplying Dates from a CSV file
---------------------------------------------

You can also specify date ranges for some witnesses in a separate CSV file.
For the sake of completeness, it is recommended that you specify date ranges for witnesses in your TEI XML collation, but you may have pulled your collation data and witness date ranges from different sources, or you might want to overwrite existing date ranges in the collation with updated values.
You can specify a path to the CSV file containing witness IDs and their date ranges using the ``--dates-file`` command-line option.
The CSV file should not have any header rows, and every row should be formatted as ``"id",min,max``, where the first column contains a string (encoded as such by being surrounded by double quotes) corresponding to the witness ID and the other two columns are either empty (if one or both ends of the date range are unknown) or integers corresponding to years (where negative integers are assumed to refer to dates BCE). 

Supported Output Formats and Options
------------------------------------

You can specify a preferred output format for the conversion explicitly with the ``--format`` flag.
Supported options include ``nexus``, ``hennig86``, ``phylip`` (note that the relaxed version of this format used by RAxML, which has better support for multi-state characters, is used rather than the strict version), ``fasta``, ``xml`` (specifically, the flavor of XML read by BEAST 2.7), ``csv``, ``tsv``, ``excel`` (note that only ``.xlsx`` format is supported), and ``stemma``.
If you do not supply a ``--format`` argument, then ``teiphy`` will attempt to infer the correct format from the file extension of the output file name.

By default, ``teiphy`` includes constant characters (i.e., variation units where all witnesses attest to the same substantive reading) in its outputs.
If you wish to exclude these from your analysis (as is the case if you want to use ascertainment bias correction in your phylogenetic software), then you can do so by specifying the ``--drop-constant`` flag.

For ``nexus`` outputs, the ``CharStateLabels`` block (which provides human-readable labels for variation units and readings) is included in the output file by default, but you can disable it by specifying the ``--no-labels`` flag.
This is necessary if you intend to pass your NEXUS-formatted data to phylogenetic programs like MrBayes that do not recognize this block.
Note that all reading labels will be slugified so that all characters (e.g., Greek characters) are converted to ASCII characters and spaces and other punctuation marks are replaced by underscores; this is to conformance with the recommendations for the NEXUS format.

Note that for ``hennig86``, ``phylip``, and ``fasta`` output formats, only up to 32 states (represented by the symbols 0-9 and a-v) are supported at this time.
This is a requirement for Hennig86 format, and some phylogenetic programs that use these formats (such as IQTREE and RAxML) do not support symbols outside of the basic 36 alphanumeric characters or a 32-character alphabet at this time.
The ``stemma`` output format currently supports up to 62 states.
Outputs in ``nexus`` format also support up to 62 states to accommodate software like PAUP* and Andrew Edmondson's fork of MrBayes (https://github.com/edmondac/MrBayes), but note that some of the programs listed above will not work with ``nexus`` inputs with a state alphabet this large. 

Collations can also be converted to tabular formats.
Within Python, the ``collation`` class's ``to_numpy`` method can be invoked to convert a collation to a NumPy ``array`` with rows for variant readings, columns for witnesses, and frequency values in the cells.
Where a witness has missing data at a variation, its frequencies for different readings at this unit can be split over 1 using the ``split_missing`` argument.
If the ``uniform`` option is specified for this argument, then the frequency of 1 is split over all substantive readings, corresponding to a flat prior about what the witness's missing reading was.
If the ``proportional`` option is specified for this argument, then the frequency of 1 is split in proportion to the readings' support from witnesses whose readings are not missing, corresponding to a prior informed by the sample populations for the readings.
Otherwise, the witness will have frequencies of 0 for all readings at that unit.
The same class's ``to_distance_matrix`` method produces a NumPy ``array`` with rows and columns for witnesses, where each cell contains the number of units where the row witness and column witness both have unambiguous readings and these readings disagree.
The cells can instead be populated with the proportion of disagreements among units where the row and column witnesses have readings with the ``proportion`` argument.
If you specify the ``show_ext`` argument as True, then each cell will be populated by the number or proportion of disagreements followed by the number of units where both witnesses have have unambiguous readings (e.g., 3/50 or 0.06/50).
The same class's ``to_similarity_matrix`` method produces a NumPy ``array`` with rows and columns for witnesses, where each cell contains the number of units where the row witness and column witness both have unambiguous readings and these readings agree.
The cells can instead be populated with the proportion of agreements among units where the row and column witnesses have readings with the ``proportion`` argument.
The same class's ``to_idf_matrix`` method produces a NumPy ``array`` with rows and columns for witnesses, where each cell contains the sum of inverse document frequency (IDF)-weighted agreements between the corresponding witnesses.
This value corresponds to the total expected information content (in bits) of the event of the correponding witnesses' agreement, with more exclusive agreements receiving higher weights.
If you specify the ``show_ext`` argument as True, then each cell will be populated by the number or proportion of agreements followed by the number of units where both witnesses have have unambiguous readings (e.g., 47/50 or 0.94/50).
The same class's ``to_nexus_table`` method produces a NumPy ``array`` with rows for witnesses, columns for variation unit IDs, and attested reading IDs in the cells, resembling a NEXUS sequence.
By default, cells corresponding to ambiguous readings are written as space-separated sequences of readings between braces, but they can be written as missing states with the ``ambiguous_as_missing`` argument.
The same class's ``to_long_table`` method produces a NumPy ``array`` with columns for witness ID, variation unit ID, reading index, and reading text and rows for all combinations of these values found in the collation.
The ``to_dataframe`` method invokes ``to_numpy`` by default, but if the ``table_type`` argument is ``distance``, ``agreement``, ``idf``, ``nexus`` or ``long``, then it will invoke ``to_distance_matrix``, ``to_agreement_matrix``, ``to_idf_matrix``, ``to_nexus_table`` or ``to_long_table``, respectively.
It returns a Pandas ``DataFrame`` augmented with row and column labels (or, in the case of a long table, just column labels).

From the command line, the types of matrices listed above can be written to a specified CSV, TSV, or Excel (.xlsx) file.
If you specify the output filename with its extension, ``teiphy`` will infer which format to use.
If you want to write a distance matrix, a similarity matrix, a NEXUS-style table, or a long table to output instead of a reading-witness matrix, then you can do so by specifying the ``--table distance``, ``--table similarity``, ``--table nexus``, or ``--table long`` command-line argument, respectively.
If you are writing a reading-witness matrix to output, you can set the method's ``split_missing`` argument using the ``--split-missing`` command-line flag.
If you are writing a distance or similarity matrix to output, then you can set the method's ``proportion`` and ``show_ext`` arguments using using the ``--proportion`` and ``--show-ext`` command-line flags, respectively.
As with plain NEXUS outputs, if you are writing a NEXUS table to output, then you can set the method's ``ambiguous_as_missing`` argument using the ``--ambiguous-as-missing`` command-line flag.
You can also write a pairwise distance or similarity matrix to a PHYLIP (.phy, .ph) file if you specify ``--table distance`` or ``--table similarity`` as an option with a PHYLIP output.
(Note that only these two table types are support for this output format; if you specify any other type of table with a PHYLIP output, then the option will be ignored, and a standard PHYLIP output will be generated instead.)
The ``--proportion`` and ``--show-ext`` flags are supported for PHYLIP matrix outputs.

Other Options
-------------

If you wish to include status messages for the purposes of measuring
performance or validating your collation, you can include the
``--verbose`` flag when you invoke any conversion command through
the CLI.

To run this script with the example input in verbose mode with the settings described above enabled, enter ``teiphy`` directory and enter the command

::

   teiphy -t reconstructed -t defective -t orthographic -t subreading -m lac -m overlap -s"*" -s T -s /1 -s /2 -s /3 --fill-correctors --verbose example\ubs_ephesians.xml ubs_ephesians.nxs

from the command line.