#!/usr/bin/env python3

from typing import List, Union
from pathlib import Path
import time  # to time calculations for users
import string  # for easy retrieval of character ranges
from lxml import etree as et  # for reading TEI XML inputs
import numpy as np  # for collation matrix outputs
import pandas as pd  # for writing to DataFrames, CSV, Excel, etc.
from slugify import slugify  # for converting Unicode text from readings to ASCII for NEXUS

from .common import xml_ns, tei_ns
from .format import Format
from .witness import Witness
from .variation_unit import VariationUnit


class Collation:
    """Base class for storing TEI XML collation data internally.

    This corresponds to the entire XML tree, rooted at the TEI element of the collation.

    Attributes:
        manuscript_suffixes: A list of suffixes used to distinguish manuscript subwitnesses like first hands, correctors, main texts, alternate texts, and multiple attestations from their base witnesses.
        trivial_reading_types: A set of reading types (e.g., "reconstructed", "defective", "orthographic", "subreading") whose readings should be collapsed under the previous substantive reading.
        missing_reading_types: A set of reading types (e.g., "lac", "overlap") whose readings should be treated as missing data.
        fill_corrector_lacunae: A boolean flag indicating whether or not to fill "lacunae" in witnesses with type "corrector".
        witnesses: A list of Witness instances contained in this Collation.
        witness_index_by_id: A dictionary mapping base witness ID strings to their int indices in the witnesses list.
        variation_units: A list of VariationUnit instances contained in this Collation.
        readings_by_witness: A dictionary mapping base witness ID strings to lists of reading support coefficients for all units (with at least two substantive readings).
        substantive_variation_unit_ids: A list of ID strings for variation units with two or more substantive readings.
        substantive_variation_unit_reading_tuples: A list of (variation unit ID, reading ID) tuples for substantive readings.
        verbose: A boolean flag indicating whether or not to print timing and debugging details for the user.
    """

    def __init__(
        self,
        xml: et.ElementTree,
        manuscript_suffixes: List[str] = [],
        trivial_reading_types: List[str] = [],
        missing_reading_types: List[str] = [],
        fill_corrector_lacunae: bool = False,
        verbose: bool = False,
    ):
        """Constructs a new Collation instance with the given settings.

        Args:
            xml: An lxml.etree.ElementTree representing an XML tree rooted at a TEI element.
            manuscript_suffixes: An optional list of suffixes used to distinguish manuscript subwitnesses like first hands, correctors, main texts, alternate texts, and multiple attestations from their base witnesses.
            trivial_reading_types: An optional set of reading types (e.g., "reconstructed", "defective", "orthographic", "subreading") whose readings should be collapsed under the previous substantive reading.
            missing_reading_types: An optional set of reading types (e.g., "lac", "overlap") whose readings should be treated as missing data.
            fill_corrector_lacunae: An optional flag indicating whether or not to fill "lacunae" in witnesses with type "corrector".
            verbose: An optional flag indicating whether or not to print timing and debugging details for the user.
        """
        self.manuscript_suffixes = manuscript_suffixes
        self.trivial_reading_types = set(trivial_reading_types)
        self.missing_reading_types = set(missing_reading_types)
        self.fill_corrector_lacunae = fill_corrector_lacunae
        self.verbose = verbose
        self.witnesses = []
        self.witness_index_by_id = {}
        self.variation_units = []
        self.readings_by_witness = {}
        self.substantive_variation_unit_ids = []
        self.substantive_variation_unit_reading_tuples = []
        # Now parse the XML tree to populate these data structures:
        if self.verbose:
            print("Initializing collation...")
        t0 = time.time()
        self.parse_list_wit(xml)
        self.parse_apps(xml)
        self.parse_readings_by_witness()
        t1 = time.time()
        if self.verbose:
            print("Total time to initialize collation: %0.4fs." % (t1 - t0))

    def parse_list_wit(self, xml: et.ElementTree):
        """Given an XML tree for a collation, populates its list of witnesses from its listWit element.

        Args:
            xml: An lxml.etree.ElementTree representing an XML tree rooted at a TEI element.
        """
        if self.verbose:
            print("Parsing witness list...")
        t0 = time.time()
        self.witnesses = []
        self.witness_index_by_id = {}
        for w in xml.xpath(
            "/tei:TEI/tei:teiHeader/tei:fileDesc/tei:sourceDesc/tei:listWit/tei:witness", namespaces={"tei": tei_ns}
        ):
            wit = Witness(w, self.verbose)
            self.witness_index_by_id[wit.id] = len(self.witnesses)
            self.witnesses.append(wit)
        t1 = time.time()
        if self.verbose:
            print("Finished processing %d witnesses in %0.4fs." % (len(self.witnesses), t1 - t0))
        return

    def parse_apps(self, xml: et.ElementTree):
        """Given an XML tree for a collation, populates its list of variation units from its app elements.

        Args:
            xml: An lxml.etree.ElementTree representing an XML tree rooted at a TEI element.
        """
        if self.verbose:
            print("Parsing variation units...")
        t0 = time.time()
        for a in xml.xpath('//tei:app', namespaces={'tei': tei_ns}):
            vu = VariationUnit(a, self.verbose)
            self.variation_units.append(vu)
        t1 = time.time()
        if self.verbose:
            print("Finished processing %d variation units in %0.4fs." % (len(self.variation_units), t1 - t0))
        return

    def get_base_wit(self, wit: str):
        """Given a witness siglum, strips of the specified manuscript suffixes until the siglum matches one in the witness list or until no more suffixes can be stripped.

        Args:
            wit: A string representing a witness siglum, potentially including suffixes to be stripped.
        """
        base_wit = wit
        # If our starting siglum corresponds to a siglum in the witness list, then just return it:
        if base_wit in self.witness_index_by_id:
            return base_wit
        # Otherwise, strip any suffixes we find until the siglum corresponds to a base witness in the list
        # or no more suffixes can be stripped:
        suffix_found = True
        while suffix_found:
            suffix_found = False
            for suffix in self.manuscript_suffixes:
                if base_wit.endswith(suffix):
                    suffix_found = True
                    base_wit = base_wit[: -len(suffix)]
                    break  # stop looking for other suffixes
            # If the siglum stripped of this suffix now corresponds to a siglum in the witness list, then return it:
            if base_wit in self.witness_index_by_id:
                return base_wit
        # If we get here, then all possible manuscript suffixes have been stripped, and the resulting siglum does not correspond to a siglum in the witness list:
        return base_wit

    def get_readings_by_witness_for_unit(self, vu: VariationUnit):
        """Returns a dictionary mapping witness IDs to a list of their reading coefficients for a given variation unit.

        Args:
            vu: A VariationUnit to be processed.

        Returns:
            A dictionary mapping witness ID strings to a list of their coefficients for all substantive readings in this VariationUnit.
        """
        # In a first pass, populate lists of substantive (variation unit ID, reading ID) tuples and reading labels
        # and a map from reading IDs to the indices of their parent substantive reading in this unit:
        substantive_variation_unit_reading_tuples = []
        reading_id_to_index = {}
        for rdg in vu.readings:
            # If this reading is missing (e.g., lacunose or inapplicable due to an overlapping variant) or targets another reading, then skip it:
            if rdg.type in self.missing_reading_types or len(rdg.certainties) > 0:
                continue
            # If this reading is trivial, then map it to the last substantive index:
            if rdg.type in self.trivial_reading_types:
                reading_id_to_index[rdg.id] = len(substantive_variation_unit_reading_tuples) - 1
                continue
            # Otherwise, the reading is substantive: add it to the map and update the last substantive index:
            substantive_variation_unit_reading_tuples.append(tuple([vu.id, rdg.id]))
            reading_id_to_index[rdg.id] = len(substantive_variation_unit_reading_tuples) - 1
        # If the list of substantive readings only contains one entry, then this variation unit is not informative;
        # return an empty dictionary and add nothing to the list of substantive reading labels:
        if self.verbose:
            print(
                "Variation unit %s has %d substantive readings."
                % (vu.id, len(substantive_variation_unit_reading_tuples))
            )
        readings_by_witness_for_unit = {}
        if len(substantive_variation_unit_reading_tuples) <= 1:
            return readings_by_witness_for_unit
        # Otherwise, add these substantive reading ID tuples and labels to their corresponding list and initialize the output dictionary with empty sets for all base witnesses:
        for substantive_variation_unit_reading_tuple in substantive_variation_unit_reading_tuples:
            self.substantive_variation_unit_reading_tuples.append(substantive_variation_unit_reading_tuple)
        for wit in self.witnesses:
            readings_by_witness_for_unit[wit.id] = [0] * len(substantive_variation_unit_reading_tuples)
        # In a second pass, assign each base witness a set containing the readings it supports in this unit:
        for rdg in vu.readings:
            # Initialize the dictionary indicating support for this reading (or its disambiguations):
            rdg_support = [0] * len(substantive_variation_unit_reading_tuples)
            # If this is a missing reading (e.g., a lacuna or an overlap), then we can skip this reading, as its corresponding set will be empty:
            if rdg.type in self.missing_reading_types:
                continue
            # If this reading is trivial, then it will contain an entry for the index of its parent substantive reading:
            elif rdg.type in self.trivial_reading_types:
                rdg_support[reading_id_to_index[rdg.id]] += 1
            # If this reading has one or more target readings, then add an entry for each of those readings according to their certainty in this reading:
            elif len(rdg.certainties) > 0:
                for t in rdg.certainties:
                    # For overlaps, the target may be to a reading not included in this unit, so skip it if its ID is unrecognized:
                    if t in reading_id_to_index:
                        rdg_support[reading_id_to_index[t]] += rdg.certainties[t]
            # Otherwise, this reading is itself substantive; add an entry for the index of this reading:
            else:
                rdg_support[reading_id_to_index[rdg.id]] += 1
            # Proceed for each witness siglum in the support for this reading:
            for wit in rdg.wits:
                # Is this siglum a base siglum?
                base_wit = self.get_base_wit(wit)
                if base_wit not in self.witness_index_by_id:
                    # If it is not, then it is probably just because we've encountered a corrector or some other secondary witness not included in the witness list;
                    # report this if we're in verbose mode and move on:
                    if self.verbose:
                        print(
                            "Skipping unknown witness siglum %s (base siglum %s) in variation unit %s, reading %s..."
                            % (wit, base_wit, vu.id, rdg.id)
                        )
                    continue
                # If we've found a base siglum, then add this reading's contribution to the base witness's reading set for this unit;
                # normally the existing set will be empty, but if we reduce two suffixed sigla to the same base witness,
                # then that witness may attest to multiple readings in the same unit:
                readings_by_witness_for_unit[base_wit] = [
                    (readings_by_witness_for_unit[base_wit][i] + rdg_support[i]) for i in range(len(rdg_support))
                ]
        # In a third pass, normalize the reading weights for all non-lacunose readings:
        for wit in readings_by_witness_for_unit:
            rdg_support = readings_by_witness_for_unit[wit]
            norm = sum(rdg_support)
            # Skip lacunae, as we can't normalize the vector of reading weights:
            if norm == 0:
                continue
            for i in range(len(rdg_support)):
                rdg_support[i] = rdg_support[i] / norm
        return readings_by_witness_for_unit

    def parse_readings_by_witness(self):
        """Populates the internal dictionary mapping witness IDs to a list of their reading support sets for all variation units, and then fills the empty reading support sets for witnesses of type "corrector" with the entries of the previous witness."""
        if self.verbose:
            print("Populating internal dictionary of witness readings...")
        t0 = time.time()
        # Initialize the data structures to be populated here:
        self.readings_by_witness = {}
        self.substantive_variation_unit_ids = []
        for wit in self.witnesses:
            self.readings_by_witness[wit.id] = []
        # Populate them for each variation unit:
        for vu in self.variation_units:
            readings_by_witness_for_unit = self.get_readings_by_witness_for_unit(vu)
            if len(readings_by_witness_for_unit) > 0:
                self.substantive_variation_unit_ids.append(vu.id)
            for wit in readings_by_witness_for_unit:
                self.readings_by_witness[wit].append(readings_by_witness_for_unit[wit])
        # Optionally, fill the lacunae of the correctors:
        if self.fill_corrector_lacunae:
            for i, wit in enumerate(self.witnesses):
                # If this is the first witness, then it shouldn't be a corrector (since there is no previous witness against which to compare it):
                if i == 0:
                    continue
                # Otherwise, if this witness is not a corrector, then skip it:
                if wit.type != "corrector":
                    continue
                # Otherwise, retrieve the previous witness:
                prev_wit = self.witnesses[i - 1]
                for j in range(len(self.readings_by_witness[wit.id])):
                    # If the corrector has no reading, then set it to the previous witness's reading:
                    if sum(self.readings_by_witness[wit.id][j]) == 0:
                        self.readings_by_witness[wit.id][j] = self.readings_by_witness[prev_wit.id][j]
        t1 = time.time()
        if self.verbose:
            print(
                "Populated dictionary for %d witnesses over %d substantive variation units in %0.4fs."
                % (len(self.witnesses), len(self.substantive_variation_unit_ids), t1 - t0)
            )
        return

    def get_nexus_symbols(self):
        """Returns a list of one-character symbols needed to represent the states of all substantive readings in NEXUS.

        The number of symbols equals the maximum number of substantive readings at any variation unit.

        Returns:
            A list of individual characters representing states in readings.
        """
        # NOTE: PAUP* allows up to 64 symbols, but IQTREE does not appear to support symbols outside of 0-9 and a-z, and base symbols must be case-insensitive,
        # so we will settle for a maximum of 32 singleton symbols for now
        possible_symbols = list(string.digits) + list(string.ascii_lowercase)[:22]
        # The number of symbols needed is equal to the length of the longest substantive reading vector:
        nsymbols = 0
        # If there are no witnesses, then no symbols are needed at all:
        if len(self.witnesses) == 0:
            return []
        wit_id = self.witnesses[0].id
        for rdg_support in self.readings_by_witness[wit_id]:
            nsymbols = max(nsymbols, len(rdg_support))
        nexus_symbols = possible_symbols[:nsymbols]
        return nexus_symbols

    # def get_nexus_equates(self, nexus_symbols: List[str]):
    #     """Returns a list of one-character multiple-reading symbols for the NEXUS Equate block and a dictionary mapping multistate reading index lists to these symbols.

    #     Note that this will ignore any certainty degrees assigned to these states in the collation.

    #     Args:
    #         nexus_symbols: A list of nexus symbols for the singleton states.

    #     Returns:
    #         A dictionary mapping tuples of multiple reading indices to their corresponding symbols in the equate block.
    #     """
    #     # NOTE: EQUATE symbols are allowed to be case-sensitive, so we can use uppercase characters for these:
    #     possible_symbols = (
    #         list(string.ascii_uppercase)
    #     )
    #     # First, populate a set of all reading index tuples that we encounter in the collation:
    #     reading_ind_tuples_set = set()
    #     # If there are no witnesses, then no symbols are needed at all:
    #     if len(self.witnesses) == 0:
    #         return [], {}
    #     for wit in self.witnesses:
    #         for rdg_support in self.readings_by_witness[wit.id]:
    #             rdg_inds = [
    #                 i for i, w in enumerate(rdg_support) if w > 0
    #             ]  # the index list consists of the indices of all readings with any degree of certainty assigned to them
    #             if len(rdg_inds) > 1:
    #                 rdg_ind_tuple = tuple(rdg_inds)
    #                 reading_ind_tuples_set.add(rdg_ind_tuple)
    #     # Sort the reading index tuples in lexicographical order and map them to the remaining symbols:
    #     reading_ind_tuples = sorted(list(reading_ind_tuples_set))
    #     nexus_equates = possible_symbols[: len(reading_ind_tuples)]
    #     nexus_equate_mapping = {t: possible_symbols[i] for i, t in enumerate(reading_ind_tuples)}
    #     return nexus_equates, nexus_equate_mapping

    def to_nexus(
        self,
        file_addr: Union[Path, str],
        char_state_labels: bool = True,
        states_present: bool = False,
        ambiguous_as_missing: bool = False,
    ):
        """Writes this Collation to a NEXUS file with the given address.

        Args:
            file_addr: A string representing the path to an output NEXUS file; the file type should be .nex, .nexus, or .nxs.
            char_state_labels: An optional flag indicating whether or not to include the CharStateLabels block.
            states_present: An optional flag indicating whether to use the StatesFormat=StatesPresent setting
                instead of the StatesFormat=Frequency setting
                (and thus represent all states with single symbols rather than frequency vectors).
                Note that this setting will ignore any certainty degrees assigned to multiple ambiguous states in the collation.
            ambiguous_as_missing: An optional flag indicating whether to treat all ambiguous states as missing data.
                If this flag is set, then only base symbols will be generated for the NEXUS file.
                It is only applied if the states_present option is True.
        """
        # Start by calculating the values we will be using here:
        ntax = len(self.witnesses)
        nchar = (
            len(self.readings_by_witness[self.witnesses[0].id]) if ntax > 0 else 0
        )  # if the number of taxa is 0, then the number of characters is irrelevant
        taxlabels = [slugify(wit.id, lowercase=False, separator='_') for wit in self.witnesses]
        max_taxlabel_length = max(
            [len(taxlabel) for taxlabel in taxlabels]
        )  # keep track of the longest taxon label for tabular alignment purposes
        charlabels = [slugify(vu_id, lowercase=False, separator='_') for vu_id in self.substantive_variation_unit_ids]
        missing_symbol = '?'
        symbols = self.get_nexus_symbols()
        # equates, equate_mapping = [], {}
        # if states_present and not ambiguous_as_missing:
        #     equates, equate_mapping = self.get_nexus_equates(symbols)
        with open(file_addr, "w", encoding="utf-8") as f:
            # Start with the NEXUS header:
            f.write("#NEXUS\n\n")
            # Then begin the data block:
            f.write("Begin DATA;\n")
            # Write the collation matrix dimensions:
            f.write("\tDimensions ntax=%d nchar=%d;\n" % (ntax, nchar))
            # Write the format subblock:
            f.write("\tFormat\n")
            f.write("\t\tDataType=Standard\n")
            f.write("\t\tMissing=%s\n" % missing_symbol)
            if states_present:
                # There's no need to write StatesFormat=StatesPresent\n")
                f.write("\t\tSymbols=\"%s\";\n" % (" ".join(symbols)))
                # if not ambiguous_as_missing:
                #     f.write("\t\tEquate=\"")
                #     # Populate a reverse dictionary mapping the equate symbols to their reading index tuples:
                #     equate_to_symbols = {}
                #     for rdg_ind_tuple, e in equate_mapping.items():
                #         equate_to_symbols[e] = rdg_ind_tuple
                #     # Then for each symbol, write its mapping:
                #     for i, e in enumerate(equates):
                #         if i == 0:
                #             f.write("%s=(%s)" % (e, "".join([symbols[j] for j in equate_to_symbols[e]])))
                #         else:
                #             f.write(" %s=(%s)" % (e, "".join([symbols[j] for j in equate_to_symbols[e]])))
                #     f.write("\"\n")
            else:
                f.write("\t\tStatesFormat=Frequency\n")
                f.write("\t\tSymbols=\"%s\";\n" % (" ".join(symbols)))
            # If the char_state_labels is set, then write the labels for character-state labels, with each on its own line:
            if char_state_labels:
                f.write("\tCharStateLabels")
                substantive_variation_unit_ids_set = set(self.substantive_variation_unit_ids)
                substantive_variation_unit_reading_tuples_set = set(self.substantive_variation_unit_reading_tuples)
                vu_ind = 1
                for vu in self.variation_units:
                    if vu.id not in substantive_variation_unit_ids_set:
                        continue
                    if vu_ind == 1:
                        f.write("\n\t\t%d %s /" % (vu_ind, slugify(vu.id, lowercase=False, separator='_')))
                    else:
                        f.write(",\n\t\t%d %s /" % (vu_ind, slugify(vu.id, lowercase=False, separator='_')))
                    rdg_ind = 0
                    for rdg in vu.readings:
                        key = tuple([vu.id, rdg.id])
                        if key not in substantive_variation_unit_reading_tuples_set:
                            continue
                        ascii_rdg_text = slugify(
                            rdg.text, lowercase=False, separator='_', replacements=[['η', 'h'], ['ω', 'w']]
                        )
                        if ascii_rdg_text == "":
                            ascii_rdg_text = "om."
                        f.write(" %s" % ascii_rdg_text)
                        rdg_ind += 1
                    if rdg_ind > 0:
                        vu_ind += 1
                f.write(";\n")
            # Write the matrix subblock:
            f.write("\tMatrix")
            for i, wit in enumerate(self.witnesses):
                taxlabel = taxlabels[i]
                if states_present:
                    sequence = "\n\t\t" + taxlabel
                    # Add enough space after this label ensure that all sequences are nicely aligned:
                    sequence += " " * (max_taxlabel_length - len(taxlabel) + 1)
                    for rdg_support in self.readings_by_witness[wit.id]:
                        # If this reading is lacunose in this witness, then use the missing character:
                        if sum(rdg_support) == 0:
                            sequence += missing_symbol
                            continue
                        rdg_inds = [
                            i for i, w in enumerate(rdg_support) if w > 0
                        ]  # the index list consists of the indices of all readings with any degree of certainty assigned to them
                        # For singleton readings, just print the symbol:
                        if len(rdg_inds) == 1:
                            sequence += symbols[rdg_inds[0]]
                            continue
                        # For multiple readings, print the corresponding equate symbol or the missing symbol depending on input settings:
                        if ambiguous_as_missing:
                            sequence += missing_symbol
                        else:
                            sequence += "{%s}" % "".join([str(rdg_ind) for rdg_ind in rdg_inds])
                else:
                    sequence = "\n\t\t" + taxlabel
                    for rdg_support in self.readings_by_witness[wit.id]:
                        sequence += "\n\t\t\t"
                        # If this reading is lacunose in this witness, then use the missing character:
                        if sum(rdg_support) == 0:
                            sequence += missing_symbol
                            continue
                        # Otherwise, print out its frequencies for different readings in parentheses:
                        sequence += "("
                        for j, w in enumerate(rdg_support):
                            sequence += "%s:%0.4f" % (symbols[j], w)
                            if j < len(rdg_support) - 1:
                                sequence += " "
                        sequence += ")"
                f.write("%s" % (sequence))
            f.write(";\n")
            # End the characters block:
            f.write("End;")
        return

    def get_hennig86_symbols(self):
        """Returns a list of one-character symbols needed to represent the states of all substantive readings in Hennig86 format.

        The number of symbols equals the maximum number of substantive readings at any variation unit.

        Returns:
            A list of individual characters representing states in readings.
        """
        possible_symbols = (
            list(string.digits) + list(string.ascii_uppercase)[:22]
        )  # NOTE: the maximum number of symbols allowed in Hennig86 format is 32
        # The number of symbols needed is equal to the length of the longest substantive reading vector:
        nsymbols = 0
        # If there are no witnesses, then no symbols are needed at all:
        if len(self.witnesses) == 0:
            return []
        wit_id = self.witnesses[0].id
        for rdg_support in self.readings_by_witness[wit_id]:
            nsymbols = max(nsymbols, len(rdg_support))
        hennig86_symbols = possible_symbols[:nsymbols]
        return hennig86_symbols

    def to_hennig86(self, file_addr: Union[Path, str]):
        """Writes this Collation to a file in Hennig86 format with the given address.
        Note that because Hennig86 format does not support NEXUS-style ambiguities, such ambiguities will be treated as missing data.

        Args:
            file_addr: A string representing the path to an output file.
        """
        # Start by calculating the values we will be using here:
        ntax = len(self.witnesses)
        nchar = (
            len(self.readings_by_witness[self.witnesses[0].id]) if ntax > 0 else 0
        )  # if the number of taxa is 0, then the number of characters is irrelevant
        taxlabels = []
        for wit in self.witnesses:
            taxlabel = wit.id
            # Hennig86 format requires taxon names to start with a letter, so if this is not the case, then append "WIT_" to the start of the name:
            if taxlabel[0] not in string.ascii_letters:
                taxlabel = "WIT_" + taxlabel
            # Then replace any disallowed characters in the string with an underscore:
            taxlabel = slugify(taxlabel, lowercase=False, separator='_')
            taxlabels.append(taxlabel)
        max_taxlabel_length = max(
            [len(taxlabel) for taxlabel in taxlabels]
        )  # keep track of the longest taxon label for tabular alignment purposes
        missing_symbol = '?'
        symbols = self.get_hennig86_symbols()
        with open(file_addr, "w", encoding="utf-8") as f:
            # Start with the nstates header:
            f.write("nstates %d;\n" % len(symbols))
            # Then begin the xread block:
            f.write("xread\n")
            # Write the dimensions:
            f.write("%d %d\n" % (nchar, ntax))
            # Now write the matrix:
            for i, wit in enumerate(self.witnesses):
                taxlabel = taxlabels[i]
                # Add enough space after this label ensure that all sequences are nicely aligned:
                sequence = taxlabel + (" " * (max_taxlabel_length - len(taxlabel) + 1))
                for rdg_support in self.readings_by_witness[wit.id]:
                    # If this reading is lacunose in this witness, then use the missing character:
                    if sum(rdg_support) == 0:
                        sequence += missing_symbol
                        continue
                    rdg_inds = [
                        i for i, w in enumerate(rdg_support) if w > 0
                    ]  # the index list consists of the indices of all readings with any degree of certainty assigned to them
                    # For singleton readings, just print the symbol:
                    if len(rdg_inds) == 1:
                        sequence += symbols[rdg_inds[0]]
                        continue
                    # For multiple readings, print the missing symbol:
                    sequence += missing_symbol
                f.write("%s\n" % (sequence))
            f.write(";")
        return

    def get_phylip_symbols(self):
        """Returns a list of one-character symbols needed to represent the states of all substantive readings in PHYLIP format.

        The number of symbols equals the maximum number of substantive readings at any variation unit.

        Returns:
            A list of individual characters representing states in readings.
        """
        possible_symbols = [
            "A",
            "C",
            "D",
            "E",
            "F",
            "G",
            "H",
            "I",
            "K",
            "L",
            "M",
            "N",
            "P",
            "Q",
            "R",
            "S",
            "T",
            "V",
            "W",
            "Y",
        ]  # NOTE: the maximum number of symbols allowed in PHYLIP format is 20, corresponding to the number of unambiguous amino acids
        # The number of symbols needed is equal to the length of the longest substantive reading vector:
        nsymbols = 0
        # If there are no witnesses, then no symbols are needed at all:
        if len(self.witnesses) == 0:
            return []
        wit_id = self.witnesses[0].id
        for rdg_support in self.readings_by_witness[wit_id]:
            nsymbols = max(nsymbols, len(rdg_support))
        phylip_symbols = possible_symbols[:nsymbols]
        return phylip_symbols

    def to_phylip(self, file_addr: Union[Path, str]):
        """Writes this Collation to a file in PHYLIP format with the given address.
        Note that because PHYLIP format does not support NEXUS-style ambiguities, such ambiguities will be treated as missing data.

        Args:
            file_addr: A string representing the path to an output file.
        """
        # Start by calculating the values we will be using here:
        ntax = len(self.witnesses)
        nchar = (
            len(self.readings_by_witness[self.witnesses[0].id]) if ntax > 0 else 0
        )  # if the number of taxa is 0, then the number of characters is irrelevant
        taxlabels = []
        for wit in self.witnesses:
            taxlabel = wit.id
            # Then replace any disallowed characters in the string with an underscore:
            taxlabel = slugify(taxlabel, lowercase=False, separator='_')
            taxlabels.append(taxlabel)
        max_taxlabel_length = max(
            [len(taxlabel) for taxlabel in taxlabels]
        )  # keep track of the longest taxon label for tabular alignment purposes
        # If the longest taxon label exceeds 10, then warn the user, as this may result in an unreadable file in some programs:
        if max_taxlabel_length > 10:
            print(
                "WARNING: One or more taxon labels are longer than 10 characters. They will be printed as they are, but some programs may not be able to read the alignment file. Consider modifying the taxon names in the output file."
            )
        missing_symbol = '?'
        symbols = self.get_phylip_symbols()
        with open(file_addr, "w", encoding="ascii") as f:
            # Write the dimensions:
            f.write("%d %d\n" % (nchar, ntax))
            # Now write the matrix:
            for i, wit in enumerate(self.witnesses):
                taxlabel = taxlabels[i]
                # Add enough space after this label ensure that all sequences are nicely aligned:
                sequence = taxlabel + (" " * (max_taxlabel_length - len(taxlabel) + 1))
                for rdg_support in self.readings_by_witness[wit.id]:
                    # If this reading is lacunose in this witness, then use the missing character:
                    if sum(rdg_support) == 0:
                        sequence += missing_symbol
                        continue
                    rdg_inds = [
                        i for i, w in enumerate(rdg_support) if w > 0
                    ]  # the index list consists of the indices of all readings with any degree of certainty assigned to them
                    # For singleton readings, just print the symbol:
                    if len(rdg_inds) == 1:
                        sequence += symbols[rdg_inds[0]]
                        continue
                    # For multiple readings, print the missing symbol:
                    sequence += missing_symbol
                f.write("%s\n" % (sequence))
        return

    def get_fasta_symbols(self):
        """Returns a list of one-character symbols needed to represent the states of all substantive readings in FASTA format.

        The number of symbols equals the maximum number of substantive readings at any variation unit.

        Returns:
            A list of individual characters representing states in readings.
        """
        possible_symbols = (
            list(string.digits) + list(string.ascii_lowercase)[:22]
        )  # NOTE: for RAxML, multistate characters with an alphabet sizes up to 32 are supported
        # The number of symbols needed is equal to the length of the longest substantive reading vector:
        nsymbols = 0
        # If there are no witnesses, then no symbols are needed at all:
        if len(self.witnesses) == 0:
            return []
        wit_id = self.witnesses[0].id
        for rdg_support in self.readings_by_witness[wit_id]:
            nsymbols = max(nsymbols, len(rdg_support))
        fasta_symbols = possible_symbols[:nsymbols]
        return fasta_symbols

    def to_fasta(self, file_addr: Union[Path, str]):
        """Writes this Collation to a file in FASTA format with the given address.
        Note that because FASTA format does not support NEXUS-style ambiguities, such ambiguities will be treated as missing data.

        Args:
            file_addr: A string representing the path to an output file.
        """
        # Start by calculating the values we will be using here:
        ntax = len(self.witnesses)
        nchar = (
            len(self.readings_by_witness[self.witnesses[0].id]) if ntax > 0 else 0
        )  # if the number of taxa is 0, then the number of characters is irrelevant
        taxlabels = []
        for wit in self.witnesses:
            taxlabel = wit.id
            # Then replace any disallowed characters in the string with an underscore:
            taxlabel = slugify(taxlabel, lowercase=False, separator='_')
            taxlabels.append(taxlabel)
        max_taxlabel_length = max(
            [len(taxlabel) for taxlabel in taxlabels]
        )  # keep track of the longest taxon label for tabular alignment purposes
        missing_symbol = '?'
        symbols = self.get_fasta_symbols()
        with open(file_addr, "w", encoding="ascii") as f:
            # Now write the matrix:
            for i, wit in enumerate(self.witnesses):
                taxlabel = taxlabels[i]
                # Add enough space after this label ensure that all sequences are nicely aligned:
                sequence = ">%s\n" % taxlabel
                for rdg_support in self.readings_by_witness[wit.id]:
                    # If this reading is lacunose in this witness, then use the missing character:
                    if sum(rdg_support) == 0:
                        sequence += missing_symbol
                        continue
                    rdg_inds = [
                        i for i, w in enumerate(rdg_support) if w > 0
                    ]  # the index list consists of the indices of all readings with any degree of certainty assigned to them
                    # For singleton readings, just print the symbol:
                    if len(rdg_inds) == 1:
                        sequence += symbols[rdg_inds[0]]
                        continue
                    # For multiple readings, print the missing symbol:
                    sequence += missing_symbol
                f.write("%s\n" % (sequence))
        return

    def to_numpy(self, split_missing: bool = True):
        """Returns this Collation in the form of a NumPy array, along with arrays of its row and column labels.

        Args:
            split_missing: An optional flag indicating whether or not to treat missing characters/variation units as having a contribution of 1 split over all states/readings; if False, then missing data is ignored (i.e., all states are 0). Default value is True.

        Returns:
            A NumPy array with a row for each substantive reading and a column for each witness.
            A list of substantive reading ID strings.
            A list of witness ID strings.
        """
        # Initialize the output array with the appropriate dimensions:
        reading_labels = []
        substantive_variation_unit_ids_set = set(self.substantive_variation_unit_ids)
        substantive_variation_unit_reading_tuples_set = set(self.substantive_variation_unit_reading_tuples)
        for vu in self.variation_units:
            if vu.id not in substantive_variation_unit_ids_set:
                continue
            for rdg in vu.readings:
                key = tuple([vu.id, rdg.id])
                if key in substantive_variation_unit_reading_tuples_set:
                    reading_labels.append(vu.id + ", " + rdg.text)
        witness_labels = [wit.id for wit in self.witnesses]
        matrix = np.zeros((len(reading_labels), len(witness_labels)), dtype=float)
        # Then populate it with the appropriate values:
        for col_ind, wit_id in enumerate(witness_labels):
            row_ind = 0
            for rdg_support in self.readings_by_witness[wit_id]:
                # If this reading support vector sums to 0, then this is missing data; handle it as specified:
                if sum(rdg_support) == 0:
                    if split_missing:
                        for i in range(len(rdg_support)):
                            matrix[row_ind, col_ind] = 1 / len(rdg_support)
                            row_ind += 1
                    else:
                        row_ind += len(rdg_support)
                # Otherwise, adds its coefficients normally:
                else:
                    for i in range(len(rdg_support)):
                        matrix[row_ind, col_ind] = rdg_support[i]
                        row_ind += 1
        return matrix, reading_labels, witness_labels

    def to_distance_matrix(self, proportion=False):
        """Transforms this Collation into a NumPy distance matrix between witnesses, along with an array of its labels for the witnesses.
        Distances can be computed either as counts of disagreements (the default setting), or as proportions of disagreements over all variation units where both witnesses have singleton readings.

        Args:
            proportion: An optional flag indicating whether or not to calculate distances as proportions over extant, unambiguous variation units.

        Returns:
            A NumPy distance matrix with a row and column for each witness.
            A list of witness ID strings.
        """
        # Initialize the output array with the appropriate dimensions:
        witness_labels = [wit.id for wit in self.witnesses]
        matrix = np.zeros((len(witness_labels), len(witness_labels)), dtype=float)
        for i, wit_1 in enumerate(witness_labels):
            for j, wit_2 in enumerate(witness_labels):
                extant_units = 0
                disagreements = 0
                # If both witnesses are the same, then the matrix entry is trivially 0:
                if j == i:
                    matrix[i, j] = 0
                    continue
                # If either of the cells for this pair of witnesses has been populated already, then just copy the distance without recalculating:
                if i > j:
                    matrix[i, j] = matrix[j, i]
                    continue
                for vu_ind in range(len(self.substantive_variation_unit_ids)):
                    wit_1_rdg_support = self.readings_by_witness[wit_1][vu_ind]
                    wit_2_rdg_support = self.readings_by_witness[wit_2][vu_ind]
                    wit_1_rdg_inds = [k for k, w in enumerate(wit_1_rdg_support) if w > 0]
                    wit_2_rdg_inds = [k for k, w in enumerate(wit_2_rdg_support) if w > 0]
                    if len(wit_1_rdg_inds) != 1 or len(wit_2_rdg_inds) != 1:
                        continue
                    extant_units += 1
                    if wit_1_rdg_inds[0] != wit_2_rdg_inds[0]:
                        disagreements += 1
                if proportion:
                    matrix[i, j] = disagreements / max(
                        extant_units, 1
                    )  # the max in the denominator is to prevent division by 0; the distance entry will be 0 if the two witnesses have no overlap
                else:
                    matrix[i, j] = disagreements
        return matrix, witness_labels

    def to_dataframe(self, split_missing: bool = True):
        """Returns this Collation in the form of a Pandas DataFrame array, including the appropriate row and column labels.

        Args:
            split_missing: An optional flag indicating whether or not to treat missing characters/variation units as having a contribution of 1 split over all states/readings; if False, then missing data is ignored (i.e., all states are 0). Default value is True.

        Returns:
            A Pandas DataFrame with a row for each substantive reading and a column for each witness.
        """
        # Convert the collation to a NumPy array and get its row and column labels first:
        matrix, reading_labels, witness_labels = self.to_numpy(split_missing)
        df = pd.DataFrame(matrix, index=reading_labels, columns=witness_labels)
        return df

    def to_csv(self, file_addr: Union[Path, str], split_missing: bool = True, **kwargs):
        """Writes this Collation to a comma-separated value (CSV) file with the given address.

        If your witness IDs are numeric (e.g., Gregory-Aland numbers), then they will be written in full to the CSV file, but Excel will likely interpret them as numbers and truncate any leading zeroes!

        Args:
            file_addr: A string representing the path to an output CSV file; the file type should be .csv.
            split_missing: An optional flag indicating whether or not to treat missing characters/variation units as having a contribution of 1 split over all states/readings; if False, then missing data is ignored (i.e., all states are 0). Default value is True.
            **kwargs: Keyword arguments for pandas.DataFrame.to_csv.
        """
        # Convert the collation to a Pandas DataFrame first:
        df = self.to_dataframe(split_missing)
        return df.to_csv(file_addr, encoding="utf-8", **kwargs)

    def to_excel(self, file_addr: Union[Path, str], split_missing: bool = True):
        """Writes this Collation to an Excel (.xlsx) file with the given address.

        Since Pandas is deprecating its support for xlwt, specifying an output in old Excel (.xls) output is not recommended.

        Args:
            file_addr: A string representing the path to an output Excel file; the file type should be .xlsx.
            split_missing: An optional flag indicating whether or not to treat missing characters/variation units as having a contribution of 1 split over all states/readings; if False, then missing data is ignored (i.e., all states are 0). Default value is True.
        """
        # Convert the collation to a Pandas DataFrame first:
        df = self.to_dataframe(split_missing)
        return df.to_excel(file_addr)

    def to_stemma(self, file_addr: Union[Path, str]):
        """Writes this Collation to a STEMMA file without an extension and a Chron file (containing low, middle, and high dates for all witnesses) without an extension.

        Since this format does not support ambiguous states, all reading vectors with anything other than one nonzero entry will be interpreted as lacunose.

        Args:
            file_addr: A string representing the path to an output STEMMA prep file; the file should have no extension.
            The accompanying chron file will match this file name, except that it will have "_chron" appended to the end.
        """
        # In a first pass, populate a dictionary mapping (variation unit index, reading index) tuples from the readings_by_witness dictionary
        # to the readings' texts:
        reading_texts_by_indices = {}
        substantive_variation_unit_ids_set = set(self.substantive_variation_unit_ids)
        substantive_variation_unit_reading_tuples_set = set(self.substantive_variation_unit_reading_tuples)
        vu_ind = 0
        for vu in self.variation_units:
            if vu.id not in substantive_variation_unit_ids_set:
                continue
            rdg_ind = 0
            for rdg in vu.readings:
                key = tuple([vu.id, rdg.id])
                if key not in substantive_variation_unit_reading_tuples_set:
                    continue
                indices = tuple([vu_ind, rdg_ind])
                reading_texts_by_indices[indices] = rdg.text
                rdg_ind += 1
            if rdg_ind > 0:
                vu_ind += 1
        # In a second pass, populate another dictionary mapping (variation unit index, reading index) tuples from the readings_by_witness dictionary
        # to the witnesses exclusively supporting those readings:
        reading_wits_by_indices = {}
        for indices in reading_texts_by_indices:
            reading_wits_by_indices[indices] = []
        for wit in self.readings_by_witness:
            for vu_ind, rdg_support in enumerate(self.readings_by_witness[wit]):
                # If this witness does not exclusively support exactly one reading at this unit, then treat it as lacunose:
                if len([i for i, w in enumerate(rdg_support) if w > 0]) != 1:
                    continue
                rdg_ind = rdg_support.index(1)
                indices = tuple([vu_ind, rdg_ind])
                reading_wits_by_indices[indices].append(wit)
        # In a third pass, write to the STEMMA file:
        chron_file_addr = str(file_addr) + "_chron"
        with open(file_addr, "w", encoding="utf-8") as f:
            # Start with the witness list:
            f.write("* %s ;\n\n" % " ".join([wit.id for wit in self.witnesses]))
            f.write("^ %s\n\n" % chron_file_addr)
            # Then add a line indicating that all witnesses are lacunose unless they are specified explicitly:
            f.write("= $? $* ;\n\n")
            # Then proceed for each variation unit:
            for vu_ind, vu_id in enumerate(self.substantive_variation_unit_ids):
                # Print the variation unit ID first:
                f.write("@ %s\n" % vu_id)
                # In a first pass, print the texts of all readings enclosed in brackets:
                f.write("[ ")
                rdg_ind = 0
                while True:
                    indices = tuple([vu_ind, rdg_ind])
                    if indices not in reading_texts_by_indices:
                        break
                    text = slugify(
                        reading_texts_by_indices[indices], lowercase=False, allow_unicode=True, separator='.'
                    )
                    # Denote omissions by en-dashes:
                    if text == "":
                        text = "\u2013"
                    # The first reading should not be preceded by anything:
                    if rdg_ind == 0:
                        f.write(text)
                        f.write(" |")
                    # Every subsequent reading should be preceded by a space:
                    elif rdg_ind > 0:
                        f.write(" %s" % text)
                    rdg_ind += 1
                f.write(" ]\n")
                # In a second pass, print the indices and witnesses for all readings enclosed in angle brackets:
                rdg_ind = 0
                f.write("\t< ")
                while True:
                    indices = tuple([vu_ind, rdg_ind])
                    if indices not in reading_wits_by_indices:
                        break
                    wits = " ".join(reading_wits_by_indices[indices])
                    # Open the variant reading support block with an angle bracket:
                    if rdg_ind == 0:
                        f.write("%d %s" % (rdg_ind, wits))
                    # Open all subsequent variant reading support blocks with pipes on the next line:
                    else:
                        f.write("\n\t| %d %s" % (rdg_ind, wits))
                    rdg_ind += 1
                f.write(" >\n")
        # In a fourth pass, write to the chron file:
        max_id_length = max(
            [len(slugify(wit.id, lowercase=False, allow_unicode=True, separator='_')) for wit in self.witnesses]
        )
        max_date_length = 0
        for wit in self.witnesses:
            if wit.date_range[0] is not None:
                max_date_length = max(max_date_length, len(str(wit.date_range[0])))
            if wit.date_range[1] is not None:
                max_date_length = max(max_date_length, len(str(wit.date_range[1])))
        # Attempt to get the minimum and maximum dates for witnesses; if we can't do this, then don't write a chron file:
        min_date = None
        max_date = None
        try:
            min_date = min([wit.date_range[0] for wit in self.witnesses if wit.date_range[0] is not None])
            max_date = max([wit.date_range[1] for wit in self.witnesses if wit.date_range[1] is not None])
        except Exception as e:
            print("WARNING: no witnesses have date ranges; no chron file will be written!")
            return
        with open(chron_file_addr, "w", encoding="utf-8") as f:
            for wit in self.witnesses:
                wit_label = slugify(wit.id, lowercase=False, allow_unicode=True, separator='_')
                f.write(wit_label)
                f.write(" " * (max_id_length - len(wit.id) + 1))
                # If this witness's date range is empty, then use the min and max dates over all witnesses as a default date range:
                date_range = wit.date_range
                if date_range[0] is None and date_range[1] is None:
                    date_range = tuple([min_date, max_date])
                # Then write the date range minimum, average, and maximum to the chron file:
                low_date = str(date_range[0])
                f.write(" " * (max_date_length - len(low_date) + 2))
                f.write(low_date)
                avg_date = str(int(((date_range[0] + date_range[1]) / 2)))
                f.write(" " * (max_date_length - len(str(avg_date)) + 2))
                f.write(avg_date)
                high_date = str(date_range[1])
                f.write(" " * (max_date_length - len(high_date) + 2))
                f.write(high_date)
                f.write("\n")
        return

    def to_file(
        self,
        file_addr: Union[Path, str],
        format: Format = None,
        split_missing: bool = True,
        char_state_labels: bool = True,
        states_present: bool = False,
        ambiguous_as_missing: bool = False,
    ):
        """Writes this Collation to the file with the given address.

        Args:
            file_addr (Union[Path, str]): The path to the output file.
            format (Format, optional): The desired output format.
                If None then it is infered from the file suffix.
                Defaults to None.
            split_missing (bool, optional): An optional flag indicating whether to treat
                missing characters/variation units as having a contribution of 1 split over all states/readings;
                if False, then missing data is ignored (i.e., all states are 0).
                Not applicable for NEXUS, HENNIG86, PHYLIP, FASTA, or STEMMA format.
                Default value is True.
            char_state_labels (bool, optional): An optional flag indicating whether to print
                the CharStateLabels block in NEXUS output.
                Default value is True.
            states_present (bool, optional): An optional flag indicating whether to use the StatesFormat=StatesPresent setting
                instead of the StatesFormat=Frequency setting
                (and thus represent all states with single symbols rather than frequency vectors)
                in NEXUS output.
                Note that this setting will ignore any certainty degrees assigned to multiple ambiguous states in the collation.
                Default value is False.
            ambiguous_as_missing (bool, optional): An optional flag indicating whether to treat all ambiguous states as missing data.
                If this flag is set, then only base symbols will be generated for the NEXUS file.
                It is only applied if the states_present option is True.
        """
        file_addr = Path(file_addr)
        format = format or Format.infer(
            file_addr.suffix
        )  # an exception will be raised here if the format or suffix is invalid

        if format == Format.NEXUS:
            return self.to_nexus(
                file_addr,
                char_state_labels=char_state_labels,
                states_present=states_present,
                ambiguous_as_missing=ambiguous_as_missing,
            )

        if format == format.HENNIG86:
            return self.to_hennig86(file_addr)

        if format == format.PHYLIP:
            return self.to_phylip(file_addr)

        if format == format.FASTA:
            return self.to_fasta(file_addr)

        if format == Format.CSV:
            return self.to_csv(file_addr, split_missing=split_missing)

        if format == Format.TSV:
            return self.to_csv(file_addr, split_missing=split_missing, sep="\t")

        if format == Format.EXCEL:
            return self.to_excel(file_addr, split_missing=split_missing)

        if format == Format.STEMMA:
            return self.to_stemma(file_addr)
