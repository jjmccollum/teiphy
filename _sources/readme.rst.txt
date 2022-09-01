======
teiphy
======

General-purpose Python utility for converting TEI XML collations to
NEXUS and other formats.

About This Project
==================

Introduction
------------

This project began as a utility for my PhD research on reconstructing
the textual tradition of Ephesians using phylogenetic methods. Since
transcriptions and collations in the humanities are commonly encoded in
TEI XML format (https://tei-c.org/), while most phylogenetic software
expects input in NEXUS format (https://doi.org/10.1093/sysbio/46.4.590),
I needed a tool to convert my collation data from the former to the
latter.

While this is a straightforward process for most collation data,
lacunae, retroversions, and other sources of ambiguity occasionally make
a one-to-one mapping of witnesses to readings impossible, and in some
cases, one disambiguation may be more likely than another in a
quantifiable way. Mechanisms for accommodating such situations exist in
both TEI XML and NEXUS, and for likelihood-based phylogenetic methods,
“soft decisions” about the states at the leaves and even the root of the
tree can provide useful information to the inference process. For these
reasons, I wanted to ensure that these types of judgments, as well as
other rich features from TEI XML, could be respected (and, where,
necessary, preserved) in the conversion process.

Design Philosophy
-----------------

My underlying philosophy about collations is that they should preserve
as much detail as possible, including information on how certain types
of data can be normalized and collapsed for analysis. Since we may want
to conduct the same analysis at different levels of granularity, the
underlying collation data should be available for us to use in any case,
and only the output should reflect changes in the desired level of
detail. Likewise, as noted in the previous section, uncertainty about
witnesses’ attestations should be encoded in the collation and preserved
in the conversion of the collation.

Installation and Dependencies
=============================

**TBA**

Usage
=====

The usage and expected input format for this utility are described in
what follows. Examples are provided to illustrate different concepts.

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
we assume a hierarchical ordering of reading types (e.g., ``subreading``
> ``orthographic`` > ``defective`` > ``reconstructed``) so we can “roll
up” readings with types lower in the hierarchy into their “parent”
readings with types higher in the hierarchy. This can be done with a
flat list of ``rdg`` elements alone, as follows:

.. code:: xml

   <app xml:id="B10K1V1U24-26">
       <lem><w>εν</w><w>εφεσω</w></lem>
       <rdg n="1" wit="01C2 02 03C2 06 012 018 020 025 044 049 056 075S 0142 0150 0151 0319 1 18 33 35 38 61 69 81 88 93 94 102 104 177 181 203 218 296 322 326 330 337 363 365 383 398 424* 436 442 451 459 462 467 506 606 629 636 664 665 915 1069 1108 1127 1175 1240 1241 1245 1311 1319 1398 1490 1505 1509 1573 1611 1617 1678 1718 1721 1729 1751 1831 1836 1837 1838 1840 1851 1860 1877 1881 1886 1893 1908 1910 1912 1918 1939 1959 1962 1963 1985 1987 1991 1996 1999 2004 2005 2008 2011 2012 2127 2138 2180 2243 2352 2400 2464 2492 2495 2516 2523 2544 2576 2805 2865S L169 L587 L809 L1159 L1178 L1188 L1440 L2058 VL61 VL64 VL75 VL77 VL78 VL89 vgcl vgst vgww syrh syrp copsa copbo gothA gothB Ambrosiaster Chrysostom Jerome MariusVictorinus Pelagius PseudoAthanasius TheodoreOfMopsuestia"><w>εν</w><w>εφεσω</w></rdg>
       <rdg n="1-v1" type="reconstructed" wit="L2010"><w>εν</w><w><unclear>ε</unclear>φεσω</w></rdg>
       <rdg n="1-v2" type="reconstructed" wit="2344"><w><unclear>εν</unclear></w><w>εφεσω</w></rdg>
       <rdg n="1-v3" type="reconstructed" wit="256"><w><supplied reason="lacuna">εν</supplied></w><w><supplied reason="lacuna">εφεσ</supplied>ω</w></rdg>
       <rdg n="1-f1" type="defective" cause="parablepsis" wit="010"><w>εν</w><w>εφεω</w></rdg>
       <rdg n="1-f2" type="defective" cause="dittography" wit="263"><w>εν</w><w>νεφεσω</w></rdg>
       <rdg n="1-o1" type="orthographic" wit="0278"><w>εν</w><w>εφεσωι</w></rdg>
       <rdg n="1-s1" type="subreading" cause="clarification" wit=""><w>εν</w><w>τω</w><w>εφεσω</w></rdg>
       <rdg n="1-s1-v1" type="reconstructed" wit="1115"><w>εν</w><w>τ<unclear>ω</unclear></w><w>εφεσω</w></rdg>
       <rdg n="2" wit="P46 01* 03* 6 424C1 1739 BasilOfCaesarea Ephrem Marcion Origen"/>
   </app>

Alternatively, this can be done in a more precise and hierarchical
fashion using ``rdgGrp`` elements with the appropriate types:

.. code:: xml

   <app xml:id="B10K1V1U24-26">
       <lem><w>εν</w><w>εφεσω</w></lem>
       <rdg n="1" wit="01C2 02 03C2 06 012 018 020 025 044 049 056 075S 0142 0150 0151 0319 1 18 33 35 38 61 69 81 88 93 94 102 104 177 181 203 218 296 322 326 330 337 363 365 383 398 424* 436 442 451 459 462 467 506 606 629 636 664 665 915 1069 1108 1127 1175 1240 1241 1245 1311 1319 1398 1490 1505 1509 1573 1611 1617 1678 1718 1721 1729 1751 1831 1836 1837 1838 1840 1851 1860 1877 1881 1886 1893 1908 1910 1912 1918 1939 1959 1962 1963 1985 1987 1991 1996 1999 2004 2005 2008 2011 2012 2127 2138 2180 2243 2352 2400 2464 2492 2495 2516 2523 2544 2576 2805 2865S L169 L587 L809 L1159 L1178 L1188 L1440 L2058 VL61 VL64 VL75 VL77 VL78 VL89 vgcl vgst vgww syrh syrp copsa copbo gothA gothB Ambrosiaster Chrysostom Jerome MariusVictorinus Pelagius PseudoAthanasius TheodoreOfMopsuestia"><w>εν</w><w>εφεσω</w></rdg>
       <rdgGrp type="reconstructed">
           <rdg n="1-v1" wit="L2010"><w>εν</w><w><unclear>ε</unclear>φεσω</w></rdg>
           <rdg n="1-v2" wit="2344"><w><unclear>εν</unclear></w><w>εφεσω</w></rdg>
           <rdg n="1-v3" wit="256"><w><supplied reason="lacuna">εν</supplied></w><w><supplied reason="lacuna">εφεσ</supplied>ω</w></rdg>
       </rdgGrp>
       <rdgGrp type="defective">
           <rdg n="1-f1" cause="parablepsis" wit="010"><w>εν</w><w>εφεω</w></rdg>
           <rdg n="1-f2" cause="dittography" wit="263"><w>εν</w><w>νεφεσω</w></rdg>
       </rdgGrp>
       <rdgGrp type="orthographic">
           <rdg n="1-o1" wit="0278"><w>εν</w><w>εφεσωι</w></rdg>
       </rdgGrp>
       <rdgGrp type="subreading">
           <rdg n="1-s1" cause="clarification" wit=""><w>εν</w><w>τω</w><w>εφεσω</w></rdg>
           <rdgGrp type="reconstructed">
               <rdg n="1-s1-v1" wit="1115"><w>εν</w><w>τ<unclear>ω</unclear></w><w>εφεσω</w></rdg>
           </rdgGrp>
       </rdgGrp>
       <rdg n="2" wit="P46 01* 03* 6 424C1 1739 BasilOfCaesarea Ephrem Marcion Origen"/>
   </app>

This utility is designed to accept both types of input. Readings without
a ``@type`` attribute are assumed to be substantive. In both cases, the
``rdg`` or ``rdgGrp`` elements should be placed according to where their
type falls in the hierarchy; a reconstruction of a subreading (e.g.,
reading ``1-s1-v1`` should be placed directly after the subreading
itself (e.g., ``1-s1``). Likewise, for the purposes of resolving
ambiguous readings, no two readings in the same ``app`` element should
be assigned the same ``@xml:id`` or ``@n`` attribute, even if they are
under different ``rdgGrp`` elements.

If you want to collapse certain types of readings under their “parent”
readings, then you can specify this using the ``-t`` argument with any
conversion command invoked through the ``main.py`` script. So with the
flags

::

   -t"reconstructed" -t"defective" -t"orthographic" -t"subreading"

the variation unit illustrated above would have only two substantive
readings (``1`` and ``2``), while with the flags

::

   -t"reconstructed" -t"defective"

it would have four substantive readings (``1``, ``1-o1``, ``1-s1``, and
``2``).

Ambiguities and Judgments of Certainty
--------------------------------------

When we have one or more witnesses with an ambiguous attestation, we may
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
       <rdg xml:id="B10K3V9U6R1" wit="P46 01C2 03 04 06 010 012 018 020 025 044 049 056 075 0142 0151 0319 1 18 33 35 38 61 69 81 88 93 94 102 104 177 181 203 218 256 263 296 322 326 330 337 363 365 383 398 424 436 442 451 459 462 467 506 606 629 636 664 665 915 1069 1108 1115 1127 1175 1240 1241 1245 1311 1319 1398 1490 1505 1509 1573 1611 1617 1678 1718 1721 1729 1751 1831 1836 1837 1838 1840 1851 1860 1877 1886 1893 1908 1910 1912 1918 1939 1959 1962 1985 1987 1991C 1996 1999 2004 2008 2011 2012 2127 2138 2180 2243 2344 2352 2400 2464 2492 2495 2516 2523 2544 2576 2805 2865 L156 L169 L587 L809 L1159 L1178 L1188 L1440 L2010 L2058 VL61 VL75 VL77 VL78 VL89 vgcl vgww vgst syrp syrh copsa copbo Adamantius Chrysostom Marcion MariusVictorinus Pelagius Tertullian TheodoreOfMopsuestia"><w>παντας</w></rdg>
       <rdg xml:id="B10K3V9U6R1-f1" type="defective" wit="1963"><w>παντα</w></rdg>
       <rdg xml:id="B10K3V9U6R1-f2" type="defective" cause="linguistic-confusion" wit="1991"><w>παντων</w></rdg>
       <rdg xml:id="B10K3V9U6R2" wit="01* 02 0150 6 424C1 1739 1881 Jerome"/>
       <witDetail n="W1/2" type="ambiguous" target="#B10K3V9U6R1 #B10K3V9U6R2" wit="Ambrosiaster CyrilOfAlexandria"><certainty target="#B10K3V9U6R1" locus="value" degree="0.5000"/><certainty target="#B10K3V9U6R2" locus="value" degree="0.5000"/></witDetail>
   </app>

Underneath this element, we can optionally include ``certainty``
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
       <rdg n="1" wit="P46 01C2 03 04 06 010 012 018 020 025 044 049 056 075 0142 0151 0319 1 18 33 35 38 61 69 81 88 93 94 102 104 177 181 203 218 256 263 296 322 326 330 337 363 365 383 398 424 436 442 451 459 462 467 506 606 629 636 664 665 915 1069 1108 1115 1127 1175 1240 1241 1245 1311 1319 1398 1490 1505 1509 1573 1611 1617 1678 1718 1721 1729 1751 1831 1836 1837 1838 1840 1851 1860 1877 1886 1893 1908 1910 1912 1918 1939 1959 1962 1985 1987 1991C 1996 1999 2004 2008 2011 2012 2127 2138 2180 2243 2344 2352 2400 2464 2492 2495 2516 2523 2544 2576 2805 2865 L156 L169 L587 L809 L1159 L1178 L1188 L1440 L2010 L2058 VL61 VL75 VL77 VL78 VL89 vgcl vgww vgst syrp syrh copsa copbo Adamantius Chrysostom Marcion MariusVictorinus Pelagius Tertullian TheodoreOfMopsuestia"><w>παντας</w></rdg>
       <rdg n="1-f1" type="defective" wit="1963"><w>παντα</w></rdg>
       <rdg n="1-f2" type="defective" cause="linguistic-confusion" wit="1991"><w>παντων</w></rdg>
       <rdg n="2" wit="01* 02 0150 6 424C1 1739 1881 Jerome"/>
       <witDetail n="W1/2" type="ambiguous" target="1 2" wit="Ambrosiaster CyrilOfAlexandria"><certainty target="1" locus="value" degree="0.5000"/><certainty target="2" locus="value" degree="0.5000"/></witDetail>
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
they mark missing data using the ``-m`` argument with any command
invoked through the ``main.py`` script.

Consider the following set of variation units:

.. code:: xml

   <!-- a large transposition is encoded as an overlapping unit below -->
   <app xml:id="B10K4V28U18-24">
       <rdg n="1" wit="018 020 044 049 056 0142 0151 1 18 35 61 88 93 102 177 181 203 296 322 326 337 363 383 398 424* 436 506 606 636 664 665 915 1069 1108 1115 1240 1245 1311 1490 1505 1509 1611 1617 1718 1721 1729 1751 1831 1836 1837 1840 1851 1860 1877 1886 1910 1912 1918 1939 1962 1963 1985 1987 1996 1999 2005 2008 2012 2138 2180 2243 2352 2495 2544 L60 L169 L587 L809 L1159 L1178 L1188 L1440 L2010 L2058 syrh Chrysostom Origen TheodoreOfMopsuestia">
           <ref target="#B10K4V28U18-20">[B10K4V28U18-20]</ref>
           <ref target="#B10K4V28U22-24">[B10K4V28U22-24]</ref>
       </rdg>
       <rdg n="2" wit="P46 P49 01 02 03 06 010 012 075 0150 0319 38 69 81 94 104 218 256 263 330 365 442 451 459 462 467 629 1127 1175 1241 1319 1398 1573 1678C 1838 1893 1908 1959 2004 2011 2127 2344 2400 2464 2492 2516 2523 2576 2805 2865 VL61 VL75 VL77 VL78 VL86 VL89 vgcl vgww vgst copbo Ambrosiaster Jerome MariusVictorinus Pelagius">
           <ref target="#B10K4V28U22-24">[B10K4V28U22-24]</ref>
           <ref target="#B10K4V28U18-20">[B10K4V28U18-20]</ref>
       </rdg>
       <rdg xml:id="B10K4V28U18-24R3" n="3" wit="016 025 6 33 424C1 1739 1881 ClementOfAlexandria Speculum">
           <ref target="#B10K4V28U18-20">[B10K4V28U18-20]</ref>
       </rdg>
       <rdg xml:id="B10K4V28U18-24R4" n="4" wit="1678* 1991 copsa Tertullian">
           <ref target="#B10K4V28U22-24">[B10K4V28U22-24]</ref>
       </rdg>
       <witDetail n="W1/2" type="ambiguous" target="1 2" wit="BasilOfCaesarea"><certainty target="1" locus="value" degree="0.3333"/><certainty target="2" locus="value" degree="0.6667"/></witDetail>
       <witDetail n="Z" type="lac" wit="P92 P132 01C1 01C2 03C1 03C2 04 06C1 06C2 048 075S 082 0159 0230 0278 0285 0320 203S 1942 2834 2865S L23 L156 L1126 L1298 VL51 VL54 VL58 VL59 VL62 VL64 VL65 VL67 VL76 VL83 VL85 syrp syrhmg gothA gothB Adamantius AthanasiusOfAlexandria Cyprian CyrilOfAlexandria CyrilOfJerusalem Ephrem Epiphanius GregoryOfNazianzus GregoryOfNyssa GregoryThaumaturgus Irenaeus Lucifer Marcion Primasius Procopius PseudoAthanasius Severian Theodoret"/>
   </app>
   <app xml:id="B10K4V28U18-20">
       <lem><w>το</w><w>αγαθον</w></lem>
       <rdg n="1" wit="P46 P49 01 02 03 06 010 012 016 018 020 025 044 049 056 075 0142 0150 0151 0319 1 6 18 33 35 38 61 69 81 88 93 94 102 104 177 181 203 218 256 263 296 322 326 330 337 363 365 383 398 424 436 442 451 459 462 467 506 606 629 636 664 665 915 1069 1108 1115 1127 1175 1240 1241 1245 1311 1319 1398 1490 1505 1509 1573 1611 1617 1678C 1718 1721 1729 1739 1751 1831 1836 1837 1838 1840 1851 1860 1877 1881 1886 1893 1908 1910 1912 1918 1939 1959 1962 1963 1985 1987 1996 1999 2004 2005 2008 2011 2012 2127 2138 2180 2243 2344 2352 2400 2464 2492 2495 2516 2523 2544 2576 2805 2865 L60 L169 L587 L809 L1159 L1178 L1188 L1440 L2010 L2058 VL61 VL75 VL77 VL78 VL86 VL89 vgcl vgww vgst syrp syrh copbo Ambrosiaster BasilOfCaesarea Chrysostom ClementOfAlexandria Jerome MariusVictorinus Origen Pelagius Speculum TheodoreOfMopsuestia"><w>το</w><w>αγαθον</w></rdg>
       <rdg n="1-f1" type="defective" cause="aural-confusion" wit="L60"><w>τω</w><w>αγαθων</w></rdg>
       <witDetail n="↑B10K4V28U18-24R4" type="overlap" target="#B10K4V28U18-24R4" wit="1678* 1991 copsa Tertullian"/>
       <witDetail n="Z" type="lac" wit="P92 P132 01C1 01C2 03C1 03C2 04 06C1 06C2 048 075S 082 0159 0230 0278 0285 0320 203S 424C1 1942 2834 2865S L23 L156 L1126 L1298 VL51 VL54 VL58 VL59 VL62 VL64 VL65 VL67 VL76 VL83 VL85 syrhmg gothA gothB Adamantius AthanasiusOfAlexandria Cyprian CyrilOfAlexandria CyrilOfJerusalem Ephrem Epiphanius GregoryOfNazianzus GregoryOfNyssa GregoryThaumaturgus Irenaeus Lucifer Marcion Primasius Procopius PseudoAthanasius Severian Theodoret"/>
   </app>
   <app xml:id="B10K4V28U22-24">
       <lem><w>ταις</w><w>χερσιν</w></lem>
       <rdg n="1" wit="P46 01C2 03 020 044 049 0151 1 18 35 61 88 102 177 203 296 322 326 337 363 398 424* 506 636 664 1069 1108 1115 1240 1245 1617 1678* 1718 1729 1837 1840 1886 1910 1985 1987 2008 2138 2243 2352 L169 L587 L1159 L1178 L1188 L2010 L2058 VL61 vgww vgst copsa Ambrosiaster Chrysostom Origen Pelagius Tertullian"><w>ταις</w><w>χερσιν</w></rdg>
       <rdg n="1-v1" type="reconstructed" wit="P49"><w><supplied reason="lacuna">ταις</supplied></w><w><supplied reason="lacuna">χερσι</supplied><unclear>ν</unclear></w></rdg>
       <rdg n="1-o1" type="orthographic" wit="1851 L809 L1440"><w>ταις</w><w>χερσι</w></rdg>
       <rdg n="1-s1" type="subreading" cause="clarification" wit="1918"><w>εν</w><w>ταις</w><w>χερσιν</w></rdg>
       <rdg n="1-s2" type="subreading" cause="clarification" wit="181"><w>ταις</w><w>χερσιν</w><w>αυτου</w></rdg>
       <rdg n="1-s3" type="subreading" cause="clarification" wit="629"><w>εν</w><w>ταις</w><w>χερσιν</w><w>αυτου</w></rdg>
       <rdg n="2" wit="01* 02 03C2 06C1 06C2 010 012 018 056 0142 0150 0319 38 81 93 104* 436 459 467 606 665 915 1175 1311 1490 1505 1509 1678C 1721 1751 1860 1877 1912 1939 1959 1962 1963 1991 1996 1999 2004 2005 2012 2180 2495 2544 VL75 VL77 VL78 VL86 VL89 vgcl copbo Jerome MariusVictorinus TheodoreOfMopsuestia"><w>ταις</w><w>ιδιαις</w><w>χερσιν</w></rdg>
       <rdg n="2-v1" type="reconstructed" wit="1838"><w>ταις</w><w>ιδ<unclear>ιαις</unclear></w><w>χερσιν</w></rdg>
       <rdg n="2-f1" type="defective" cause="aural-confusion" wit="06*"><w>ταις</w><w>ιδιαις</w><w>χιρσιν</w></rdg>
       <rdg n="2-f2" type="defective" cause="aural-confusion" wit="383"><w>ταις</w><w>ιδειαις</w><w>χερσιν</w></rdg>
       <rdg n="2-f3" type="defective" cause="aural-confusion" wit="2464"><w>ταις</w><w>ειδιαις</w><w>χερσιν</w></rdg>
       <rdg n="2-f4" type="defective" cause="aural-confusion" wit="L60"><w>ταις</w><w>ιδιες</w><w>χερσιν</w></rdg>
       <rdg n="2-o1" type="orthographic" wit="075 69 94 104C 218 256 263 330 365 442 451 462 1127 1241 1319 1398 1573 1611 1893 2011 2127 2344 2400 2492 2516 2523 2576 2805 2865"><w>ταις</w><w>ιδιαις</w><w>χερσι</w></rdg>
       <rdg n="2-s1" type="subreading" cause="parablepsis" wit="1831"><w>ιδιαις</w><w>χερσιν</w></rdg>
       <rdg n="2-s2" type="subreading" cause="parablepsis" wit="1908"><w>ταις</w><w>ιδιαις</w></rdg>
       <!-- the following reading should target readings 1 and 2 if subreadings are treated as trivial -->
       <witDetail n="W1-s3/2" type="ambiguous" target="1-s3 2" wit="1836"><w>εν</w><w>ταις</w><w>ιδιαις</w><w>χερσιν</w><w>αυτου</w></witDetail><!-- conflation or a superfluous clarification to the longer reading-->
       <witDetail n="W1/2-1" type="ambiguous" target="1 2" cause="translation" xml:lang="syr" wit="syrp syrh"><w>ܒܐܝܕܘܗܝ</w></witDetail>
       <witDetail n="W1/2-2" type="ambiguous" target="1 2" wit="BasilOfCaesarea"><certainty target="1" locus="value" degree="0.3333"/><certainty target="2" locus="value" degree="0.6667"/></witDetail>
       <witDetail n="↑B10K4V28U18-24R3" type="overlap" target="#B10K4V28U18-24R3" wit="016 025 6 33 424C1 1739 1881 ClementOfAlexandria Speculum"/>
       <witDetail n="Z" type="lac" wit="P92 P132 01C1 03C1 04 048 075S 082 0159 0230 0278 0285 0320 203S 1942 2834 2865S L23 L156 L1126 L1298 VL51 VL54 VL58 VL59 VL62 VL64 VL65 VL67 VL76 VL83 VL85 syrhmg gothA gothB Adamantius AthanasiusOfAlexandria Cyprian CyrilOfAlexandria CyrilOfJerusalem Ephrem Epiphanius GregoryOfNazianzus GregoryOfNyssa GregoryThaumaturgus Irenaeus Lucifer Marcion Primasius Procopius PseudoAthanasius Severian Theodoret"/>
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
arguments when invoking any conversion command through ``main.py``:

::

   -m"lac" -m"overlap"

Correctors’ Hands
-----------------

Collation data often distinguishes the first hand responsible for a
manuscript from the hands of correctors who introduced changed readings
either into the text or into the margin of the same manuscript. Some
manuscripts include multiple layers of correction, where each corrector
can be assumed to have had knowledge of any previous correctors’ notes.
Since the activity of most correctors is sporadic, the average corrector
will effectively be a fragmentary witness in the places where he or she
is cited in the apparatus. But if we wish to assume that each corrector
approved of all the readings from the previous hand that he or she did
not change, then we can “fill out” each corrector’s text using the text
of the first hand (for the first corrector) or the filled-out text of
the previous corrector (for all subsequent correctors). Under this
assumption, the placement of the corrector on a phylogenetic tree will
be facilitated by the disambiguation of what would otherwise be the
corrector’s “missing” characters.

To enable this behavior, you first have to ensure that the desired
correctors have their own ``witness`` elements in the collation
``listWit`` element and that they have a ``@type`` value of
``corrector``. An example for the first hand and the first two
correctors of Codex Sinaiticus follows:

.. code:: xml

   <witness n="01"/>
   <witness type="corrector" n="01C1"/>
   <witness type="corrector" n="01C2"/>

Then, when you invoke any conversion command through the ``main.py``
script, make sure that you include the ``--fill-correctors`` argument.

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

For the purposes of analysis, we will usually want to strip the
first-hand suffixes, leaving just the base sigla for the witnesses
themselves. In addition, we may wish to merge multiple attestations of a
passage in the same witness, effectively treating multiple attestations
as ambiguous readings. Both can be accomplished using the ``-s``
argument with any conversion command invoked through ``main.py``. If we
want to strip first-hand suffixes only, then we can do this via

::

   -s"*" -s"T"

This will ignore multiple attestations (i.e., treat the units where they
occur as missing characters for the base witnesses with multiple
attestations at those units), unless the sigla with multiple attestation
suffixes are included as distinct ``witness`` elements in the
collation’s ``listWit`` element.

If we want to strip first-hand suffixes and merge all multiple
attestations, then we can do so via

::

   -s"*" -s"T" -s"/1" -s"/2" -s"/3"

assuming that there are at most three multiple attestations in any unit.

Other Options
-------------

If you wish to include status messages for the purposes of measuring
performance or validating your collation, you can include the
``--verbose`` flag when you invoke any conversion command through
``main.py``.

To run this script with the example input in verbose mode with all of
the settings described above enabled, enter ``teiphy`` directory and
enter the command

::

   python teiphy\main.py to-nexus -t"reconstructed" -t"defective" -t"orthographic" -t"subreading" -m"lac" -m"overlap" -s"*" -s"T" -s"/1" -s"/2" -s"/3" --fill-correctors --verbose example\ubs_ephesians.xml ubs_ephesians.nxs

from the command line.
(If you are using Mac or Linux rather than Windows, make sure you use a forward slash instead of a backward one.)