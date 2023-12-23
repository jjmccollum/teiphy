.. start-badges

.. image:: https://raw.githubusercontent.com/jjmccollum/teiphy/main/docs/img/teiphy-logo.svg

|license badge| |testing badge| |coverage badge| |docs badge| |black badge| |git3moji badge| 
|iqtree badge| |raxml badge| |mrbayes badge| |beast badge| |stemma badge| |joss badge| |doi badge|

.. |license badge| image:: https://img.shields.io/badge/license-MIT-blue.svg?style=flat
    :target: https://choosealicense.com/licenses/mit/

.. |testing badge| image:: https://github.com/jjmccollum/teiphy/actions/workflows/testing.yml/badge.svg
    :target: https://github.com/jjmccollum/teiphy/actions/workflows/testing.yml

.. |docs badge| image:: https://github.com/jjmccollum/teiphy/actions/workflows/docs.yml/badge.svg
    :target: https://jjmccollum.github.io/teiphy
    
.. |black badge| image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black
    
.. |coverage badge| image:: https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/jjmccollum/62997df516f95bbda6eaefa02b9570aa/raw/coverage-badge.json
    :target: https://jjmccollum.github.io/teiphy/coverage/

.. |git3moji badge| image:: https://img.shields.io/badge/git3moji-%E2%9A%A1%EF%B8%8F%F0%9F%90%9B%F0%9F%93%BA%F0%9F%91%AE%F0%9F%94%A4-fffad8.svg
    :target: https://robinpokorny.github.io/git3moji/

.. |iqtree badge| image:: https://github.com/jjmccollum/teiphy/actions/workflows/iqtree.yml/badge.svg
    :target: https://github.com/jjmccollum/teiphy/actions/workflows/iqtree.yml

.. |raxml badge| image:: https://github.com/jjmccollum/teiphy/actions/workflows/raxml.yml/badge.svg
    :target: https://github.com/jjmccollum/teiphy/actions/workflows/raxml.yml

.. |mrbayes badge| image:: https://github.com/jjmccollum/teiphy/actions/workflows/mrbayes.yml/badge.svg
    :target: https://github.com/jjmccollum/teiphy/actions/workflows/mrbayes.yml

.. |beast badge| image:: https://github.com/jjmccollum/teiphy/actions/workflows/beast.yml/badge.svg
    :target: https://github.com/jjmccollum/teiphy/actions/workflows/beast.yml

.. |stemma badge| image:: https://github.com/jjmccollum/teiphy/actions/workflows/stemma.yml/badge.svg
    :target: https://github.com/jjmccollum/teiphy/actions/workflows/stemma.yml

.. |joss badge| image:: https://joss.theoj.org/papers/e0a813f4cdf56e9f6ae5d555ce6ed93b/status.svg
    :target: https://joss.theoj.org/papers/e0a813f4cdf56e9f6ae5d555ce6ed93b
    
.. |doi badge| image:: https://zenodo.org/badge/DOI/10.5281/zenodo.7455638.svg
   :target: https://doi.org/10.5281/zenodo.7455638

.. end-badges

.. start-about

A Python package for converting TEI XML collations to NEXUS and other formats.

Textual scholars have been using phylogenetics to analyze manuscript traditions since the early 1990s.
Many standard phylogenetic software packages accept as input the `NEXUS file format <https://doi.org/10.1093/sysbio/46.4.590>`_.
The ``teiphy`` program takes a collation of texts encoded using the `Text Encoding Initiative (TEI) guidelines <https://tei-c.org/release/doc/tei-p5-doc/en/html/TC.html>`_
and converts it to a NEXUS format so that it can be used for phylogenetic analysis.
It can also convert to other formats as well, including Hennig86 (for TNT), PHYLIP (for RAxML), FASTA, and the XML format used by BEAST 2.7.


.. end-about


.. start-quickstart

Installation
============

The software can be installed using ``pip``:

.. code-block:: bash

    pip install teiphy

Alternatively, you can install the package by cloning this repository and installing it with poetry:

.. code-block:: bash

    git clone https://github.com/jjmccollum/teiphy.git
    cd teiphy
    pip install poetry
    poetry install

Once the package is installed, you can run all unit tests via the command

.. code-block:: bash

    poetry run pytest

Usage
============

To use the software, run the ``teiphy`` command line tool:

.. code-block:: bash

    teiphy <input TEI XML> <output file>

``teiphy`` can export to NEXUS, Hennig86 (TNT), PHYLIP (in the relaxed form used by RAxML), FASTA, BEAST 2.7 XML, CSV, TSV, Excel and STEMMA formats. 
``teiphy`` will try to infer the file format to export to from the extension of the output file. Accepted file extensions are:
".nex", ".nexus", ".nxs", ".ph", ".phy", ".fa", ".fasta", ".xml", ".tnt", ".csv", ".tsv", ".xlsx".

To explicitly say which format you wish to export to, use the ``--format`` option. For example:

.. code-block:: bash

    teiphy <input TEI XML> <output file> --format nexus

For more information about the other options, see the help with:

.. code-block:: bash

    teiphy --help

Or see the documentation with explanations about `advanced usage <https://jjmccollum.github.io/teiphy/advanced.html>`_.

The software can also be used in Python directly. 
See `API Reference <https://jjmccollum.github.io/teiphy/reference.html>`_ in the documentation for more information.

.. end-quickstart

Credits
============

.. start-credits

``teiphy`` was designed by Joey McCollum (Australian Catholic University) and Robert Turnbull (University of Melbourne).
We received additional help from Stephen C. Carlson (Australian Catholic University).

If you use this software, please cite the paper: Joey McCollum and Robert Turnbull, "``teiphy``: A Python Package for Converting TEI XML Collations to NEXUS and Other Formats," *JOSS* 7.80 (2022): 4879, DOI: 10.21105/joss.04879.

.. code-block:: bibtex

    @article{MT2022, 
        author = {Joey McCollum and Robert Turnbull}, 
        title = {{teiphy: A Python Package for Converting TEI XML Collations to NEXUS and Other Formats}}, 
        journal = {Journal of Open Source Software},
        year = {2022}, 
        volume = {7}, 
        number = {80}, 
        pages = {4879},
        publisher = {The Open Journal}, 
        doi = {10.21105/joss.04879}, 
        url = {https://doi.org/10.21105/joss.04879}
    }

Further details on the capabilities of ``teiphy``, particularly in terms of the text-critically valuable features it can map from TEI XML collations to BEAST 2 inputs, are discussed in Joey McCollum and Robert Turnbull, "Using Bayesian Phylogenetics to Infer Manuscript Transmission History," *DSH* TBD (2024), DOI: 10.1093/llc/fqad089.

.. code-block:: bibtex

    @article{MT2024, 
        author = {Joey McCollum and Robert Turnbull}, 
        title = {{Using Bayesian Phylogenetics to Infer Manuscript Transmission History}}, 
        journal = {Digital Scholarship in the Humanities},
        year = {2024}, 
        volume = {TBD}, 
        number = {TBD}, 
        pages = {TBD},
        doi = {10.1093/llc/fqad089}, 
        url = {https://doi.org/10.1093/llc/fqad089}
    }

.. end-credits
