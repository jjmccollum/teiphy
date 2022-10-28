==================
Advanced Usage
==================

Lacunae, retroversions, and other sources of ambiguity occasionally make
a one-to-one mapping of witnesses to readings impossible, and in some
cases, one disambiguation may be more likely than another in a
quantifiable way. Mechanisms for accommodating such situations exist in
both TEI XML and NEXUS, and for likelihood-based phylogenetic methods,
“soft decisions” about the states at the leaves and even the root of the
tree can provide useful information to the inference process. For these
reasons, ``teiphy`` ensures that these types of judgments, as well as
other rich features from TEI XML, can be respected (and, where,
necessary, preserved) in the conversion process.


Collations should preserve
as much detail as possible, including information on how certain types
of data can be normalized and collapsed for analysis. Since we may want
to conduct the same analysis at different levels of granularity, the
underlying collation data should be available for us to use in any case,
and only the output should reflect changes in the desired level of
detail. Likewise, as noted in the previous section, uncertainty about
witnesses’ attestations should be encoded in the collation and preserved
in the conversion of the collation.

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
the ``witDetail`` element’s ``@target`` attribute will be assigned equal
probabilities. While it is recommended that you specify values between 0
and 1 for the ``@degree`` attribute of each ``certainty`` element, this
is not necessary; the values you specify will be normalized in the
conversion.

This example above follows the TEI Guidelines more strictly, in that it
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
must reference that attribute’s value in the ``witDetail`` and
``certainty`` elements; otherwise, you must use and reference the ``@n``
attribute.

For NEXUS output, the character states for each witness is encoded using
``StatesFormat=Frequency``, meaning that each non-missing character is
represented as a vector of frequencies for each reading/state. For
unambiguous readings, this vector should have a value of 1 for a single
reading/state, while for ambiguous readings, it should have multiple
values for different readings/states.

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

Correctors’ Hands
-----------------

Collation data often distinguishes the first hand responsible for a
manuscript from the hands of correctors who introduced changed readings
either into the text or into the margin of the same manuscript. Some
manuscripts include multiple layers of correction, where each corrector
can be assumed to have had knowledge of any previous correctors’ notes.
Since the activity of most correctors is sporadic, the average corrector
will effectively be a fragmentary witness in the places where he or she
is cited in the apparatus. But if you wish to assume that each corrector
approved of all the readings from the previous hand that he or she did
not change, then you can “fill out” each corrector’s text using the text
of the first hand (for the first corrector) or the filled-out text of
the previous corrector (for all subsequent correctors). Under this
assumption, the placement of the corrector on a phylogenetic tree will
be facilitated by the disambiguation of what would otherwise be the
corrector’s “missing” characters.

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
collation’s ``listWit`` element.
Note that the ``*`` character must be passed as an option in a special way (i.e., as ``-s"*"``, with no space after the argument and surrounding quotation marks)
because it is a reserved character on the command line and must be escaped properly.

If you want to strip first-hand suffixes and merge all multiple
attestations, then you can do so via

::

   -s"*" -s"T" -s"/1" -s"/2" -s"/3"

assuming that there are at most three multiple attestations in any unit.

Supported Output Formats and Options
------------------------------------

You can specify a preferred output format for the conversion explicitly with the ``--format`` flag.
Supported options include ``nexus``, ``hennig86``, ``phylip`` (note that the relaxed version of this format used by RAxML, which has better support for multi-state characters, is used rather than the strict version), ``fasta``, ``csv``, ``tsv``, ``excel`` (note that only ``.xlsx`` format is supported), and ``stemma``.
If you do not supply a ``--format`` argument, then ``teiphy`` will attempt to infer the correct format from the file extension of the output file name.

For ``nexus`` outputs, the ``CharStateLabels`` block (which provides human-readable labels for variation units and readings) is included in the output file by default, but you can disable it by specifying the ``--no-labels`` flag.
This is necessary if you intend to pass your NEXUS-formatted data to phylogenetic programs like MrBayes that do not recognize this block.
Note that all reading labels will be slugified so that all characters (e.g., Greek characters) are converted to ASCII characters and spaces and other punctuation marks are replaced by underscores; this is to conformance with the recommendations for the NEXUS format.

For ``nexus`` outputs, you can also include a ``--states-present`` flag, which will convert your collation data for each witness to a string of mostly single-state symbols, 
including symbols that represent missing readings, as well as some multi-state symbols in braces representing ambiguous readings (e.g., ``P46 1003110?001011000200100001000100001{01}0100``).
The ``StatesFormat=StatesPresent`` NEXUS setting produces more compact outputs and is the expected states format for PAUP*.
The downside is that it cannot accommodate degrees of certainty in ambiguous readings.
If the ``--states-present`` flag is not supplied, then the more precise ``StatesFormat=Frequency`` setting is used by default, which encodes reading states as frequency vectors:

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

For ``nexus`` outputs with the ``--states-present`` flag set, you can also include the ``--ambiguous-as-missing`` flag if you want to treat all ambiguous states as missing states.
If your NEXUS-formatted output is to be used by a phylogenetic software that ignores or does not recognize ambiguous states, you may want or need to use this option.

Note that for the ``nexus``, ``hennig86``, ``phylip``, and ``fasta`` output formats, only up to 32 states (represented by the symbols 0-9 and a-v) are supported at this time.
This is a requirement for Hennig86 format, and some phylogenetic programs that use these formats (such as IQTREE and RAxML) do not support symbols outside of the basic 36 alphanumeric characters or a 32-character alphabet at this time.

Other Options
-------------

If you wish to include status messages for the purposes of measuring
performance or validating your collation, you can include the
``--verbose`` flag when you invoke any conversion command through
the CLI.

To run this script with the example input in verbose mode with the settings described above enabled, enter ``teiphy`` directory and enter the command

::

   teiphy -t reconstructed -t defective -t orthographic -t subreading -m lac -m overlap -s"*" -s T -s /1 -s /2 -s /3 --fill-correctors --states-present --verbose example\ubs_ephesians.xml ubs_ephesians.nxs

from the command line.