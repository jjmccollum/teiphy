#!/usr/bin/env python3

from enum import Enum
from typing import List, Union
from pathlib import os, Path
from datetime import datetime  # for calculating the current year (for dating and tree height purposes)
import time  # to time calculations for users
import string  # for easy retrieval of character ranges
from lxml import etree as et  # for reading TEI XML inputs
import numpy as np  # for random number sampling and collation matrix outputs
import pandas as pd  # for writing to DataFrames, CSV, Excel, etc.
from slugify import slugify  # for converting Unicode text from readings to ASCII for NEXUS
from jinja2 import Environment, PackageLoader, select_autoescape  # for filling output XML templates

from .common import xml_ns, tei_ns
from .format import Format
from .witness import Witness
from .variation_unit import VariationUnit


class ParsingException(Exception):
    pass


class WitnessDateException(Exception):
    pass


class IntrinsicRelationsException(Exception):
    pass


class ClockModel(str, Enum):
    strict = "strict"
    uncorrelated = "uncorrelated"
    local = "local"


class AncestralLogger(str, Enum):
    state = "state"
    sequence = "sequence"
    none = "none"


class TableType(str, Enum):
    matrix = "matrix"
    distance = "distance"
    similarity = "similarity"
    nexus = "nexus"
    long = "long"


class Collation:
    """Base class for storing TEI XML collation data internally.

    This corresponds to the entire XML tree, rooted at the TEI element of the collation.

    Attributes:
        manuscript_suffixes: A list of suffixes used to distinguish manuscript subwitnesses like first hands, correctors, main texts, alternate texts, and multiple attestations from their base witnesses.
        trivial_reading_types: A set of reading types (e.g., "reconstructed", "defective", "orthographic", "subreading") whose readings should be collapsed under the previous substantive reading.
        missing_reading_types: A set of reading types (e.g., "lac", "overlap") whose readings should be treated as missing data.
        fill_corrector_lacunae: A boolean flag indicating whether or not to fill "lacunae" in witnesses with type "corrector".
        fragmentary_threshold: A float representing the proportion such that all witnesses extant at fewer than this proportion of variation units are filtered out of the collation.
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
        fragmentary_threshold: float = None,
        dates_file: Union[Path, str] = None,
        verbose: bool = False,
    ):
        """Constructs a new Collation instance with the given settings.

        Args:
            xml: An lxml.etree.ElementTree representing an XML tree rooted at a TEI element.
            manuscript_suffixes: An optional list of suffixes used to distinguish manuscript subwitnesses like first hands, correctors, main texts, alternate texts, and multiple attestations from their base witnesses.
            trivial_reading_types: An optional set of reading types (e.g., "reconstructed", "defective", "orthographic", "subreading") whose readings should be collapsed under the previous substantive reading.
            missing_reading_types: An optional set of reading types (e.g., "lac", "overlap") whose readings should be treated as missing data.
            fill_corrector_lacunae: An optional flag indicating whether or not to fill "lacunae" in witnesses with type "corrector".
            fragmentary_threshold: An optional float representing the proportion such that all witnesses extant at fewer than this proportion of variation units are filtered out of the collation.
            dates_file: An optional path to a CSV file containing witness IDs, minimum dates, and maximum dates. If specified, then for all witnesses in the first column, any existing date ranges for them in the TEI XML collation will be ignored.
            verbose: An optional flag indicating whether or not to print timing and debugging details for the user.
        """
        self.manuscript_suffixes = manuscript_suffixes
        self.trivial_reading_types = set(trivial_reading_types)
        self.missing_reading_types = set(missing_reading_types)
        self.fill_corrector_lacunae = fill_corrector_lacunae
        self.fragmentary_threshold = fragmentary_threshold
        self.verbose = verbose
        self.witnesses = []
        self.witness_index_by_id = {}
        self.variation_units = []
        self.readings_by_witness = {}
        self.variation_unit_ids = []
        self.substantive_variation_unit_reading_tuples = []
        self.substantive_readings_by_variation_unit_id = {}
        self.intrinsic_categories = []
        self.intrinsic_odds_by_id = {}
        self.transcriptional_categories = []
        self.transcriptional_rates_by_id = {}
        self.origin_date_range = []
        # Now parse the XML tree to populate these data structures:
        if self.verbose:
            print("Initializing collation...")
        t0 = time.time()
        self.parse_origin_date_range(xml)
        self.parse_list_wit(xml)
        self.validate_wits(xml)
        # If a dates file was specified, then update the witness date ranges manually:
        if dates_file is not None:
            self.update_witness_date_ranges_from_dates_file(dates_file)
        # If the upper bound on a work's date of origin is not defined, then attempt to assign it an upper bound based on the witness dates;
        # otherwise, attempt to assign lower bounds to witness dates based on it:
        if self.origin_date_range[1] is None:
            self.update_origin_date_range_from_witness_date_ranges()
        else:
            self.update_witness_date_ranges_from_origin_date_range()
        self.parse_intrinsic_odds(xml)
        self.parse_transcriptional_rates(xml)
        self.parse_apps(xml)
        self.validate_intrinsic_relations()
        self.parse_readings_by_witness()
        # If a threshold of readings for fragmentary witnesses is specified, then filter the witness list using the dictionary mapping witness IDs to readings:
        if self.fragmentary_threshold is not None:
            self.filter_fragmentary_witnesses(xml)
        t1 = time.time()
        if self.verbose:
            print("Total time to initialize collation: %0.4fs." % (t1 - t0))

    def parse_origin_date_range(self, xml: et.ElementTree):
        """Given an XML tree for a collation, populates this Collation's list of origin date bounds.

        Args:
            xml: An lxml.etree.ElementTree representing an XML tree rooted at a TEI element.
        """
        if self.verbose:
            print("Parsing origin date range...")
        t0 = time.time()
        self.origin_date_range = [None, None]
        for date in xml.xpath(
            "//tei:sourceDesc//tei:bibl//tei:date|//tei:sourceDesc//tei:biblStruct//tei:date|//tei:sourceDesc//tei:biblFull//tei:date",
            namespaces={"tei": tei_ns},
        ):
            # Try the @when attribute first; if it is set, then it accounts for both ends of the date range:
            if date.get("when") is not None:
                self.origin_date_range[0] = int(date.get("when").split("-")[0])
                self.origin_date_range[1] = self.origin_date_range[0]
            # Failing that, if it has @from and @to attributes (indicating the period over which the work was completed),
            # then the completion date of the work accounts for both ends of the date range:
            elif date.get("to") is not None:
                self.origin_date_range[0] = int(date.get("to").split("-")[0])
                self.origin_date_range[1] = self.origin_date_range[0]
            # Failing that, set lower and upper bounds on the origin date using the the @notBefore and @notAfter attributes:
            elif date.get("notBefore") is not None or date.get("notAfter") is not None:
                if date.get("notBefore") is not None:
                    self.origin_date_range[0] = int(date.get("notBefore").split("-")[0])
                if date.get("notAfter") is not None:
                    self.origin_date_range[1] = int(date.get("notAfter").split("-")[0])
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

    def parse_list_wit(self, xml: et.ElementTree):
        """Given an XML tree for a collation, populates its list of witnesses from its listWit element.
        If the XML tree does not contain a listWit element, then a ParsingException is thrown listing all distinct witness sigla encountered in the collation.

        Args:
            xml: An lxml.etree.ElementTree representing an XML tree rooted at a TEI element.
        """
        if self.verbose:
            print("Parsing witness list...")
        t0 = time.time()
        self.witnesses = []
        self.witness_index_by_id = {}
        list_wits = xml.xpath("/tei:TEI//tei:listWit", namespaces={"tei": tei_ns})
        if len(list_wits) == 0:
            # There is no listWit element: collect all distinct witness sigla in the collation and raise a ParsingException listing them:
            distinct_sigla = set()
            sigla = []
            # Proceed for each rdg, rdgGrp, or witDetail element:
            for rdg in xml.xpath("//tei:rdg|//tei:rdgGrp|//tei:witDetail", namespaces={"tei": tei_ns}):
                wit_str = rdg.get("wit") if rdg.get("wit") is not None else ""
                wits = wit_str.split()
                for wit in wits:
                    siglum = wit.strip("#")  # remove the URI prefix, if there is one
                    if siglum not in distinct_sigla:
                        distinct_sigla.add(siglum)
                        sigla.append(siglum)
            sigla.sort()
            msg = ""
            msg += "An explicit listWit element must be included in the TEI XML collation.\n"
            msg += "The following sigla occur in the collation and should be included as the @xml:id or @n attributes of witness elements under the listWit element:\n"
            msg += ", ".join(sigla)
            raise ParsingException(msg)
        # Otherwise, take the first listWit element as the list of all witnesses and process it:
        list_wit = list_wits[0]
        for witness in list_wit.xpath("./tei:witness", namespaces={"tei": tei_ns}):
            wit = Witness(witness, self.verbose)
            self.witness_index_by_id[wit.id] = len(self.witnesses)
            self.witnesses.append(wit)
        t1 = time.time()
        if self.verbose:
            print("Finished processing %d witnesses in %0.4fs." % (len(self.witnesses), t1 - t0))
        return

    def validate_wits(self, xml: et.ElementTree):
        """Given an XML tree for a collation, checks if any witness sigla listed in a rdg, rdgGrp, or witDetail element,
        once stripped of ignored suffixes, is not found in the witness list.
        A warning will be issued for each distinct siglum like this.
        This method also checks if the upper bound of any witness's date is earlier than the lower bound on the collated work's date of origin
        and throws an exception if so.

        Args:
            xml: An lxml.etree.ElementTree representing an XML tree rooted at a TEI element.
        """
        if self.verbose:
            print("Validating witness list against collation...")
        t0 = time.time()
        # There is no listWit element: collect all distinct witness sigla in the collation and raise an exception listing them:
        distinct_extra_sigla = set()
        extra_sigla = []
        # Proceed for each rdg, rdgGrp, or witDetail element:
        for rdg in xml.xpath("//tei:rdg|//tei:rdgGrp|//tei:witDetail", namespaces={"tei": tei_ns}):
            wit_str = rdg.get("wit") if rdg.get("wit") is not None else ""
            wits = wit_str.split()
            for wit in wits:
                siglum = wit.strip("#")  # remove the URI prefix, if there is one
                base_siglum = self.get_base_wit(siglum)
                if base_siglum not in self.witness_index_by_id:
                    if base_siglum not in distinct_extra_sigla:
                        distinct_extra_sigla.add(base_siglum)
                        extra_sigla.append(base_siglum)
        if len(extra_sigla) > 0:
            extra_sigla.sort()
            msg = ""
            msg += "WARNING: The following sigla occur in the collation that do not have corresponding witness entries in the listWit:\n"
            msg += ", ".join(extra_sigla)
            print(msg)
        # If the lower bound on the date of origin is defined, then check each witness against it:
        if self.origin_date_range[0] is not None:
            bad_date_witness_sigla = []
            bad_date_upper_bounds_by_witness = {}
            for i, wit in enumerate(self.witnesses):
                if wit.date_range[1] is not None and wit.date_range[1] < self.origin_date_range[0]:
                    bad_date_witness_sigla.append(wit.id)
                    bad_date_upper_bounds_by_witness[wit.id] = wit.date_range[1]
            if len(bad_date_witness_sigla) > 0:
                msg = ""
                msg += "The following witnesses have their latest possible dates before the earliest date of origin %d specified for the collated work:\n"
                msg += ", ".join(
                    [
                        (siglum + "(" + str(bad_date_upper_bounds_by_witness[siglum]) + ")")
                        for siglum in bad_date_witness_sigla
                    ]
                )
                raise WitnessDateException(msg)
        t1 = time.time()
        if self.verbose:
            print("Finished witness validation in %0.4fs." % (t1 - t0))
        return

    def update_witness_date_ranges_from_dates_file(self, dates_file: Union[Path, str]):
        """Given a CSV-formatted dates file, update the date ranges of all witnesses whose IDs are in the first column of the dates file
        (overwriting existing date ranges if necessary).
        """
        if self.verbose:
            print("Updating witness dates from file %s..." % (str(dates_file)))
        t0 = time.time()
        dates_df = pd.read_csv(dates_file, index_col=0, names=["id", "min", "max"])
        for witness in self.witnesses:
            wit_id = witness.id
            if wit_id in dates_df.index:
                # For every witness in the list whose ID is specified in the dates file,
                # update their date ranges (as long as the date ranges in the file are are well-formed):
                min_date = int(dates_df.loc[wit_id]["min"]) if not np.isnan(dates_df.loc[wit_id]["min"]) else None
                max_date = (
                    int(dates_df.loc[wit_id]["max"])
                    if not np.isnan(dates_df.loc[wit_id]["max"])
                    else datetime.now().year
                )
                print(min_date, max_date)
                if min_date is not None and max_date is not None and min_date > max_date:
                    raise ParsingException(
                        "In dates file %s, for witness ID %s, the minimum date %d is greater than the maximum date %d."
                        % (str(dates_file), wit_id, min_date, max_date)
                    )
                witness.date_range = [min_date, max_date]
        t1 = time.time()
        if self.verbose:
            print("Finished witness date range updates in %0.4fs." % (t1 - t0))
        return

    def update_origin_date_range_from_witness_date_ranges(self):
        """Conditionally updates the upper bound on the date of origin of the work represented by this Collation
        based on the bounds on the witnesses' dates.
        If none of the witnesses have bounds on their dates, then nothing is done.
        This method is only invoked if the work's date of origin does not already have its upper bound defined.
        """
        if self.verbose:
            print("Updating upper bound on origin date using witness dates...")
        t0 = time.time()
        # Set the origin date to the earliest witness date:
        witness_date_lower_bounds = [wit.date_range[0] for wit in self.witnesses if wit.date_range[0] is not None]
        witness_date_upper_bounds = [wit.date_range[1] for wit in self.witnesses if wit.date_range[1] is not None]
        min_witness_date = (
            min(witness_date_lower_bounds + witness_date_upper_bounds)
            if len(witness_date_lower_bounds + witness_date_upper_bounds) > 0
            else None
        )
        if min_witness_date is not None:
            self.origin_date_range[1] = (
                min(self.origin_date_range[1], min_witness_date)
                if self.origin_date_range[1] is not None
                else min_witness_date
            )
        t1 = time.time()
        if self.verbose:
            print("Finished updating upper bound on origin date in %0.4fs." % (t1 - t0))
        return

    def update_witness_date_ranges_from_origin_date_range(self):
        """Attempts to update the lower bounds on the witnesses' dates of origin of the work represented by this Collation
        using the upper bound on the date of origin of the work represented by this Collation.
        This method is only invoked if the upper bound on the work's date of origin was not already defined
        (i.e., if update_origin_date_range_from_witness_date_ranges was not invoked).
        """
        if self.verbose:
            print("Updating lower bounds on witness dates using origin date...")
        t0 = time.time()
        # Proceed for every witness:
        for i, wit in enumerate(self.witnesses):
            # Ensure that the lower bound on this witness's date is no earlier than the upper bound on the date of the work's origin:
            wit.date_range[0] = (
                max(wit.date_range[0], self.origin_date_range[1])
                if wit.date_range[0] is not None
                else self.origin_date_range[1]
            )
            # Then ensure that the upper bound on this witness's date is no earlier than its lower bound, in case we updated it:
            wit.date_range[1] = max(wit.date_range[0], wit.date_range[1])
        t1 = time.time()
        if self.verbose:
            print("Finished updating lower bounds on witness dates in %0.4fs." % (t1 - t0))
        return

    def parse_intrinsic_odds(self, xml: et.ElementTree):
        """Given an XML tree for a collation, populates this Collation's list of intrinsic probability categories
        (e.g., "absolutely more likely," "highly more likely," "more likely," "slightly more likely," "equally likely")
        and its dictionary mapping these categories to numerical odds.
        If a category does not contain a certainty element specifying its number, then it will be assumed to be a parameter to be estimated.

        Args:
            xml: An lxml.etree.ElementTree representing an XML tree rooted at a TEI element.
        """
        if self.verbose:
            print("Parsing intrinsic odds categories...")
        t0 = time.time()
        self.intrinsic_categories = []
        self.intrinsic_odds_by_id = {}
        for interp in xml.xpath("//tei:interpGrp[@type=\"intrinsic\"]/tei:interp", namespaces={"tei": tei_ns}):
            # These must be indexed by the xml:id attribute, so skip any that do not have one:
            if interp.get("{%s}id" % xml_ns) is None:
                continue
            odds_category = interp.get("{%s}id" % xml_ns)
            # If this element contains a certainty subelement with a fixed odds value for this category, then set it:
            odds = None
            for certainty in interp.xpath("./tei:certainty", namespaces={"tei": tei_ns}):
                if certainty.get("degree") is not None:
                    odds = float(certainty.get("degree"))
                    break
            self.intrinsic_categories.append(odds_category)
            self.intrinsic_odds_by_id[odds_category] = odds
        t1 = time.time()
        if self.verbose:
            print(
                "Finished processing %d intrinsic odds categories in %0.4fs."
                % (len(self.intrinsic_categories), t1 - t0)
            )
        return

    def parse_transcriptional_rates(self, xml: et.ElementTree):
        """Given an XML tree for a collation, populates this Collation's dictionary mapping transcriptional change categories
        (e.g., "aural confusion," "visual error," "clarification") to numerical rates.
        If a category does not contain a certainty element specifying its number, then it will be assumed to be a parameter to be estimated.

        Args:
            xml: An lxml.etree.ElementTree representing an XML tree rooted at a TEI element.
        """
        if self.verbose:
            print("Parsing transcriptional change categories...")
        t0 = time.time()
        self.transcriptional_categories = []
        self.transcriptional_rates_by_id = {}
        for interp in xml.xpath("//tei:interpGrp[@type=\"transcriptional\"]/tei:interp", namespaces={"tei": tei_ns}):
            # These must be indexed by the xml:id attribute, so skip any that do not have one:
            if interp.get("{%s}id" % xml_ns) is None:
                continue
            transcriptional_category = interp.get("{%s}id" % xml_ns)
            # If this element contains a certainty subelement with a fixed rate for this category, then set it:
            rate = None
            for certainty in interp.xpath("./tei:certainty", namespaces={"tei": tei_ns}):
                if certainty.get("degree") is not None:
                    rate = float(certainty.get("degree"))
                    break
            self.transcriptional_categories.append(transcriptional_category)
            self.transcriptional_rates_by_id[transcriptional_category] = rate
        t1 = time.time()
        if self.verbose:
            print(
                "Finished processing %d transcriptional change categories in %0.4fs."
                % (len(self.transcriptional_rates_by_id), t1 - t0)
            )
        return

    def validate_intrinsic_relations(self):
        """Checks if any VariationUnit's intrinsic_relations map is not a forest.
        If any is not, then an IntrinsicRelationsException is thrown describing the VariationUnit at fault.
        """
        if self.verbose:
            print("Validating intrinsic relation graphs for variation units...")
        t0 = time.time()
        for vu in self.variation_units:
            # Skip any variation units with an empty intrinsic_relations map:
            if len(vu.intrinsic_relations) == 0:
                continue
            # For all others, start by identifying all reading IDs that are not related to by some other reading ID:
            in_degree_by_reading = {}
            for edge in vu.intrinsic_relations:
                s = edge[0]
                t = edge[1]
                if s not in in_degree_by_reading:
                    in_degree_by_reading[s] = 0
                if t not in in_degree_by_reading:
                    in_degree_by_reading[t] = 0
                in_degree_by_reading[t] += 1
            # If any reading has more than one relation pointing to it, then the intrinsic relations graph is not a forest:
            excessive_in_degree_readings = [
                rdg_id for rdg_id in in_degree_by_reading if in_degree_by_reading[rdg_id] > 1
            ]
            if len(excessive_in_degree_readings) > 0:
                msg = ""
                msg += (
                    "In variation unit %s, the following readings have more than one intrinsic relation pointing to them: %s.\n"
                    % (vu.id, ", ".join(excessive_in_degree_readings))
                )
                msg += "Please ensure that at least one reading has no relations pointing to it and that every reading has no more than one relation pointing to it."
                raise IntrinsicRelationsException(msg)
            # If every reading has another reading pointing to it, then the intrinsic relations graph contains a cycle and is not a forest:
            starting_nodes = [rdg_id for rdg_id in in_degree_by_reading if in_degree_by_reading[rdg_id] == 0]
            if len(starting_nodes) == 0:
                msg = ""
                msg += "In variation unit %s, the intrinsic relations contain a cycle.\n" % vu.id
                msg += "Please ensure that at least one reading has no relations pointing to it and that every reading has no more than one relation pointing to it."
                raise IntrinsicRelationsException(msg)
        t1 = time.time()
        if self.verbose:
            print("Finished intrinsic relations validation in %0.4fs." % (t1 - t0))
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

    def get_readings_by_witness_for_unit(self, vu: VariationUnit):
        """Returns a dictionary mapping witness IDs to a list of their reading coefficients for a given variation unit.

        Args:
            vu: A VariationUnit to be processed.

        Returns:
            A dictionary mapping witness ID strings to a list of their coefficients for all substantive readings in this VariationUnit.
        """
        # In a first pass, populate lists of substantive (variation unit ID, reading ID) tuples and reading labels
        # and a map from reading IDs to the indices of their parent substantive reading in this unit:
        reading_id_to_index = {}
        self.substantive_readings_by_variation_unit_id[vu.id] = []
        for rdg in vu.readings:
            # If this reading is missing (e.g., lacunose or inapplicable due to an overlapping variant) or targets another reading, then skip it:
            if rdg.type in self.missing_reading_types or len(rdg.certainties) > 0:
                continue
            # If this reading is trivial, then map it to the last substantive index:
            if rdg.type in self.trivial_reading_types:
                reading_id_to_index[rdg.id] = len(self.substantive_readings_by_variation_unit_id[vu.id]) - 1
                continue
            # Otherwise, the reading is substantive: add it to the map and update the last substantive index:
            self.substantive_readings_by_variation_unit_id[vu.id].append(rdg.id)
            self.substantive_variation_unit_reading_tuples.append(tuple([vu.id, rdg.id]))
            reading_id_to_index[rdg.id] = len(self.substantive_readings_by_variation_unit_id[vu.id]) - 1
        # If the list of substantive readings only contains one entry, then this variation unit is not informative;
        # return an empty dictionary and add nothing to the list of substantive reading labels:
        if self.verbose:
            print(
                "Variation unit %s has %d substantive readings."
                % (vu.id, len(self.substantive_readings_by_variation_unit_id[vu.id]))
            )
        readings_by_witness_for_unit = {}
        # Initialize the output dictionary with empty sets for all base witnesses:
        for wit in self.witnesses:
            readings_by_witness_for_unit[wit.id] = [0] * len(self.substantive_readings_by_variation_unit_id[vu.id])
        # In a second pass, assign each base witness a set containing the readings it supports in this unit:
        for rdg in vu.readings:
            # Initialize the dictionary indicating support for this reading (or its disambiguations):
            rdg_support = [0] * len(self.substantive_readings_by_variation_unit_id[vu.id])
            # If this is a missing reading (e.g., a lacuna or an overlap), then we can skip it, as its corresponding set will be empty:
            if rdg.type in self.missing_reading_types:
                continue
            # Otherwise, if this reading is trivial, then it will contain an entry for the index of its parent substantive reading:
            elif rdg.type in self.trivial_reading_types:
                rdg_support[reading_id_to_index[rdg.id]] = 1
            # Otherwise, if this reading has one or more nonzero certainty degrees,
            # then set the entries for these readings to their degrees:
            elif sum(rdg.certainties.values()) > 0:
                for t in rdg.certainties:
                    # Skip any reading whose ID is unrecognized in this unit:
                    if t in reading_id_to_index:
                        rdg_support[reading_id_to_index[t]] = rdg.certainties[t]
            # Otherwise, if this reading has one or more targets (i.e., if it is an ambiguous reading),
            # then set the entries for each of its targets to 1:
            elif len(rdg.targets) > 0:
                for t in rdg.targets:
                    # Skip any reading whose ID is unrecognized in this unit:
                    if t in reading_id_to_index:
                        rdg_support[reading_id_to_index[t]] = 1
            # Otherwise, this reading is itself substantive; set the entry for the index of this reading to 1:
            else:
                rdg_support[reading_id_to_index[rdg.id]] = 1
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
                    (min(readings_by_witness_for_unit[base_wit][i] + rdg_support[i], 1))
                    for i in range(len(rdg_support))
                ]
        return readings_by_witness_for_unit

    def parse_readings_by_witness(self):
        """Populates the internal dictionary mapping witness IDs to a list of their reading support sets for all variation units, and then fills the empty reading support sets for witnesses of type "corrector" with the entries of the previous witness."""
        if self.verbose:
            print("Populating internal dictionary of witness readings...")
        t0 = time.time()
        # Initialize the data structures to be populated here:
        self.readings_by_witness = {}
        self.variation_unit_ids = []
        for wit in self.witnesses:
            self.readings_by_witness[wit.id] = []
        # Populate them for each variation unit:
        for vu in self.variation_units:
            readings_by_witness_for_unit = self.get_readings_by_witness_for_unit(vu)
            if len(readings_by_witness_for_unit) > 0:
                self.variation_unit_ids.append(vu.id)
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
                % (len(self.witnesses), len(self.variation_unit_ids), t1 - t0)
            )
        return

    def filter_fragmentary_witnesses(self, xml):
        """Filters the original witness list and readings by witness dictionary to exclude witnesses whose proportions of extant passages fall below the fragmentary readings threshold."""
        if self.verbose:
            print(
                "Filtering fragmentary witnesses (extant in < %f of all variation units) out of internal witness list and dictionary of witness readings..."
                % self.fragmentary_threshold
            )
        t0 = time.time()
        fragmentary_witness_set = set()
        # Proceed for each witness in order:
        for wit in self.witnesses:
            wit_id = wit.id
            # We count the number of variation units at which this witness has an extant (i.e., non-missing) reading:
            extant_reading_count = 0
            total_reading_count = len(self.readings_by_witness[wit.id])
            # Proceed through all reading support lists:
            for rdg_support in self.readings_by_witness[wit_id]:
                # If the current reading support list is not all zeroes, then increment this witness's count of extant readings:
                if sum(rdg_support) != 0:
                    extant_reading_count += 1
            # If the proportion of extant readings falls below the threshold, then add this witness to the list of fragmentary witnesses:
            if extant_reading_count / total_reading_count < self.fragmentary_threshold:
                fragmentary_witness_set.add(wit_id)
        # Then filter the witness list to exclude the fragmentary witnesses:
        filtered_witnesses = [wit for wit in self.witnesses if wit.id not in fragmentary_witness_set]
        self.witnesses = filtered_witnesses
        # Then remove the entries for the fragmentary witnesses from the witnesses-to-readings dictionary:
        for wit_id in fragmentary_witness_set:
            del self.readings_by_witness[wit_id]
        t1 = time.time()
        if self.verbose:
            print(
                "Filtered out %d fragmentary witness(es) (%s) in %0.4fs."
                % (len(fragmentary_witness_set), str(list(fragmentary_witness_set)), t1 - t0)
            )
        return

    def get_nexus_symbols(self):
        """Returns a list of one-character symbols needed to represent the states of all substantive readings in NEXUS.

        The number of symbols equals the maximum number of substantive readings at any variation unit.

        Returns:
            A list of individual characters representing states in readings.
        """
        # NOTE: IQTREE does not appear to support symbols outside of 0-9 and a-z, and its base symbols must be case-insensitive.
        # The official version of MrBayes is likewise limited to 32 symbols.
        # But PAUP* allows up to 64 symbols, and Andrew Edmondson's fork of MrBayes does, as well.
        # So this method will support symbols from 0-9, a-z, and A-Z (for a total of 62 states)
        possible_symbols = list(string.digits) + list(string.ascii_lowercase) + list(string.ascii_uppercase)
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

    def to_nexus(
        self,
        file_addr: Union[Path, str],
        drop_constant: bool = False,
        char_state_labels: bool = True,
        frequency: bool = False,
        ambiguous_as_missing: bool = False,
        calibrate_dates: bool = False,
        mrbayes: bool = False,
        clock_model: ClockModel = ClockModel.strict,
    ):
        """Writes this Collation to a NEXUS file with the given address.

        Args:
            file_addr: A string representing the path to an output NEXUS file; the file type should be .nex, .nexus, or .nxs.
            drop_constant: An optional flag indicating whether to ignore variation units with one substantive reading.
            char_state_labels: An optional flag indicating whether or not to include the CharStateLabels block.
            frequency: An optional flag indicating whether to use the StatesFormat=Frequency setting
                instead of the StatesFormat=StatesPresent setting
                (and thus represent all states with frequency vectors rather than symbols).
                Note that this setting is necessary to make use of certainty degrees assigned to multiple ambiguous states in the collation.
            ambiguous_as_missing: An optional flag indicating whether to treat all ambiguous states as missing data.
                If this flag is set, then only base symbols will be generated for the NEXUS file.
                It is only applied if the frequency option is False.
            calibrate_dates: An optional flag indicating whether to add an Assumptions block that specifies date distributions for witnesses.
                This option is intended for inputs to BEAST 2.
            mrbayes: An optional flag indicating whether to add a MrBayes block that specifies model settings and age calibrations for witnesses.
                This option is intended for inputs to MrBayes.
            clock_model: A ClockModel option indicating which type of clock model to use.
                This option is intended for inputs to MrBayes and BEAST 2.
                MrBayes does not presently support a local clock model, so it will default to a strict clock model if a local clock model is specified.
        """
        # Populate a list of sites that will correspond to columns of the sequence alignment:
        substantive_variation_unit_ids = self.variation_unit_ids
        if drop_constant:
            substantive_variation_unit_ids = [
                vu_id
                for vu_id in self.variation_unit_ids
                if len(self.substantive_readings_by_variation_unit_id[vu_id]) > 1
            ]
        substantive_variation_unit_ids_set = set(substantive_variation_unit_ids)
        substantive_variation_unit_reading_tuples_set = set(self.substantive_variation_unit_reading_tuples)
        # Start by calculating the values we will be using here:
        ntax = len(self.witnesses)
        nchar = len(substantive_variation_unit_ids)
        taxlabels = [slugify(wit.id, lowercase=False, separator='_') for wit in self.witnesses]
        max_taxlabel_length = max(
            [len(taxlabel) for taxlabel in taxlabels]
        )  # keep track of the longest taxon label for tabular alignment purposes
        charlabels = [slugify(vu_id, lowercase=False, separator='_') for vu_id in substantive_variation_unit_ids]
        missing_symbol = '?'
        symbols = self.get_nexus_symbols()
        # Generate all parent folders for this file that don't already exist:
        Path(file_addr).parent.mkdir(parents=True, exist_ok=True)
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
            if frequency:
                f.write("\t\tStatesFormat=Frequency\n")
            f.write("\t\tSymbols=\"%s\";\n" % (" ".join(symbols)))
            # If the char_state_labels is set, then write the labels for character-state labels, with each on its own line:
            if char_state_labels:
                f.write("\tCharStateLabels")
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
                if frequency:
                    sequence = "\n\t\t" + taxlabel
                    for j, vu_id in enumerate(self.variation_unit_ids):
                        if vu_id not in substantive_variation_unit_ids_set:
                            continue
                        rdg_support = self.readings_by_witness[wit.id][j]
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
                else:
                    sequence = "\n\t\t" + taxlabel
                    # Add enough space after this label ensure that all sequences are nicely aligned:
                    sequence += " " * (max_taxlabel_length - len(taxlabel) + 1)
                    for j, vu_id in enumerate(self.variation_unit_ids):
                        if vu_id not in substantive_variation_unit_ids_set:
                            continue
                        rdg_support = self.readings_by_witness[wit.id][j]
                        # If this reading is lacunose in this witness, then use the missing character:
                        if sum(rdg_support) == 0:
                            sequence += missing_symbol
                            continue
                        rdg_inds = [
                            k for k, w in enumerate(rdg_support) if w > 0
                        ]  # the index list consists of the indices of all readings with any degree of certainty assigned to them
                        # For singleton readings, just print the symbol:
                        if len(rdg_inds) == 1:
                            sequence += symbols[rdg_inds[0]]
                            continue
                        # For multiple readings, print the corresponding readings in braces or the missing symbol depending on input settings:
                        if ambiguous_as_missing:
                            sequence += missing_symbol
                        else:
                            sequence += "{%s}" % "".join([str(rdg_ind) for rdg_ind in rdg_inds])
                f.write("%s" % (sequence))
            f.write(";\n")
            # End the data block:
            f.write("End;")
            # If calibrate_dates is set, then add the assumptions block:
            if calibrate_dates:
                f.write("\n\n")
                f.write("Begin ASSUMPTIONS;\n")
                # Set the scale to years:
                f.write("\tOPTIONS SCALE = years;\n\n")
                # Then calibrate the witness ages:
                calibrate_strings = []
                for i, wit in enumerate(self.witnesses):
                    taxlabel = taxlabels[i]
                    date_range = wit.date_range
                    if date_range[0] is not None:
                        # If there is a lower bound on the witness's date, then use either a fixed or uniform distribution,
                        # depending on whether the upper and lower bounds match:
                        min_age = datetime.now().year - date_range[1]
                        max_age = datetime.now().year - date_range[0]
                        if min_age == max_age:
                            calibrate_string = "\tCALIBRATE %s = fixed(%d)" % (taxlabel, min_age)
                            calibrate_strings.append(calibrate_string)
                        else:
                            calibrate_string = "\tCALIBRATE %s = uniform(%d,%d)" % (taxlabel, min_age, max_age)
                            calibrate_strings.append(calibrate_string)
                    else:
                        # If there is no lower bound on the witness's date, then use an offset log-normal distribution:
                        min_age = datetime.now().year - date_range[1]
                        calibrate_string = "\tCALIBRATE %s = offsetlognormal(%d,0.0,1.0)" % (taxlabel, min_age)
                        calibrate_strings.append(calibrate_string)
                # Then print the calibrate strings, separated by commas and line breaks and terminated by a semicolon:
                f.write("%s;\n\n" % ",\n".join(calibrate_strings))
                # End the assumptions block:
                f.write("End;")
            # If mrbayes is set, then add the mrbayes block:
            if mrbayes:
                f.write("\n\n")
                f.write("Begin MRBAYES;\n")
                # Turn on the autoclose feature by default:
                f.write("\tset autoclose=yes;\n")
                # Set the branch lengths to be governed by a birth-death clock model, and set up the parameters for this model:
                f.write("\n")
                f.write("\tprset brlenspr = clock:birthdeath;\n")
                f.write("\tprset speciationpr = uniform(0.0,10.0);\n")
                f.write("\tprset extinctionpr = beta(2.0,4.0);\n")
                f.write("\tprset sampleprob = 0.01;\n")
                # Use the specified clock model:
                f.write("\n")
                if clock_model == clock_model.uncorrelated:
                    f.write("\tprset clockvarpr=igr;\n")
                    f.write("\tprset clockratepr=lognormal(0.0,1.0);\n")
                    f.write("\tprset igrvarpr=exponential(1.0);\n")
                else:
                    f.write("\tprset clockvarpr=strict;\n")
                    f.write("\tprset clockratepr=lognormal(0.0,1.0);\n")
                # Set the priors on the tree age depending on the date range for the origin of the collated work:
                f.write("\n")
                if self.origin_date_range[0] is not None:
                    min_tree_age = (
                        datetime.now().year - self.origin_date_range[1]
                        if self.origin_date_range[1] is not None
                        else 0.0
                    )
                    max_tree_age = datetime.now().year - self.origin_date_range[0]
                    f.write("\tprset treeagepr = uniform(%d,%d);\n" % (min_tree_age, max_tree_age))
                else:
                    min_tree_age = (
                        datetime.now().year - self.origin_date_range[1]
                        if self.origin_date_range[1] is not None
                        else 0.0
                    )
                    f.write("\tprset treeagepr = offsetgamma(%d,1.0,1.0);\n" % (min_tree_age))
                # Then calibrate the witness ages:
                f.write("\n")
                f.write("\tprset nodeagepr = calibrated;\n")
                for i, wit in enumerate(self.witnesses):
                    taxlabel = taxlabels[i]
                    date_range = wit.date_range
                    if date_range[0] is not None:
                        # If there is a lower bound on the witness's date, then use either a fixed or uniform distribution,
                        # depending on whether the upper and lower bounds match:
                        min_age = datetime.now().year - date_range[1]
                        max_age = datetime.now().year - date_range[0]
                        if min_age == max_age:
                            f.write("\tcalibrate %s = fixed(%d);\n" % (taxlabel, min_age))
                        else:
                            f.write("\tcalibrate %s = uniform(%d,%d);\n" % (taxlabel, min_age, max_age))
                    else:
                        # If there is no lower bound on the witness's date, then use an offset gamma distribution:
                        min_age = datetime.now().year - date_range[1]
                        f.write("\tcalibrate %s = offsetgamma(%d,1.0,1.0);\n" % (taxlabel, min_age))
                f.write("\n")
                # Add default settings for MCMC estimation of posterior distribution:
                f.write("\tmcmcp ngen=100000;\n")
                # Write the command to run MrBayes:
                f.write("\tmcmc;\n")
                # End the assumptions block:
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

    def to_hennig86(self, file_addr: Union[Path, str], drop_constant: bool = False):
        """Writes this Collation to a file in Hennig86 format with the given address.
        Note that because Hennig86 format does not support NEXUS-style ambiguities, such ambiguities will be treated as missing data.

        Args:
            file_addr: A string representing the path to an output file.
            drop_constant (bool, optional): An optional flag indicating whether to ignore variation units with one substantive reading.
        """
        # Populate a list of sites that will correspond to columns of the sequence alignment:
        substantive_variation_unit_ids = self.variation_unit_ids
        if drop_constant:
            substantive_variation_unit_ids = [
                vu_id
                for vu_id in self.variation_unit_ids
                if len(self.substantive_readings_by_variation_unit_id[vu_id]) > 1
            ]
        substantive_variation_unit_ids_set = set(substantive_variation_unit_ids)
        substantive_variation_unit_reading_tuples_set = set(self.substantive_variation_unit_reading_tuples)
        # Start by calculating the values we will be using here:
        ntax = len(self.witnesses)
        nchar = len(substantive_variation_unit_ids)
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
        # Generate all parent folders for this file that don't already exist:
        Path(file_addr).parent.mkdir(parents=True, exist_ok=True)
        with open(file_addr, "w", encoding="ascii") as f:
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
                for j, vu_id in enumerate(self.variation_unit_ids):
                    if vu_id not in substantive_variation_unit_ids_set:
                        continue
                    rdg_support = self.readings_by_witness[wit.id][j]
                    # If this reading is lacunose in this witness, then use the missing character:
                    if sum(rdg_support) == 0:
                        sequence += missing_symbol
                        continue
                    rdg_inds = [
                        k for k, w in enumerate(rdg_support) if w > 0
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
        phylip_symbols = possible_symbols[:nsymbols]
        return phylip_symbols

    def to_phylip(self, file_addr: Union[Path, str], drop_constant: bool = False):
        """Writes this Collation to a file in PHYLIP format with the given address.
        Note that because PHYLIP format does not support NEXUS-style ambiguities, such ambiguities will be treated as missing data.

        Args:
            file_addr: A string representing the path to an output file.
            drop_constant (bool, optional): An optional flag indicating whether to ignore variation units with one substantive reading.
        """
        # Populate a list of sites that will correspond to columns of the sequence alignment:
        substantive_variation_unit_ids = self.variation_unit_ids
        if drop_constant:
            substantive_variation_unit_ids = [
                vu_id
                for vu_id in self.variation_unit_ids
                if len(self.substantive_readings_by_variation_unit_id[vu_id]) > 1
            ]
        substantive_variation_unit_ids_set = set(substantive_variation_unit_ids)
        substantive_variation_unit_reading_tuples_set = set(self.substantive_variation_unit_reading_tuples)
        # Start by calculating the values we will be using here:
        ntax = len(self.witnesses)
        nchar = len(substantive_variation_unit_ids)
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
        symbols = self.get_phylip_symbols()
        # Generate all parent folders for this file that don't already exist:
        Path(file_addr).parent.mkdir(parents=True, exist_ok=True)
        with open(file_addr, "w", encoding="ascii") as f:
            # Write the dimensions:
            f.write("%d %d\n" % (ntax, nchar))
            # Now write the matrix:
            for i, wit in enumerate(self.witnesses):
                taxlabel = taxlabels[i]
                # Add enough space after this label ensure that all sequences are nicely aligned:
                sequence = taxlabel + (" " * (max_taxlabel_length - len(taxlabel))) + "\t"
                for j, vu_id in enumerate(self.variation_unit_ids):
                    if vu_id not in substantive_variation_unit_ids_set:
                        continue
                    rdg_support = self.readings_by_witness[wit.id][j]
                    # If this reading is lacunose in this witness, then use the missing character:
                    if sum(rdg_support) == 0:
                        sequence += missing_symbol
                        continue
                    rdg_inds = [
                        k for k, w in enumerate(rdg_support) if w > 0
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

    def to_fasta(self, file_addr: Union[Path, str], drop_constant: bool = False):
        """Writes this Collation to a file in FASTA format with the given address.
        Note that because FASTA format does not support NEXUS-style ambiguities, such ambiguities will be treated as missing data.

        Args:
            file_addr: A string representing the path to an output file.
            drop_constant (bool, optional): An optional flag indicating whether to ignore variation units with one substantive reading.
        """
        # Populate a list of sites that will correspond to columns of the sequence alignment:
        substantive_variation_unit_ids = self.variation_unit_ids
        if drop_constant:
            substantive_variation_unit_ids = [
                vu_id
                for vu_id in self.variation_unit_ids
                if len(self.substantive_readings_by_variation_unit_id[vu_id]) > 1
            ]
        substantive_variation_unit_ids_set = set(substantive_variation_unit_ids)
        substantive_variation_unit_reading_tuples_set = set(self.substantive_variation_unit_reading_tuples)
        # Start by calculating the values we will be using here:
        ntax = len(self.witnesses)
        nchar = len(substantive_variation_unit_ids)
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
        # Generate all parent folders for this file that don't already exist:
        Path(file_addr).parent.mkdir(parents=True, exist_ok=True)
        with open(file_addr, "w", encoding="ascii") as f:
            # Now write the matrix:
            for i, wit in enumerate(self.witnesses):
                taxlabel = taxlabels[i]
                # Add enough space after this label ensure that all sequences are nicely aligned:
                sequence = ">%s\n" % taxlabel
                for j, vu_id in enumerate(self.variation_unit_ids):
                    if vu_id not in substantive_variation_unit_ids_set:
                        continue
                    rdg_support = self.readings_by_witness[wit.id][j]
                    # If this reading is lacunose in this witness, then use the missing character:
                    if sum(rdg_support) == 0:
                        sequence += missing_symbol
                        continue
                    rdg_inds = [
                        k for k, w in enumerate(rdg_support) if w > 0
                    ]  # the index list consists of the indices of all readings with any degree of certainty assigned to them
                    # For singleton readings, just print the symbol:
                    if len(rdg_inds) == 1:
                        sequence += symbols[rdg_inds[0]]
                        continue
                    # For multiple readings, print the missing symbol:
                    sequence += missing_symbol
                f.write("%s\n" % (sequence))
        return

    def get_beast_symbols(self):
        """Returns a list of one-character symbols needed to represent the states of all substantive readings in BEAST format.

        The number of symbols equals the maximum number of substantive readings at any variation unit.

        Returns:
            A list of individual characters representing states in readings.
        """
        possible_symbols = (
            list(string.digits) + list(string.ascii_lowercase) + list(string.ascii_uppercase)
        )  # NOTE: for BEAST, any number of states should theoretically be permissible, but since code maps are required for some reason, we will limit the number of symbols to 62 for now
        # The number of symbols needed is equal to the length of the longest substantive reading vector:
        nsymbols = 0
        # If there are no witnesses, then no symbols are needed at all:
        if len(self.witnesses) == 0:
            return []
        wit_id = self.witnesses[0].id
        for rdg_support in self.readings_by_witness[wit_id]:
            nsymbols = max(nsymbols, len(rdg_support))
        beast_symbols = possible_symbols[:nsymbols]
        return beast_symbols

    def get_tip_date_range(self):
        """Gets the minimum and maximum dates attested among the witnesses.
        Also checks if the witness with the latest possible date has a fixed date
        (i.e, if the lower and upper bounds for its date are the same)
        and issues a warning if not, as this will cause unusual behavior in BEAST 2.

        Returns:
            A tuple containing the earliest and latest possible tip dates.
        """
        earliest_date = None
        earliest_wit = None
        latest_date = None
        latest_wit = None
        for wit in self.witnesses:
            wit_id = wit.id
            date_range = wit.date_range
            if date_range[0] is not None:
                if earliest_date is not None:
                    earliest_wit = wit if date_range[0] < earliest_date else earliest_wit
                    earliest_date = min(date_range[0], earliest_date)
                else:
                    earliest_wit = wit
                    earliest_date = date_range[0]
            if date_range[1] is not None:
                if latest_date is not None:
                    latest_wit = wit if date_range[1] > latest_date else latest_wit
                    latest_date = max(date_range[1], latest_date)
                else:
                    latest_wit = wit
                    latest_date = date_range[1]
        if latest_wit.date_range[0] is None or latest_wit.date_range[0] != latest_wit.date_range[1]:
            print(
                "WARNING: the latest witness, %s, has a variable date range; this will result in problems with time-dependent substitution models and misalignment of trees in BEAST DensiTree outputs! Please ensure that witness %s has a fixed date."
                % (latest_wit.id, latest_wit.id)
            )
        return (earliest_date, latest_date)

    def get_beast_origin_span(self, tip_date_range):
        """Returns a tuple containing the lower and upper bounds for the height of the origin of the Birth-Death Skyline model.
        The upper bound on the height of the tree is the difference between the latest tip date
        and the lower bound on the date of the original work, if both are defined;
        otherwise, it is left undefined.
        The lower bound on the height of the tree is the difference between the latest tip date
        and the upper bound on the date of the original work, if both are defined;
        otherwise, it is the difference between the earliest tip date and the latest, if both are defined.

        Args:
            tip_date_range: A tuple containing the earliest and latest possible tip dates.

        Returns:
            A tuple containing lower and upper bounds on the origin height for the Birth-Death Skyline model.
        """
        origin_span = [0, None]
        # If the upper bound on the date of the work's composition is defined, then set the lower bound on the height of the origin using it and the latest tip date
        # (note that if it had to be defined in terms of witness date lower bounds, then this would have happened already):
        if self.origin_date_range[1] is not None:
            origin_span[0] = tip_date_range[1] - self.origin_date_range[1]
        # If the lower bound on the date of the work's composition is defined, then set the upper bound on the height of the origin using it and the latest tip date:
        if self.origin_date_range[0] is not None:
            origin_span[1] = tip_date_range[1] - self.origin_date_range[0]
        return tuple(origin_span)

    def get_beast_date_map(self, taxlabels):
        """Returns a string representing witness-to-date mappings in BEAST format.

        Since this format requires single dates as opposed to date ranges,
        witnesses with closed date ranges will be mapped to the average of their lower and upper bounds,
        and witnesses with open date ranges will not be mapped.

        Args:
            taxlabels: A list of slugified taxon labels.

        Returns:
            A string containing comma-separated date calibrations of the form witness_id=date.
        """
        calibrate_strings = []
        for i, wit in enumerate(self.witnesses):
            taxlabel = taxlabels[i]
            date_range = wit.date_range
            # If either end of this witness's date range is empty, then do not include it:
            if date_range[0] is None or date_range[1] is None:
                continue
            # Otherwise, take the midpoint of its date range as its date:
            date = int((date_range[0] + date_range[1]) / 2)
            calibrate_string = "%s=%d" % (taxlabel, date)
            calibrate_strings.append(calibrate_string)
        # Then output the full date map string:
        date_map = ",".join(calibrate_strings)
        return date_map

    def get_beast_code_map_for_unit(self, symbols, missing_symbol, vu_ind):
        """Returns a string containing state/reading code mappings in BEAST format using the given single-state and missing state symbols for the character/variation unit at the given index.
        If the variation unit at the given index is a singleton unit (i.e., if it has only one substantive reading), then a code for a dummy state will be included.

        Args:
            vu_ind: An integer index for the desired unit.

        Returns:
            A string containing comma-separated code mappings.
        """
        vu = self.variation_units[vu_ind]
        vu_id = vu.id
        code_map = {}
        for k in range(len(self.substantive_readings_by_variation_unit_id[vu.id])):
            code_map[symbols[k]] = str(k)
        # If this site is a singleton site, then add a code mapping for the dummy state:
        if len(self.substantive_readings_by_variation_unit_id[vu.id]) == 1:
            code_map[symbols[1]] = str(1)
        # Then add a mapping for the missing state, including a dummy state if this is a singleton site:
        code_map[missing_symbol] = " ".join(
            str(k) for k in range(len(self.substantive_readings_by_variation_unit_id[vu.id]))
        )
        # If this site is a singleton site, then add the dummy state to the missing state mapping:
        if len(self.substantive_readings_by_variation_unit_id[vu.id]) == 1:
            code_map[missing_symbol] = code_map[missing_symbol] + " " + str(1)
        # Then combine all of the mappings into a single string:
        code_map_string = ", ".join([code + "=" + code_map[code] for code in code_map])
        return code_map_string

    def get_beast_equilibrium_frequencies_for_unit(self, vu_ind):
        """Returns a string containing state/reading equilibrium frequencies in BEAST format for the character/variation unit at the given index.
        Since the equilibrium frequencies are not used with the substitution models, the equilibrium frequencies simply correspond to a uniform distribution over the states.
        If the variation unit at the given index is a singleton unit (i.e., if it has only one substantive reading), then an equilibrium frequency of 0 will be added for a dummy state.

        Args:
            vu_ind: An integer index for the desired unit.

        Returns:
            A string containing space-separated equilibrium frequencies.
        """
        vu = self.variation_units[vu_ind]
        vu_id = vu.id
        # If this unit is a singleton, then return the string "0.5 0.5":
        if len(self.substantive_readings_by_variation_unit_id[vu_id]) == 1:
            return "0.5 0.5"
        # Otherwise, set the equilibrium frequencies according to a uniform distribution:
        equilibrium_frequencies = [1.0 / len(self.substantive_readings_by_variation_unit_id[vu_id])] * len(
            self.substantive_readings_by_variation_unit_id[vu_id]
        )
        equilibrium_frequencies_string = " ".join([str(w) for w in equilibrium_frequencies])
        return equilibrium_frequencies_string

    def get_beast_root_frequencies_for_unit(self, vu_ind):
        """Returns a string containing state/reading root frequencies in BEAST format for the character/variation unit at the given index.
        The root frequencies are calculated from the intrinsic odds at this unit.
        If the variation unit at the given index is a singleton unit (i.e., if it has only one substantive reading), then a root frequency of 0 will be added for a dummy state.
        If no intrinsic odds are specified, then a uniform distribution over all states is assumed.

        Args:
            vu_ind: An integer index for the desired unit.

        Returns:
            A string containing space-separated root frequencies.
        """
        vu = self.variation_units[vu_ind]
        vu_id = vu.id
        intrinsic_relations = vu.intrinsic_relations
        intrinsic_odds_by_id = self.intrinsic_odds_by_id
        # If this unit is a singleton, then return the string "1 0":
        if len(self.substantive_readings_by_variation_unit_id[vu_id]) == 1:
            return "1 0"
        # If this unit has no intrinsic odds, then assume a uniform distribution over all readings:
        if len(intrinsic_relations) == 0:
            root_frequencies = [1.0 / len(self.substantive_readings_by_variation_unit_id[vu_id])] * len(
                self.substantive_readings_by_variation_unit_id[vu_id]
            )
            root_frequencies_string = " ".join([str(w) for w in root_frequencies])
            return root_frequencies_string
        # We will populate the root frequencies based on the intrinsic odds of the readings:
        root_frequencies_by_id = {}
        for rdg_id in self.substantive_readings_by_variation_unit_id[vu_id]:
            root_frequencies_by_id[rdg_id] = 0
        # First, construct an adjacency list for efficient edge iteration:
        neighbors_by_source = {}
        for edge in intrinsic_relations:
            s = edge[0]
            t = edge[1]
            if s not in neighbors_by_source:
                neighbors_by_source[s] = []
            if t not in neighbors_by_source:
                neighbors_by_source[t] = []
            neighbors_by_source[s].append(t)
        # Next, identify all readings that are not targeted by any intrinsic odds relation:
        in_degree_by_reading = {}
        for edge in intrinsic_relations:
            s = edge[0]
            t = edge[1]
            if s not in in_degree_by_reading:
                in_degree_by_reading[s] = 0
            if t not in in_degree_by_reading:
                in_degree_by_reading[t] = 0
            in_degree_by_reading[t] += 1
        starting_nodes = [t for t in in_degree_by_reading if in_degree_by_reading[t] == 0]
        # Set the root frequencies for these readings to 1 (they will be normalized later):
        for starting_node in starting_nodes:
            root_frequencies_by_id[starting_node] = 1.0
        # Next, set the frequencies for the remaining readings recursively using the adjacency list:
        def update_root_frequencies(s):
            for t in neighbors_by_source[s]:
                intrinsic_category = intrinsic_relations[(s, t)]
                odds = (
                    intrinsic_odds_by_id[intrinsic_category]
                    if intrinsic_odds_by_id[intrinsic_category] is not None
                    else 1.0
                )  # TODO: This needs to be handled using parameters once we have it implemented in BEAST
                root_frequencies_by_id[t] = root_frequencies_by_id[s] / odds
                update_root_frequencies(t)
            return

        for starting_node in starting_nodes:
            update_root_frequencies(starting_node)
        # Then produce a normalized vector of root frequencies that corresponds to a probability distribution:
        root_frequencies = [
            root_frequencies_by_id[rdg_id] for rdg_id in self.substantive_readings_by_variation_unit_id[vu_id]
        ]
        total_frequencies = sum(root_frequencies)
        for k in range(len(root_frequencies)):
            root_frequencies[k] = root_frequencies[k] / total_frequencies
        root_frequencies_string = " ".join([str(w) for w in root_frequencies])
        return root_frequencies_string

    def to_beast(
        self,
        file_addr: Union[Path, str],
        drop_constant: bool = False,
        clock_model: ClockModel = ClockModel.strict,
        ancestral_logger: AncestralLogger = AncestralLogger.state,
        seed: int = None,
    ):
        """Writes this Collation to a file in BEAST format with the given address.

        Args:
            file_addr: A string representing the path to an output file.
            drop_constant (bool, optional): An optional flag indicating whether to ignore variation units with one substantive reading.
            clock_model: A ClockModel option indicating which clock model to use.
            ancestral_logger: An AncestralLogger option indicating which class of logger (if any) to use for ancestral states.
            seed: A seed for random number generation (for setting initial values of unspecified transcriptional rates).
        """
        # Populate a list of sites that will correspond to columns of the sequence alignment:
        substantive_variation_unit_ids = self.variation_unit_ids
        if drop_constant:
            substantive_variation_unit_ids = [
                vu_id
                for vu_id in self.variation_unit_ids
                if len(self.substantive_readings_by_variation_unit_id[vu_id]) > 1
            ]
        substantive_variation_unit_ids_set = set(substantive_variation_unit_ids)
        substantive_variation_unit_reading_tuples_set = set(self.substantive_variation_unit_reading_tuples)
        # First, calculate the values we will be using for the main template:
        taxlabels = [slugify(wit.id, lowercase=False, separator='_') for wit in self.witnesses]
        missing_symbol = '?'
        symbols = self.get_beast_symbols()
        tip_date_range = self.get_tip_date_range()
        origin_span = self.get_beast_origin_span(tip_date_range)
        date_map = self.get_beast_date_map(taxlabels)
        # Then populate the necessary objects for the BEAST XML Jinja template:
        witness_objects = []
        variation_unit_objects = []
        intrinsic_category_objects = []
        transcriptional_category_objects = []
        # Start with witnesses:
        for i, wit in enumerate(self.witnesses):
            witness_object = {}
            # Copy the ID for this witness:
            witness_object["id"] = wit.id
            # Copy its date bounds:
            witness_object["min_date"] = wit.date_range[0]
            witness_object["max_date"] = wit.date_range[1]
            # Populate its sequence from its entries in the witness's readings dictionary:
            sequence = ""
            for j, rdg_support in enumerate(self.readings_by_witness[wit.id]):
                vu_id = self.variation_unit_ids[j]
                # Skip any variation units deemed non-substantive:
                if vu_id not in substantive_variation_unit_ids:
                    continue
                # If this witness has a certainty of 0 for all readings, then it is a gap; assign a likelihood of 1 to each reading:
                if sum(rdg_support) == 0:
                    for k, w in enumerate(rdg_support):
                        sequence += "1"
                        if k < len(rdg_support) - 1:
                            sequence += ", "
                        else:
                            if len(rdg_support) > 1:
                                sequence += "; "
                            else:
                                # If this site is a singleton site, then add a dummy state:
                                sequence += ", 0; "
                # Otherwise, read the probabilities as they are given:
                else:
                    for k, w in enumerate(rdg_support):
                        sequence += str(w)
                        if k < len(rdg_support) - 1:
                            sequence += ", "
                        else:
                            if len(rdg_support) > 1:
                                sequence += "; "
                            else:
                                # If this site is a singleton site, then add a dummy state:
                                sequence += ", 0; "
            # Strip the final semicolon and space from the sequence:
            sequence = sequence.strip("; ")
            # Then set the witness object's sequence attribute to this string:
            witness_object["sequence"] = sequence
            witness_objects.append(witness_object)
        # Then proceed to variation units:
        for j, vu in enumerate(self.variation_units):
            if vu.id not in substantive_variation_unit_ids_set:
                continue
            variation_unit_object = {}
            # Copy the ID of this variation unit:
            variation_unit_object["id"] = vu.id
            # Copy this variation unit's number of substantive readings,
            # setting it to 2 if it is a singleton unit:
            variation_unit_object["nstates"] = (
                len(self.substantive_readings_by_variation_unit_id[vu.id])
                if len(self.substantive_readings_by_variation_unit_id[vu.id]) > 1
                else 2
            )
            # Then construct the code map for this unit:
            variation_unit_object["code_map"] = self.get_beast_code_map_for_unit(symbols, missing_symbol, j)
            # Then populate a comma-separated string of reading labels for this unit:
            rdg_texts = []
            vu_label = vu.id
            for rdg in vu.readings:
                key = tuple([vu.id, rdg.id])
                if key not in substantive_variation_unit_reading_tuples_set:
                    continue
                rdg_text = slugify(rdg.text, lowercase=False, allow_unicode=True, separator='_')
                # Replace any empty reading text with an omission marker:
                if rdg_text == "":
                    rdg_text = "om."
                rdg_texts.append(rdg_text)
            # If this site is a singleton site, then add a dummy reading for the dummy state:
            if len(self.substantive_readings_by_variation_unit_id[vu.id]) == 1:
                rdg_texts.append("DUMMY")
            rdg_texts_string = ", ".join(rdg_texts)
            variation_unit_object["rdg_texts"] = rdg_texts_string
            # Then populate this unit's equilibrium frequency string and its root frequency string:
            variation_unit_object["equilibrium_frequencies"] = self.get_beast_equilibrium_frequencies_for_unit(j)
            variation_unit_object["root_frequencies"] = self.get_beast_root_frequencies_for_unit(j)
            # Then populate a dictionary mapping epoch height ranges to lists of off-diagonal entries for substitution models:
            rate_objects_by_epoch_height_range = {}
            epoch_height_ranges = []
            # Then proceed based on whether the transcriptional relations for this variation unit have been defined:
            if len(vu.transcriptional_relations_by_date_range) == 0:
                # If there are no transcriptional relations, then map the epoch range of (None, None) to their list of off-diagonal entries:
                epoch_height_ranges.append((None, None))
                rate_objects_by_epoch_height_range[(None, None)] = []
                rate_objects = rate_objects_by_epoch_height_range[(None, None)]
                if len(self.substantive_readings_by_variation_unit_id[vu.id]) == 1:
                    # If this is a singleton site, then use an arbitrary 2x2 rate matrix:
                    rate_objects.append({"transcriptional_categories": ["default"], "expression": None})
                    rate_objects.append({"transcriptional_categories": ["default"], "expression": None})
                else:
                    # If this is a site with multiple substantive readings, but no transcriptional relations list,
                    # then use a Lewis Mk substitution matrix with the appropriate number of states:
                    for k_1, rdg_id_1 in enumerate(self.substantive_readings_by_variation_unit_id[vu.id]):
                        for k_2, rdg_id_2 in enumerate(self.substantive_readings_by_variation_unit_id[vu.id]):
                            # Skip diagonal elements:
                            if k_1 == k_2:
                                continue
                            rate_objects.append({"transcriptional_categories": ["default"], "expression": None})
            else:
                # Otherwise, proceed for every date range:
                for date_range in vu.transcriptional_relations_by_date_range:
                    # Get the map of transcriptional relations for reference later:
                    transcriptional_relations = vu.transcriptional_relations_by_date_range[date_range]
                    # Now get the epoch height range corresponding to this date range, and initialize its list in the dictionary:
                    epoch_height_range = [None, None]
                    epoch_height_range[0] = tip_date_range[1] - date_range[1] if date_range[1] is not None else None
                    epoch_height_range[1] = tip_date_range[1] - date_range[0] if date_range[0] is not None else None
                    epoch_height_range = tuple(epoch_height_range)
                    epoch_height_ranges.append(epoch_height_range)
                    rate_objects_by_epoch_height_range[epoch_height_range] = []
                    rate_objects = rate_objects_by_epoch_height_range[epoch_height_range]
                    # Then proceed for every pair of readings in this unit:
                    for k_1, rdg_id_1 in enumerate(self.substantive_readings_by_variation_unit_id[vu.id]):
                        for k_2, rdg_id_2 in enumerate(self.substantive_readings_by_variation_unit_id[vu.id]):
                            # Skip diagonal elements:
                            if k_1 == k_2:
                                continue
                            # If the first reading has no transcriptional relation to the second in this unit, then use the default rate:
                            if (rdg_id_1, rdg_id_2) not in transcriptional_relations:
                                rate_objects.append({"transcriptional_categories": ["default"], "expression": None})
                                continue
                            # Otherwise, if only one category of transcriptional relations holds between the first and second readings,
                            # then use its rate:
                            if len(transcriptional_relations[(rdg_id_1, rdg_id_2)]) == 1:
                                # If there is only one such category, then add its rate as a standalone var element:
                                transcriptional_category = list(transcriptional_relations[(rdg_id_1, rdg_id_2)])[0]
                                rate_objects.append(
                                    {"transcriptional_categories": [transcriptional_category], "expression": None}
                                )
                                continue
                            # If there is more than one, then add a var element that is a sum of the individual categories' rates:
                            transcriptional_categories = list(transcriptional_relations[(rdg_id_1, rdg_id_2)])
                            args = []
                            for transcriptional_category in transcriptional_categories:
                                args.append("%s_rate" % transcriptional_category)
                            args_string = " ".join(args)
                            ops = ["+"] * (len(args) - 1)
                            ops_string = " ".join(ops)
                            expression_string = " ".join([args_string, ops_string])
                            rate_objects.append(
                                {
                                    "transcriptional_categories": transcriptional_categories,
                                    "expression": expression_string,
                                }
                            )
            # Now reorder the list of epoch height ranges, and get a list of non-null epoch dates in ascending order from the dictionary:
            epoch_height_ranges.reverse()
            epoch_heights = [
                epoch_height_range[0] for epoch_height_range in epoch_height_ranges if epoch_height_range[0] is not None
            ]
            # Then add all of these data structures to the variation unit object:
            variation_unit_object["epoch_heights"] = epoch_heights
            variation_unit_object["epoch_heights_string"] = " ".join(
                [str(epoch_height) for epoch_height in epoch_heights]
            )
            variation_unit_object["epoch_height_ranges"] = epoch_height_ranges
            variation_unit_object["epoch_rates"] = [
                rate_objects_by_epoch_height_range[epoch_height_range] for epoch_height_range in epoch_height_ranges
            ]
            variation_unit_objects.append(variation_unit_object)
        # Then proceed to intrinsic odds categories:
        for intrinsic_category in self.intrinsic_categories:
            intrinsic_category_object = {}
            # Copy the ID of this intrinsic category:
            intrinsic_category_object["id"] = intrinsic_category
            # Then copy the odds factors associated with this intrinsic category,
            # setting it to 1.0 if it is not specified and setting the estimate attribute accordingly:
            odds = self.intrinsic_odds_by_id[intrinsic_category]
            intrinsic_category_object["odds"] = odds if odds is not None else 1.0
            intrinsic_category_object["estimate"] = "false" if odds is not None else "true"
            intrinsic_category_objects.append(intrinsic_category_object)
        # Then proceed to transcriptional rate categories:
        rng = np.random.default_rng(seed)
        for transcriptional_category in self.transcriptional_categories:
            transcriptional_category_object = {}
            # Copy the ID of this transcriptional category:
            transcriptional_category_object["id"] = transcriptional_category
            # Then copy the rate of this transcriptional category,
            # setting it to a random number sampled from a Gamma distribution if it is not specified and setting the estimate attribute accordingly:
            rate = self.transcriptional_rates_by_id[transcriptional_category]
            transcriptional_category_object["rate"] = rate if rate is not None else rng.gamma(5.0, 2.0)
            transcriptional_category_object["estimate"] = "false" if rate is not None else "true"
            transcriptional_category_objects.append(transcriptional_category_object)
        # Now render the output XML file using the Jinja template:
        env = Environment(loader=PackageLoader("teiphy", "templates"), autoescape=select_autoescape())
        template = env.get_template("beast_template.xml")
        rendered = template.render(
            nsymbols=len(symbols),
            date_map=date_map,
            origin_span=origin_span,
            clock_model=clock_model.value,
            clock_rate_categories=2 * len(self.witnesses) - 1,
            ancestral_logger=ancestral_logger.value,
            witnesses=witness_objects,
            variation_units=variation_unit_objects,
            intrinsic_categories=intrinsic_category_objects,
            transcriptional_categories=transcriptional_category_objects,
        )
        # Generate all parent folders for this file that don't already exist:
        Path(file_addr).parent.mkdir(parents=True, exist_ok=True)
        with open(file_addr, "w", encoding="utf-8") as f:
            f.write(rendered)
        return

    def to_numpy(self, drop_constant: bool = False, split_missing: bool = True):
        """Returns this Collation in the form of a NumPy array, along with arrays of its row and column labels.

        Args:
            drop_constant (bool, optional): An optional flag indicating whether to ignore variation units with one substantive reading.
            split_missing: An optional flag indicating whether or not to treat missing characters/variation units as having a contribution of 1 split over all states/readings; if False, then missing data is ignored (i.e., all states are 0). Default value is True.

        Returns:
            A NumPy array with a row for each substantive reading and a column for each witness.
            A list of substantive reading ID strings.
            A list of witness ID strings.
        """
        # Populate a list of sites that will correspond to columns of the sequence alignment:
        substantive_variation_unit_ids = self.variation_unit_ids
        if drop_constant:
            substantive_variation_unit_ids = [
                vu_id
                for vu_id in self.variation_unit_ids
                if len(self.substantive_readings_by_variation_unit_id[vu_id]) > 1
            ]
        substantive_variation_unit_ids_set = set(substantive_variation_unit_ids)
        substantive_variation_unit_reading_tuples_set = set(self.substantive_variation_unit_reading_tuples)
        # Initialize the output array with the appropriate dimensions:
        reading_labels = []
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
        col_ind = 0
        for i, wit in enumerate(self.witnesses):
            row_ind = 0
            for j, vu_id in enumerate(self.variation_unit_ids):
                if vu_id not in substantive_variation_unit_ids_set:
                    continue
                rdg_support = self.readings_by_witness[wit.id][j]
                # If this reading support vector sums to 0, then this is missing data; handle it as specified:
                if sum(rdg_support) == 0:
                    if split_missing:
                        for i in range(len(rdg_support)):
                            matrix[row_ind, col_ind] = 1 / len(rdg_support)
                            row_ind += 1
                    else:
                        row_ind += len(rdg_support)
                # Otherwise, add its coefficients normally:
                else:
                    for i in range(len(rdg_support)):
                        matrix[row_ind, col_ind] = rdg_support[i]
                        row_ind += 1
            col_ind += 1
        return matrix, reading_labels, witness_labels

    def to_distance_matrix(self, drop_constant: bool = False, proportion: bool = False, show_ext: bool = False):
        """Transforms this Collation into a NumPy distance matrix between witnesses, along with an array of its labels for the witnesses.
        Distances can be computed either as counts of disagreements (the default setting), or as proportions of disagreements over all variation units where both witnesses have singleton readings.
        Optionally, the count of units where both witnesses have singleton readings can be included after the count/proportion of disagreements.

        Args:
            drop_constant (bool, optional): An optional flag indicating whether to ignore variation units with one substantive reading.
                Default value is False.
            proportion (bool, optional): An optional flag indicating whether or not to calculate distances as proportions over extant, unambiguous variation units.
                Default value is False.
            show_ext: An optional flag indicating whether each cell in a distance or similarity matrix
                should include the number of their extant, unambiguous variation units after the number of their disagreements.
                Default value is False.

        Returns:
            A NumPy distance matrix with a row and column for each witness.
            A list of witness ID strings.
        """
        # Populate a list of sites that will correspond to columns of the sequence alignment:
        substantive_variation_unit_ids = self.variation_unit_ids
        if drop_constant:
            substantive_variation_unit_ids = [
                vu_id
                for vu_id in self.variation_unit_ids
                if len(self.substantive_readings_by_variation_unit_id[vu_id]) > 1
            ]
        substantive_variation_unit_ids_set = set(substantive_variation_unit_ids)
        substantive_variation_unit_reading_tuples_set = set(self.substantive_variation_unit_reading_tuples)
        # Initialize the output array with the appropriate dimensions:
        witness_labels = [wit.id for wit in self.witnesses]
        # The type of the matrix will depend on the input options:
        matrix = None
        if show_ext:
            matrix = np.full(
                (len(witness_labels), len(witness_labels)), "NA", dtype=object
            )  # strings of the form "disagreements/extant"
        elif proportion:
            matrix = np.full(
                (len(witness_labels), len(witness_labels)), 0.0, dtype=float
            )  # floats of the form disagreements/extant
        else:
            matrix = np.full((len(witness_labels), len(witness_labels)), 0, dtype=int)  # ints of the form disagreements
        for i, wit_1 in enumerate(witness_labels):
            for j, wit_2 in enumerate(witness_labels):
                extant_units = 0
                disagreements = 0
                # If either of the cells for this pair of witnesses has been populated already,
                # then just copy the entry from the other side of the diagonal without recalculating:
                if i > j:
                    matrix[i, j] = matrix[j, i]
                    continue
                # Otherwise, calculate the number of units where both witnesses have unambiguous readings
                # and the number of units where they disagree:
                for k, vu_id in enumerate(self.variation_unit_ids):
                    if vu_id not in substantive_variation_unit_ids_set:
                        continue
                    wit_1_rdg_support = self.readings_by_witness[wit_1][k]
                    wit_2_rdg_support = self.readings_by_witness[wit_2][k]
                    wit_1_rdg_inds = [l for l, w in enumerate(wit_1_rdg_support) if w > 0]
                    wit_2_rdg_inds = [l for l, w in enumerate(wit_2_rdg_support) if w > 0]
                    if len(wit_1_rdg_inds) != 1 or len(wit_2_rdg_inds) != 1:
                        continue
                    extant_units += 1
                    if wit_1_rdg_inds[0] != wit_2_rdg_inds[0]:
                        disagreements += 1
                cell_entry = None
                if proportion:
                    cell_entry = disagreements / max(
                        extant_units, 1
                    )  # the max in the denominator is to prevent division by 0; the distance entry will be 0 if the two witnesses have no overlap
                else:
                    cell_entry = disagreements
                if show_ext:
                    cell_entry = str(cell_entry) + "/" + str(extant_units)
                matrix[i, j] = cell_entry
        return matrix, witness_labels

    def to_similarity_matrix(self, drop_constant: bool = False, proportion: bool = False, show_ext: bool = False):
        """Transforms this Collation into a NumPy similarity matrix between witnesses, along with an array of its labels for the witnesses.
        Similarities can be computed either as counts of agreements (the default setting), or as proportions of agreements over all variation units where both witnesses have singleton readings.
        Optionally, the count of units where both witnesses have singleton readings can be included after the count/proportion of agreements.

        Args:
            drop_constant (bool, optional): An optional flag indicating whether to ignore variation units with one substantive reading.
                Default value is False.
            proportion (bool, optional): An optional flag indicating whether or not to calculate similarities as proportions over extant, unambiguous variation units.
                Default value is False.
            show_ext: An optional flag indicating whether each cell in a distance or similarity matrix
                should include the number of their extant, unambiguous variation units after the number of agreements.
                Default value is False.

        Returns:
            A NumPy distance matrix with a row and column for each witness.
            A list of witness ID strings.
        """
        # Populate a list of sites that will correspond to columns of the sequence alignment:
        substantive_variation_unit_ids = self.variation_unit_ids
        if drop_constant:
            substantive_variation_unit_ids = [
                vu_id
                for vu_id in self.variation_unit_ids
                if len(self.substantive_readings_by_variation_unit_id[vu_id]) > 1
            ]
        substantive_variation_unit_ids_set = set(substantive_variation_unit_ids)
        substantive_variation_unit_reading_tuples_set = set(self.substantive_variation_unit_reading_tuples)
        # Initialize the output array with the appropriate dimensions:
        witness_labels = [wit.id for wit in self.witnesses]
        # The type of the matrix will depend on the input options:
        matrix = None
        if show_ext:
            matrix = np.full(
                (len(witness_labels), len(witness_labels)), "NA", dtype=object
            )  # strings of the form "agreements/extant"
        elif proportion:
            matrix = np.full(
                (len(witness_labels), len(witness_labels)), 0.0, dtype=float
            )  # floats of the form agreements/extant
        else:
            matrix = np.full((len(witness_labels), len(witness_labels)), 0, dtype=int)  # ints of the form agreements
        for i, wit_1 in enumerate(witness_labels):
            for j, wit_2 in enumerate(witness_labels):
                extant_units = 0
                agreements = 0
                # If either of the cells for this pair of witnesses has been populated already,
                # then just copy the entry from the other side of the diagonal without recalculating:
                if i > j:
                    matrix[i, j] = matrix[j, i]
                    continue
                # Otherwise, calculate the number of units where both witnesses have unambiguous readings
                # and the number of units where they agree:
                for k, vu_id in enumerate(self.variation_unit_ids):
                    if vu_id not in substantive_variation_unit_ids_set:
                        continue
                    wit_1_rdg_support = self.readings_by_witness[wit_1][k]
                    wit_2_rdg_support = self.readings_by_witness[wit_2][k]
                    wit_1_rdg_inds = [l for l, w in enumerate(wit_1_rdg_support) if w > 0]
                    wit_2_rdg_inds = [l for l, w in enumerate(wit_2_rdg_support) if w > 0]
                    if len(wit_1_rdg_inds) != 1 or len(wit_2_rdg_inds) != 1:
                        continue
                    extant_units += 1
                    if wit_1_rdg_inds[0] == wit_2_rdg_inds[0]:
                        agreements += 1
                cell_entry = None
                if proportion:
                    cell_entry = agreements / max(
                        extant_units, 1
                    )  # the max in the denominator is to prevent division by 0; the distance entry will be 0 if the two witnesses have no overlap
                else:
                    cell_entry = agreements
                if show_ext:
                    cell_entry = str(cell_entry) + "/" + str(extant_units)
                matrix[i, j] = cell_entry
        return matrix, witness_labels

    def to_nexus_table(self, drop_constant: bool = False, ambiguous_as_missing: bool = False):
        """Returns this Collation in the form of a table with rows for taxa, columns for characters, and reading IDs in cells.

        Args:
            drop_constant (bool, optional): An optional flag indicating whether to ignore variation units with one substantive reading.
                Default value is False.
            ambiguous_as_missing (bool, optional): An optional flag indicating whether to treat all ambiguous states as missing data.
                Default value is False.

        Returns:
            A NumPy array with rows for taxa, columns for characters, and reading IDs in cells.
            A list of substantive reading ID strings.
            A list of witness ID strings.
        """
        # Populate a list of sites that will correspond to columns of the sequence alignment:
        substantive_variation_unit_ids = self.variation_unit_ids
        if drop_constant:
            substantive_variation_unit_ids = [
                vu_id
                for vu_id in self.variation_unit_ids
                if len(self.substantive_readings_by_variation_unit_id[vu_id]) > 1
            ]
        substantive_variation_unit_ids_set = set(substantive_variation_unit_ids)
        substantive_variation_unit_reading_tuples_set = set(self.substantive_variation_unit_reading_tuples)
        # In a first pass, populate a dictionary mapping (variation unit index, reading index) tuples from the readings_by_witness dictionary
        # to the readings' IDs:
        reading_ids_by_indices = {}
        for j, vu in enumerate(self.variation_units):
            if vu.id not in substantive_variation_unit_ids_set:
                continue
            k = 0
            for rdg in vu.readings:
                key = tuple([vu.id, rdg.id])
                if key not in substantive_variation_unit_reading_tuples_set:
                    continue
                indices = tuple([j, k])
                reading_ids_by_indices[indices] = rdg.id
                k += 1
        # Initialize the output array with the appropriate dimensions:
        missing_symbol = '?'
        witness_labels = [wit.id for wit in self.witnesses]
        matrix = np.full(
            (len(witness_labels), len(substantive_variation_unit_ids)), missing_symbol, dtype=object
        )  # use dtype=object because the maximum string length is not known up front
        # Then populate it with the appropriate values:
        row_ind = 0
        for i, wit in enumerate(self.witnesses):
            col_ind = 0
            for j, vu in enumerate(self.variation_units):
                if vu.id not in substantive_variation_unit_ids_set:
                    continue
                rdg_support = self.readings_by_witness[wit.id][j]
                # If this reading support vector sums to 0, then this is missing data; handle it as specified:
                if sum(rdg_support) == 0:
                    matrix[row_ind, col_ind] = missing_symbol
                # Otherwise, add its coefficients normally:
                else:
                    rdg_inds = [
                        k for k, w in enumerate(rdg_support) if w > 0
                    ]  # the index list consists of the indices of all readings with any degree of certainty assigned to them
                    # For singleton readings, just print the reading ID:
                    if len(rdg_inds) == 1:
                        k = rdg_inds[0]
                        matrix[row_ind, col_ind] = reading_ids_by_indices[(j, k)]
                    # For multiple readings, print the corresponding reading IDs in braces or the missing symbol depending on input settings:
                    else:
                        if ambiguous_as_missing:
                            matrix[row_ind, col_ind] = missing_symbol
                        else:
                            matrix[row_ind, col_ind] = "{%s}" % " ".join(
                                [reading_ids_by_indices[(j, k)] for k in rdg_inds]
                            )
                col_ind += 1
            row_ind += 1
        return matrix, witness_labels, substantive_variation_unit_ids

    def to_long_table(self, drop_constant: bool = False):
        """Returns this Collation in the form of a long table with columns for taxa, characters, reading indices, and reading values.
        Note that this method treats ambiguous readings as missing data.

        Args:
            drop_constant (bool, optional): An optional flag indicating whether to ignore variation units with one substantive reading.
                Default value is False.

        Returns:
            A NumPy array with columns for taxa, characters, reading indices, and reading values, and rows for each combination of these values in the matrix.
            A list of column label strings.
        """
        # Populate a list of sites that will correspond to columns of the sequence alignment:
        substantive_variation_unit_ids = self.variation_unit_ids
        if drop_constant:
            substantive_variation_unit_ids = [
                vu_id
                for vu_id in self.variation_unit_ids
                if len(self.substantive_readings_by_variation_unit_id[vu_id]) > 1
            ]
        substantive_variation_unit_ids_set = set(substantive_variation_unit_ids)
        substantive_variation_unit_reading_tuples_set = set(self.substantive_variation_unit_reading_tuples)
        # Initialize the outputs:
        column_labels = ["taxon", "character", "state", "value"]
        long_table_list = []
        # Populate a dictionary mapping (variation unit index, reading index) tuples to reading texts:
        reading_texts_by_indices = {}
        for j, vu in enumerate(self.variation_units):
            if vu.id not in substantive_variation_unit_ids_set:
                continue
            k = 0
            for rdg in vu.readings:
                key = tuple([vu.id, rdg.id])
                if key not in substantive_variation_unit_reading_tuples_set:
                    continue
                indices = tuple([j, k])
                reading_texts_by_indices[indices] = rdg.text
                k += 1
        # Then populate the output list with the appropriate values:
        witness_labels = [wit.id for wit in self.witnesses]
        missing_symbol = '?'
        for i, wit in enumerate(self.witnesses):
            row_ind = 0
            for j, vu_id in enumerate(self.variation_unit_ids):
                if vu_id not in substantive_variation_unit_ids_set:
                    continue
                rdg_support = self.readings_by_witness[wit.id][j]
                # Populate a list of nonzero coefficients for this reading support vector:
                rdg_inds = [k for k, w in enumerate(rdg_support) if w > 0]
                # If this list does not consist of exactly one reading, then treat it as missing data:
                if len(rdg_inds) != 1:
                    long_table_list.append([wit.id, vu_id, missing_symbol, missing_symbol])
                    continue
                k = rdg_inds[0]
                rdg_text = reading_texts_by_indices[(j, k)]
                # Replace empty reading texts with the omission placeholder:
                if rdg_text == "":
                    rdg_text = "om."
                long_table_list.append([wit.id, vu_id, k, rdg_text])
        # Then convert the long table entries list to a NumPy array:
        long_table = np.array(long_table_list)
        return long_table, column_labels

    def to_dataframe(
        self,
        drop_constant: bool = False,
        ambiguous_as_missing: bool = False,
        proportion: bool = False,
        table_type: TableType = TableType.matrix,
        split_missing: bool = True,
        show_ext: bool = False,
    ):
        """Returns this Collation in the form of a Pandas DataFrame array, including the appropriate row and column labels.

        Args:
            drop_constant (bool, optional): An optional flag indicating whether to ignore variation units with one substantive reading.
                Default value is False.
            ambiguous_as_missing (bool, optional): An optional flag indicating whether to treat all ambiguous states as missing data.
                Default value is False.
            proportion (bool, optional): An optional flag indicating whether or not to calculate distances as proportions over extant, unambiguous variation units.
                Default value is False.
            table_type (TableType, optional): A TableType option indicating which type of tabular output to generate.
                Only applicable for tabular outputs.
                Default value is "matrix".
            split_missing: An optional flag indicating whether or not to treat missing characters/variation units as having a contribution of 1 split over all states/readings;
                if False, then missing data is ignored (i.e., all states are 0).
                Default value is True.
            show_ext: An optional flag indicating whether each cell in a distance or similarity matrix
                should include the number of their extant, unambiguous variation units after the number of their disagreements/agreements.
                Only applicable for tabular output formats of type \"distance\" or \"similarity\".
                Default value is False.

        Returns:
            A Pandas DataFrame corresponding to a collation matrix with reading frequencies or a long table with discrete reading states.
        """
        df = None
        # Proceed based on the table type:
        if table_type == TableType.matrix:
            # Convert the collation to a NumPy array and get its row and column labels first:
            matrix, reading_labels, witness_labels = self.to_numpy(
                drop_constant=drop_constant, split_missing=split_missing
            )
            df = pd.DataFrame(matrix, index=reading_labels, columns=witness_labels)
        elif table_type == TableType.distance:
            # Convert the collation to a NumPy array and get its row and column labels first:
            matrix, witness_labels = self.to_distance_matrix(
                drop_constant=drop_constant, proportion=proportion, show_ext=show_ext
            )
            df = pd.DataFrame(matrix, index=witness_labels, columns=witness_labels)
        elif table_type == TableType.similarity:
            # Convert the collation to a NumPy array and get its row and column labels first:
            matrix, witness_labels = self.to_similarity_matrix(
                drop_constant=drop_constant, proportion=proportion, show_ext=show_ext
            )
            df = pd.DataFrame(matrix, index=witness_labels, columns=witness_labels)
        elif table_type == TableType.nexus:
            # Convert the collation to a NumPy array and get its row and column labels first:
            matrix, witness_labels, vu_labels = self.to_nexus_table(
                drop_constant=drop_constant, ambiguous_as_missing=ambiguous_as_missing
            )
            df = pd.DataFrame(matrix, index=witness_labels, columns=vu_labels)
        elif table_type == TableType.long:
            # Convert the collation to a long table and get its column labels first:
            long_table, column_labels = self.to_long_table(drop_constant=drop_constant)
            df = pd.DataFrame(long_table, columns=column_labels)
        return df

    def to_csv(
        self,
        file_addr: Union[Path, str],
        drop_constant: bool = False,
        ambiguous_as_missing: bool = False,
        proportion: bool = False,
        table_type: TableType = TableType.matrix,
        split_missing: bool = True,
        show_ext: bool = False,
        **kwargs
    ):
        """Writes this Collation to a comma-separated value (CSV) file with the given address.

        If your witness IDs are numeric (e.g., Gregory-Aland numbers), then they will be written in full to the CSV file, but Excel will likely interpret them as numbers and truncate any leading zeroes!

        Args:
            file_addr: A string representing the path to an output CSV file; the file type should be .csv.
            drop_constant: An optional flag indicating whether to ignore variation units with one substantive reading.
                Default value is False.
            ambiguous_as_missing: An optional flag indicating whether to treat all ambiguous states as missing data.
                Default value is False.
            proportion: An optional flag indicating whether or not to calculate distances as proportions over extant, unambiguous variation units.
                Default value is False.
            table_type: A TableType option indicating which type of tabular output to generate.
                Only applicable for tabular outputs.
                Default value is "matrix".
            split_missing: An optional flag indicating whether or not to treat missing characters/variation units as having a contribution of 1 split over all states/readings;
                if False, then missing data is ignored (i.e., all states are 0).
                Default value is True.
            show_ext: An optional flag indicating whether each cell in a distance or similarity matrix
                should include the number of their extant, unambiguous variation units after the number of their disagreements/agreements.
                Only applicable for tabular output formats of type \"distance\" or \"similarity\".
                Default value is False.
            **kwargs: Keyword arguments for pandas.DataFrame.to_csv.
        """
        # Convert the collation to a Pandas DataFrame first:
        df = self.to_dataframe(
            drop_constant=drop_constant,
            ambiguous_as_missing=ambiguous_as_missing,
            proportion=proportion,
            table_type=table_type,
            split_missing=split_missing,
            show_ext=show_ext,
        )
        # Generate all parent folders for this file that don't already exist:
        Path(file_addr).parent.mkdir(parents=True, exist_ok=True)
        # Proceed based on the table type:
        if table_type == TableType.long:
            return df.to_csv(
                file_addr, encoding="utf-8-sig", index=False, **kwargs
            )  # add BOM to start of file so that Excel will know to read it as Unicode
        return df.to_csv(
            file_addr, encoding="utf-8-sig", **kwargs
        )  # add BOM to start of file so that Excel will know to read it as Unicode

    def to_excel(
        self,
        file_addr: Union[Path, str],
        drop_constant: bool = False,
        ambiguous_as_missing: bool = False,
        proportion: bool = False,
        table_type: TableType = TableType.matrix,
        split_missing: bool = True,
        show_ext: bool = False,
    ):
        """Writes this Collation to an Excel (.xlsx) file with the given address.

        Since Pandas is deprecating its support for xlwt, specifying an output in old Excel (.xls) output is not recommended.

        Args:
            file_addr: A string representing the path to an output Excel file; the file type should be .xlsx.
            drop_constant: An optional flag indicating whether to ignore variation units with one substantive reading.
                Default value is False.
            ambiguous_as_missing: An optional flag indicating whether to treat all ambiguous states as missing data.
                Default value is False.
            proportion: An optional flag indicating whether or not to calculate distances as proportions over extant, unambiguous variation units.
                Default value is False.
            table_type: A TableType option indicating which type of tabular output to generate.
                Only applicable for tabular outputs.
                Default value is "matrix".
            split_missing: An optional flag indicating whether or not to treat missing characters/variation units as having a contribution of 1 split over all states/readings;
                if False, then missing data is ignored (i.e., all states are 0).
                Default value is True.
            show_ext: An optional flag indicating whether each cell in a distance or similarity matrix
                should include the number of their extant, unambiguous variation units after the number of their disagreements/agreements.
                Only applicable for tabular output formats of type \"distance\" or \"similarity\".
                Default value is False.
        """
        # Convert the collation to a Pandas DataFrame first:
        df = self.to_dataframe(
            drop_constant=drop_constant,
            ambiguous_as_missing=ambiguous_as_missing,
            proportion=proportion,
            table_type=table_type,
            split_missing=split_missing,
            show_ext=show_ext,
        )
        # Generate all parent folders for this file that don't already exist:
        Path(file_addr).parent.mkdir(parents=True, exist_ok=True)
        # Proceed based on the table type:
        if table_type == TableType.long:
            return df.to_excel(file_addr, index=False)
        return df.to_excel(file_addr)

    def to_phylip_matrix(
        self,
        file_addr: Union[Path, str],
        drop_constant: bool = False,
        proportion: bool = False,
        table_type: TableType = TableType.distance,
        show_ext: bool = False,
    ):
        """Writes this Collation as a PHYLIP-formatted distance/similarity matrix to the file with the given address.

        Args:
            file_addr: A string representing the path to an output PHYLIP file; the file type should be .ph or .phy.
            drop_constant: An optional flag indicating whether to ignore variation units with one substantive reading.
                Default value is False.
            proportion: An optional flag indicating whether or not to calculate distances as proportions over extant, unambiguous variation units.
                Default value is False.
            table_type: A TableType option indicating which type of tabular output to generate.
                For PHYLIP-formatted outputs, distance and similarity matrices are the only supported table types.
                Default value is "distance".
            show_ext: An optional flag indicating whether each cell in a distance or similarity matrix
                should include the number of their extant, unambiguous variation units after the number of their disagreements/agreements.
                Only applicable for tabular output formats of type \"distance\" or \"similarity\".
                Default value is False.
        """
        # Convert the collation to a Pandas DataFrame first:
        matrix = None
        witness_labels = []
        # Proceed based on the table type:
        if table_type == TableType.distance:
            # Convert the collation to a NumPy array and get its row and column labels first:
            matrix, witness_labels = self.to_distance_matrix(
                drop_constant=drop_constant, proportion=proportion, show_ext=show_ext
            )
        elif table_type == TableType.similarity:
            # Convert the collation to a NumPy array and get its row and column labels first:
            matrix, witness_labels = self.to_similarity_matrix(
                drop_constant=drop_constant, proportion=proportion, show_ext=show_ext
            )
        # Generate all parent folders for this file that don't already exist:
        Path(file_addr).parent.mkdir(parents=True, exist_ok=True)
        with open(file_addr, "w", encoding="utf-8") as f:
            # The first line contains the number of taxa:
            f.write("%d\n" % len(witness_labels))
            # Every subsequent line contains a witness label, followed by the values in its row of the matrix:
            for i, wit_id in enumerate(witness_labels):
                wit_label = slugify(wit_id, lowercase=False, allow_unicode=True, separator='_')
                f.write("%s %s\n" % (wit_label, " ".join([str(v) for v in matrix[i]])))
        return

    def get_stemma_symbols(self):
        """Returns a list of one-character symbols needed to represent the states of all substantive readings in STEMMA format.

        The number of symbols equals the maximum number of substantive readings at any variation unit.

        Returns:
            A list of individual characters representing states in readings.
        """
        possible_symbols = (
            list(string.digits) + list(string.ascii_lowercase) + list(string.ascii_uppercase)
        )  # NOTE: the maximum number of symbols allowed in STEMMA format (other than "?" and "-") is 62
        # The number of symbols needed is equal to the length of the longest substantive reading vector:
        nsymbols = 0
        # If there are no witnesses, then no symbols are needed at all:
        if len(self.witnesses) == 0:
            return []
        wit_id = self.witnesses[0].id
        for rdg_support in self.readings_by_witness[wit_id]:
            nsymbols = max(nsymbols, len(rdg_support))
        stemma_symbols = possible_symbols[:nsymbols]
        return stemma_symbols

    def to_stemma(self, file_addr: Union[Path, str]):
        """Writes this Collation to a STEMMA file without an extension and a Chron file (containing low, middle, and high dates for all witnesses) without an extension.

        Since this format does not support ambiguous states, all reading vectors with anything other than one nonzero entry will be interpreted as lacunose.

        Args:
            file_addr: A string representing the path to an output STEMMA prep file; the file should have no extension.
            The accompanying chron file will match this file name, except that it will have "_chron" appended to the end.
            drop_constant: An optional flag indicating whether to ignore variation units with one substantive reading.
        """
        # Populate a list of sites that will correspond to columns of the sequence alignment
        # (by default, constant sites are dropped):
        substantive_variation_unit_ids = [
            vu_id for vu_id in self.variation_unit_ids if len(self.substantive_readings_by_variation_unit_id[vu_id]) > 1
        ]
        substantive_variation_unit_ids_set = set(substantive_variation_unit_ids)
        substantive_variation_unit_reading_tuples_set = set(self.substantive_variation_unit_reading_tuples)
        # In a first pass, populate a dictionary mapping (variation unit index, reading index) tuples from the readings_by_witness dictionary
        # to the readings' texts:
        reading_texts_by_indices = {}
        for j, vu in enumerate(self.variation_units):
            if vu.id not in substantive_variation_unit_ids_set:
                continue
            k = 0
            for rdg in vu.readings:
                key = tuple([vu.id, rdg.id])
                if key not in substantive_variation_unit_reading_tuples_set:
                    continue
                indices = tuple([j, k])
                reading_texts_by_indices[indices] = rdg.text
                k += 1
        # In a second pass, populate another dictionary mapping (variation unit index, reading index) tuples from the readings_by_witness dictionary
        # to the witnesses exclusively supporting those readings:
        reading_wits_by_indices = {}
        for indices in reading_texts_by_indices:
            reading_wits_by_indices[indices] = []
        for i, wit in enumerate(self.witnesses):
            for j, vu_id in enumerate(self.variation_unit_ids):
                if vu_id not in substantive_variation_unit_ids_set:
                    continue
                rdg_support = self.readings_by_witness[wit.id][j]
                # If this witness does not exclusively support exactly one reading at this unit, then treat it as lacunose:
                if len([k for k, w in enumerate(rdg_support) if w > 0]) != 1:
                    continue
                k = rdg_support.index(1)
                indices = tuple([j, k])
                reading_wits_by_indices[indices].append(wit.id)
        # In a third pass, write to the STEMMA file:
        symbols = self.get_stemma_symbols()
        Path(file_addr).parent.mkdir(
            parents=True, exist_ok=True
        )  # generate all parent folders for this file that don't already exist
        chron_file_addr = str(file_addr) + "_chron"
        with open(file_addr, "w", encoding="utf-8") as f:
            # Start with the witness list:
            f.write("* %s ;\n\n" % " ".join([wit.id for wit in self.witnesses]))
            # f.write("^ %s\n\n" % chron_file_addr) #write the relative path to the chron file
            f.write(
                "^ %s\n\n" % ("." + os.sep + Path(chron_file_addr).name)
            )  # write the relative path to the chron file
            # Then add a line indicating that all witnesses are lacunose unless they are specified explicitly:
            f.write("= $? $* ;\n\n")
            # Then proceed for each variation unit:
            for j, vu_id in enumerate(self.variation_unit_ids):
                if vu_id not in substantive_variation_unit_ids_set:
                    continue
                # Print the variation unit ID first:
                f.write("@ %s\n" % vu_id)
                # In a first pass, print the texts of all readings enclosed in brackets:
                f.write("[ ")
                k = 0
                while True:
                    indices = tuple([j, k])
                    if indices not in reading_texts_by_indices:
                        break
                    text = slugify(
                        reading_texts_by_indices[indices], lowercase=False, allow_unicode=True, separator='.'
                    )
                    # Denote omissions by en-dashes:
                    if text == "":
                        text = "\u2013"
                    # The first reading should not be preceded by anything:
                    if k == 0:
                        f.write(text)
                        f.write(" |")
                    # Every subsequent reading should be preceded by a space:
                    elif k > 0:
                        f.write(" %s" % text)
                    k += 1
                f.write(" ]\n")
                # In a second pass, print the indices and witnesses for all readings enclosed in angle brackets:
                k = 0
                f.write("\t< ")
                while True:
                    indices = tuple([j, k])
                    if indices not in reading_wits_by_indices:
                        break
                    rdg_symbol = symbols[k]  # get the one-character alphanumeric code for this state
                    wits = " ".join(reading_wits_by_indices[indices])
                    # Open the variant reading support block with an angle bracket:
                    if k == 0:
                        f.write("%s %s" % (rdg_symbol, wits))
                    # Open all subsequent variant reading support blocks with pipes on the next line:
                    else:
                        f.write("\n\t| %s %s" % (rdg_symbol, wits))
                    k += 1
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
                # If either the lower bound on this witness's date is empty, then use the min and max dates over all witnesses as defaults:
                date_range = wit.date_range
                if date_range[0] is None:
                    date_range = tuple([min_date, date_range[1]])
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
        drop_constant: bool = False,
        split_missing: bool = True,
        char_state_labels: bool = True,
        frequency: bool = False,
        ambiguous_as_missing: bool = False,
        proportion: bool = False,
        calibrate_dates: bool = False,
        mrbayes: bool = False,
        clock_model: ClockModel = ClockModel.strict,
        ancestral_logger: AncestralLogger = AncestralLogger.state,
        table_type: TableType = TableType.matrix,
        show_ext: bool = False,
        seed: int = None,
    ):
        """Writes this Collation to the file with the given address.

        Args:
            file_addr (Union[Path, str]): The path to the output file.
            format (Format, optional): The desired output format.
                If None then it is infered from the file suffix.
                Defaults to None.
            drop_constant (bool, optional): An optional flag indicating whether to ignore variation units with one substantive reading.
                Default value is False.
            split_missing (bool, optional): An optional flag indicating whether to treat
                missing characters/variation units as having a contribution of 1 split over all states/readings;
                if False, then missing data is ignored (i.e., all states are 0).
                Not applicable for NEXUS, HENNIG86, PHYLIP, FASTA, or STEMMA format.
                Default value is True.
            char_state_labels (bool, optional): An optional flag indicating whether to print
                the CharStateLabels block in NEXUS output.
                Default value is True.
            frequency (bool, optional): An optional flag indicating whether to use the StatesFormat=Frequency setting
                instead of the StatesFormat=StatesPresent setting
                (and thus represent all states with frequency vectors rather than symbols)
                in NEXUS output.
                Note that this setting is necessary to make use of certainty degrees assigned to multiple ambiguous states in the collation.
                Default value is False.
            ambiguous_as_missing (bool, optional): An optional flag indicating whether to treat all ambiguous states as missing data.
                If this flag is set, then only base symbols will be generated for the NEXUS file.
                It is only applied if the frequency option is False.
                Default value is False.
            proportion (bool, optional): An optional flag indicating whether to populate a distance matrix's cells
                with a proportion of disagreements to variation units where both witnesses are extant.
                It is only applied if the table_type option is "distance".
                Default value is False.
            calibrate_dates (bool, optional): An optional flag indicating whether to add an Assumptions block that specifies date distributions for witnesses
                in NEXUS output.
                This option is intended for inputs to BEAST 2.
                Default value is False.
            mrbayes (bool, optional): An optional flag indicating whether to add a MrBayes block that specifies model settings and age calibrations for witnesses
                in NEXUS output.
                This option is intended for inputs to MrBayes.
                Default value is False.
            clock_model (ClockModel, optional): A ClockModel option indicating which type of clock model to use.
                This option is intended for inputs to MrBayes and BEAST 2.
                MrBayes does not presently support a local clock model, so it will default to a strict clock model if a local clock model is specified.
                Default value is "strict".
            ancestral_logger (AncestralLogger, optional): An AncestralLogger option indicating which class of logger (if any) to use for ancestral states.
                This option is intended for inputs to BEAST 2.
            table_type (TableType, optional): A TableType option indicating which type of tabular output to generate.
                Only applicable for tabular outputs and PHYLIP outputs.
                If the output is a PHYLIP file, then the type of tabular output must be "distance" or "similarity"; otherwise, it will be ignored.
                Default value is "matrix".
            show_ext (bool, optional): An optional flag indicating whether each cell in a distance or similarity matrix
                should include the number of variation units where both witnesses are extant after the number of their disagreements/agreements.
                Only applicable for tabular output formats of type "distance" or "similarity".
                Default value is False.
            seed (optional, int): A seed for random number generation (for setting initial values of unspecified transcriptional rates in BEAST 2 XML output).
        """
        file_addr = Path(file_addr)
        format = format or Format.infer(
            file_addr.suffix
        )  # an exception will be raised here if the format or suffix is invalid

        if format == Format.NEXUS:
            return self.to_nexus(
                file_addr,
                drop_constant=drop_constant,
                char_state_labels=char_state_labels,
                frequency=frequency,
                ambiguous_as_missing=ambiguous_as_missing,
                calibrate_dates=calibrate_dates,
                mrbayes=mrbayes,
                clock_model=clock_model,
            )

        if format == format.HENNIG86:
            return self.to_hennig86(file_addr, drop_constant=drop_constant)

        if format == format.PHYLIP:
            if table_type in [TableType.distance, TableType.similarity]:
                return self.to_phylip_matrix(
                    file_addr,
                    drop_constant=drop_constant,
                    proportion=proportion,
                    table_type=table_type,
                    show_ext=show_ext,
                )
            return self.to_phylip(file_addr, drop_constant=drop_constant)

        if format == format.FASTA:
            return self.to_fasta(file_addr, drop_constant=drop_constant)

        if format == format.BEAST:
            return self.to_beast(
                file_addr,
                drop_constant=drop_constant,
                clock_model=clock_model,
                ancestral_logger=ancestral_logger,
                seed=seed,
            )

        if format == Format.CSV:
            return self.to_csv(
                file_addr,
                drop_constant=drop_constant,
                ambiguous_as_missing=ambiguous_as_missing,
                proportion=proportion,
                table_type=table_type,
                split_missing=split_missing,
                show_ext=show_ext,
            )

        if format == Format.TSV:
            return self.to_csv(
                file_addr,
                drop_constant=drop_constant,
                ambiguous_as_missing=ambiguous_as_missing,
                proportion=proportion,
                table_type=table_type,
                split_missing=split_missing,
                show_ext=show_ext,
                sep="\t",
            )

        if format == Format.EXCEL:
            return self.to_excel(
                file_addr,
                drop_constant=drop_constant,
                ambiguous_as_missing=ambiguous_as_missing,
                proportion=proportion,
                table_type=table_type,
                split_missing=split_missing,
                show_ext=show_ext,
            )

        if format == Format.STEMMA:
            return self.to_stemma(file_addr)
