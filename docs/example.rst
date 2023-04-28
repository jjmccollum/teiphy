=======
Example
=======

Due to the availability of extensive collation data for the Greek New
Testament, and because this project was originally developed for use
with such data, we tested this library on a sample collation of the book of
Ephesians in thirty-eight textual witnesses (including manuscripts,
correctors’ hands, translations to other languages, and quotations from
church fathers). The manuscript transcriptions used for this collation
were those produced by the University of Birmingham’s Institute for
Textual Scholarship and Electronic Editing (ITSEE) for the International
Greek New Testament Project (IGNTP); they are freely accessible at
https://itseeweb.cal.bham.ac.uk/epistulae/XML/igntp.xml. To achieve a
balance between variety and conciseness, we restricted the collation to
a set of forty-two variation units in Ephesians corresponding to
variation units in the United Bible Societies Greek New Testament, 
which highlights variation units that affect substantive
matters of translation.

In our example collation, witnesses are described in the ``listWit``
element under the ``teiHeader``. Because most New Testament witnesses
are identified by numerical Gregory-Aland identifiers, these witnesses
are identified with ``@n`` attributes; the recommended practice is to
identify such elements by ``@xml:id`` attributes, but this software is
designed to work with either identifying attribute (preferring
``@xml:id`` if both are provided), and we have left things as they are
to demonstrate this feature.

The ``witness`` elements in the example collation also contain ``origDate`` elements that provide dates or date ranges for the corresponding witnesses.
Where a witness can be dated to a specific year, the ``@when`` attribute is sufficient to specify this; if it can be dated within a range of years,
the ``@notBefore`` and ``@notAfter`` attributes should be used.
While such dating elements are not required, our software includes them in the conversion process whenever possible.
This way, phylogenetic methods that employ clock models and other chronolological constraints can benefit from this information when it is provided.

Each variation unit is encoded as an ``app`` element with a unique
``@xml:id`` attribute. Within a variation unit, a ``lem`` element
without a ``@wit`` attribute presents the main text, and it is followed
by ``rdg`` elements that describe variant readings (with the first
``rdg`` duplicating the ``lem`` reading and detailing its witnesses) and
their attestations among the witnesses. (Situations where the ``lem``
reading is not duplicated by the first ``rdg`` element, but has its own
``@wit`` attribute, are also supported.) For conciseness, we use the
``@n`` attribute for each reading as a local identifier; the recommended
practice for readings that will be referenced elsewhere is to use the
``@xml:id`` attribute, and this software will use this as the identifier
if it is specified, but we have only specified ``@xml:id`` attributes
for ``rdg`` elements referenced in other variation units to demonstrate
the flexibility of the software. For witnesses with missing or ambiguous
readings at a given variation unit, we use the ``witDetail`` element.
For ambiguous readings, we specify their possible disambiguations with
the ``@target`` attribute and express our degrees of certainty about
these disambiguations using ``certainty`` elements under the
``witDetail`` element.

The `TEI XML file <https://github.com/jjmccollum/teiphy/blob/main/example/ubs_ephesians.xml>`__
for this example is available in the ``example`` directory in the GitHub repository.

IQ-TREE
=======

`IQ-TREE <http://www.iqtree.org/>`_ is a popular phylogenetic analysis package. 
To use it to perform a maximum likelihood phylogenetic analysis of the Ephesians example, 
convert the TEI XML to NEXUS format using ``teiphy`` with the command

.. code:: bash

    teiphy -t reconstructed -t defective -t orthographic -m overlap -m lac -s"*" -s T --fill-correctors example/ubs_ephesians.xml ubs_ephesians_iqtree.nexus

This file can then be run in IQ-TREE with the following command:

.. code:: bash

    iqtree -s ubs_ephesians_iqtree.nexus -m MK -bb 1000

This uses the Lewis Mk substitution model (without ascertainment bias correction) and with 1000 bootstrap replicates.
If you wish to use ascertainment bias correction, then you must first exclude constant sites from the output as follows:

.. code:: bash

    teiphy -t reconstructed -t defective -t orthographic -m overlap -m lac -s"*" -s T --drop-constant --fill-correctors example/ubs_ephesians.xml ubs_ephesians_iqtree.nexus

This file can then be run in IQ-TREE with ascertainment bias correction using the following command:

.. code:: bash

    iqtree -s ubs_ephesians_iqtree.nexus -m MK+ASC -bb 1000

An example of a tree produced by IQ-TREE is found below:

.. image:: https://raw.githubusercontent.com/jjmccollum/teiphy/main/docs/img/iqtree.svg

Running this example with IQ-TREE is part of the continuous integration pipeline: |iqtree badge|

MrBayes
=======

`MrBayes <https://nbisweden.github.io/MrBayes/>`_ is a Bayesian phylogenetic software package.
To use it to perform a phylogenetic analysis of the Ephesians example, 
convert the TEI XML to NEXUS format using ``teiphy`` with this command:

.. code:: bash

    teiphy -t reconstructed -t defective -t orthographic -m overlap -m lac -s"*" -s T --fill-correctors --no-labels example/ubs_ephesians.xml ubs_ephesians_mrbayes.nexus

.. note::

    MrBayes requires the ``--no-labels`` flag.

This will generate the input file for MrBayes with the default strict clock model.
If you would prefer to use an uncorrelated (independent gamma rate) clock model, then you can do so with the following command:

.. code:: bash

    teiphy -t reconstructed -t defective -t orthographic -m overlap -m lac -s"*" -s T --fill-correctors --no-labels --clock uncorrelated example/ubs_ephesians.xml ubs_ephesians_mrbayes.nexus

This file can then be read into MrBayes as follows:

.. code:: bash

    mb ubs_ephesians_mrbayes.nexus

More settings can be added manually to the NEXUS file to control the Bayesian analysis as described in the `MrBayes manual <https://github.com/NBISweden/MrBayes/blob/develop/doc/manual/Manual_MrBayes_v3.2.pdf>`_.

An example of a maximum clade credibility tree produced by MrBayes for the generated input with a strict clock is found below. 
The label on each internal node is the probability of that clade being present in the posterior:

.. image:: https://raw.githubusercontent.com/jjmccollum/teiphy/main/docs/img/mrbayes.svg

Running this example with MrBayes is part of the continuous integration pipeline: |mrbayes badge|

BEAST 2.7
=========

`BEAST 2 <http://www.beast2.org/>`_ is another Bayesian phylogenetic software package that boasts various model options and extensive customizability.
To use it to perform a phylogenetic analysis of the Ephesians example, 
convert the TEI XML to BEAST 2.7 XML format using ``teiphy`` with this command:

.. code:: bash

    teiphy -t reconstructed -t defective -t orthographic -t subreading -m overlap -m lac -s"*" -s T --fill-correctors example/ubs_ephesians.xml ubs_ephesians_beast.xml

This will generate the input file for BEAST with the default strict clock model.
If you would prefer to use an uncorrelated random clock model or a local random clock model, then you can do so with either of the following commands, respectively:

.. code:: bash

    teiphy -t reconstructed -t defective -t orthographic -t subreading -m overlap -m lac -s"*" -s T --fill-correctors --clock uncorrelated example/ubs_ephesians.xml ubs_ephesians_beast.xml
    teiphy -t reconstructed -t defective -t orthographic -t subreading -m overlap -m lac -s"*" -s T --fill-correctors --clock local example/ubs_ephesians.xml ubs_ephesians_beast.xml

To run this input, you must first make sure that you have BEAST 2.7 or later installed (as earlier versions will not be compatible with the XML format)
and that the BEASTLabs and BDSKY packages are installed (which you can do using the ``packagemanager`` utility that comes with BEAST 2).
Once these packages are installed, you can run the example with the command

.. code:: bash

    beast ubs_ephesians_beast.xml

An example of a maximum clade credibility tree produced by BEAST 2 for the generated input with a strict clock is found below. 
The label on each internal node is the probability of that clade being present in the posterior:

.. image:: https://raw.githubusercontent.com/jjmccollum/teiphy/main/docs/img/beast.svg

Running this example with BEAST 2 is part of the continuous integration pipeline: |beast badge|

STEMMA
=======

`STEMMA <https://github.com/stemmatic/stemma>`_ is a phylogenetic analysis program written by Stephen C. Carlson. 
It searches for an optimal stemma topology according to the maximum-parsimony criterion
and uses reticulating links to model contamination between branches to form a phylogenetic network.

To create the files required for STEMMA, run this command:

.. code:: bash

    teiphy -t reconstructed -t defective -t orthographic -m overlap -m lac -s"*" -s T --fill-correctors --format stemma example/ubs_ephesians.xml stemma_example

This will create two files: ``stemma_example`` (containing the textual information from the collation) and ``stemma_example_chron`` (containing date ranges for witnesses). 

These can then be used with Carlson's `prep <https://github.com/stemmatic/prep>`_ program to prepare the file for phylogenetic analysis:

.. code:: bash

    prep stemma_example

Finally, the analysis is run with these commands:

.. code:: bash

    stemma stemma_example a 100
    soln stemma_example SOLN

This begins a heuristic search for the optimal stemma using a simulated annealing approach (option ``a``) for 100 iterations.

An example of a tree produced by STEMMA is found below:

.. image:: https://raw.githubusercontent.com/jjmccollum/teiphy/main/docs/img/stemma.svg

Note that some witnesses (e.g., 012, 35) from the collation are excluded from this tree by STEMMA
because they have the same reading sequence as another witness
after their reconstructed, defective, and orthographic readings have been regularized.

Running this example with STEMMA is part of the continuous integration pipeline: |stemma badge|

.. |iqtree badge| image:: https://github.com/jjmccollum/teiphy/actions/workflows/iqtree.yml/badge.svg
    :target: https://github.com/jjmccollum/teiphy/actions/workflows/iqtree.yml

.. |mrbayes badge| image:: https://github.com/jjmccollum/teiphy/actions/workflows/mrbayes.yml/badge.svg
    :target: https://github.com/jjmccollum/teiphy/actions/workflows/mrbayes.yml

.. |beast badge| image:: https://github.com/jjmccollum/teiphy/actions/workflows/beast.yml/badge.svg
    :target: https://github.com/jjmccollum/teiphy/actions/workflows/beast.yml

.. |stemma badge| image:: https://github.com/jjmccollum/teiphy/actions/workflows/stemma.yml/badge.svg
    :target: https://github.com/jjmccollum/teiphy/actions/workflows/stemma.yml

