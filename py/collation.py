#!/usr/bin/env python3

import time # to time calculations for users
import re # for parsing augmented witness sigla
import string # for easy retrieval of character ranges
from lxml import etree as et # for reading TEI XML inputs

from common import xml_ns, tei_ns # import namespace variables from the common support module

"""
Base class for storing TEI XML witness data internally.
"""
class witness():
    """
    Constructs a new witness instance from the TEI XML input.
    """
    def __init__(self, xml, verbose=False):
        # If it has a type, then save that; otherwise, default to "manuscript":
        self.type = xml.get("type") if xml.get("type") is not None else "manuscript"
        # Use its xml:id if it has one; otherwise, use its n attribute if it has one; otherwise, use its text:
        self.id = ""
        if xml.get("{%s}id" % xml_ns) is not None:
            self.id = xml.get("{%s}id" % xml_ns)
        elif xml.get("n") is not None:
            self.id = xml.get("n")
        else:
            self.id = xml.text
        if verbose:
            print("New witness %s with type %s" % (self.id, self.type))

"""
Base class for storing TEI XML reading data internally.
This can correspond to a <lem>, <rdg>, or <witDetail> element in the collation.
"""
class reading():
    """
    Constructs a new reading instance from the TEI XML input.
    """
    def __init__(self, xml, verbose=False):
        # If it has a type, then save that; otherwise, default to "substantive":
        self.type = xml.get("type") if xml.get("type") is not None else "substantive"
        # Serialize its contents:
        self.text = serialize(xml)
        # Use its xml:id if it has one; otherwise, use its n attribute if it has one; otherwise, use its text:
        self.id = ""
        if xml.get("{%s}id" % xml_ns) is not None:
            self.id = xml.get("{%s}id" % xml_ns)
        elif xml.get("n") is not None:
            self.id = xml.get("n")
        else:
            self.id = xml.text
        # Save a list of the targets in its target attribute (stripping any "#" prefixes), split over spaces:
        self.targets = [t.strip("#") for t in xml.get("target").split()] if xml.get("target") is not None else []
        # Save a list of the entries in its wit attribute (stripping any "#" prefixes), split over spaces:
        self.wits = [t.strip("#") for w in xml.get("wit").split()] if xml.get("wit") is not None else []
        if verbose:
            print("New reading %s with type %s, witnesses %s, and text %s" % (self.id, self.n, self.type, " ".join(wit in self.wits), text))

    """
    Given an XML element, recursively serializes it in a more readable format.
    """
    def serialize(self, xml):
        # Determine what this element is:
        raw_tag = xml.tag.replace("{%s}" % tei_ns, "")
        # If it is a reading, then serialize its children, separated by spaces:
        if raw_tag == "rdg":
            text = "" if xml.text is None else xml.text
            text += " ".join([self.serialize(child) for child in xml])
            return text
        # If it is a word, abbreviation, or overline-rendered element, then serialize its text and tail, 
        # recursively processing any subelements:
        if raw_tag in ["w", "abbr"]:
            text = "" if xml.text is None else xml.text
            text += "".join([self.serialize(child) for child in xml])
            text += "" if xml.tail is None else xml.tail
            return text
        # If it is an overline-rendered element, then add an overline to each character in its contents:
        if raw_tag == "hi":
            text = ""
            text += "" if xml.text is None else xml.text
            text += " ".join([self.serialize(child) for child in xml])
            # NOTE: other rendering types could be supported here
            if xml.get("rend") is not None:
                rend = xml.get("rend")
                if rend == "overline":
                    text = "".join([c + "\u0305" for c in text])
            text += "" if xml.tail is None else xml.tail
            return text
        # If it is a space, then serialize as a single space:
        if raw_tag == "space":
            text = "["
            if xml.get("unit") is not None and xml.get("extent") is not None:
                text += ", "
                unit = xml.get("unit")
                extent = xml.get("extent")
                text += extent + " " + unit
                text += " "
                text += "space"
            else:
                text += "space"
            if xml.get("reason") is not None:
                text += " "
                reason = xml.get("reason")
                text += "(" + reason + ")"
            text += "]"
            text += "" if xml.tail is None else xml.tail
            return text
        # If it is an expansion, then serialize it in parentheses:
        if raw_tag == "ex":
            text = ""
            text += "("
            text += "" if xml.text is None else xml.text
            text += " ".join([self.serialize(child) for child in xml])
            text += ")"
            text += "" if xml.tail is None else xml.tail
            return text
        # If it is a gap, then serialize it based on its attributes:
        if raw_tag == "gap":
            text = ""
            text += "["
            if xml.get("unit") is not None and xml.get("extent") is not None:
                unit = xml.get("unit")
                extent = xml.get("extent")
                text += extent + " " + unit
                text += " "
                text += "gap"
            else:
                text += "..." # placeholder text for gap if no unit and extent are specified
            if xml.get("reason") is not None:
                text += " "
                reason = xml.get("reason")
                text += "(" + reason + ")"
            text += "]"
            text += "" if xml.tail is None else xml.tail
            return text
        # If it is a supplied element, then recursively set the contents in brackets:
        if raw_tag == "supplied":
            text = ""
            text += "["
            text += "" if xml.text is None else xml.text
            text += " ".join([self.serialize(child) for child in xml])
            text += "]"
            text += "" if xml.tail is None else xml.tail
            return text
        # If it is an unclear element, then add an underdot to each character in its contents:
        if raw_tag == "unclear":
            text = ""
            text += "" if xml.text is None else xml.text
            text += " ".join([self.serialize(child) for child in xml])
            text = "".join([c + "\u0323" for c in text])
            text += "" if xml.tail is None else xml.tail
            return text
        # If it is a choice element, then recursively set the contents in brackets, separated by slashes:
        if raw_tag == "choice":
            text = ""
            text += "["
            text += "" if xml.text is None else xml.text
            text += "/".join([self.serialize(child) for child in xml])
            text += "]"
            text += "" if xml.tail is None else xml.tail
            return text
        # If it is a ref element, then set its text in brackets:
        if raw_tag == "ref":
            text = ""
            text += "["
            text += "" if xml.text is None else xml.text
            text += "]"
            text += "" if xml.tail is None else xml.tail
            return text
        # For all other elements, return an empty string:
        return ""

"""
Base class for storing TEI XML variation unit data internally.
"""
class variation_unit():
    """
    Constructs a new variation_unit instance from the TEI XML input.
    """
    def __init__(self, xml, verbose=False):
        # If it has a type, then save that; otherwise, default to "substantive":
        self.type = xml.get("type") if xml.get("type") is not None else "substantive"
        # Use its xml:id if it has one; otherwise, use its n attribute if it has one:
        self.id = None
        if xml.get("{%s}id" % xml_ns) is not None:
            self.id = xml.get("{%s}id" % xml_ns)
        elif xml.get("n") is not None:
            self.id = xml.get("n")
        # Initialize its list of readings:
        self.readings = []
        # Now parse the XML <app> element to populate these data structures:
        self.parse(xml, verbose)
        if verbose:
            print("New variation_unit %s of type %s with %d substantive readings" % (self.id, self.type, len(self.readings)))

    """
    Given an XML element, recursively parses its subelements for readings and reading groups.
    Other children of <app> elements, such as <note>, <noteGrp>, and <wit> elements, are ignored.
    """
    def parse(self, xml, verbose)
        # Determine what this element is:
        raw_tag = xml.tag.replace("{%s}" % tei_ns, "")
        # If it is an apparatus, then initialize the readings list and process the child elements of the apparatus recursively:
        if raw_tag == "app":
            self.readings = []
            for child in xml:
                self.parse(xml, verbose)
            return
        # If it is a reading group, then flatten it by processing its children recursively, applying the reading group's type to the readings contained in it:
        if raw_tag == "rdgGrp":
            # Get the type of this reading group:
            reading_group_type = xml.get("type") if xml.get("type") is not None else None
            for child in xml:
                child_raw_tag = child.tag.replace("{%s}" % tei_ns, "")
                if child_raw_tag in ["lem", "rdg"]: # any <lem> element in a <rdgGrp> can be assumed not to be a duplicate of a <rdg> element, as there should be only one <lem> at all levels under an <app> element
                    rdg = reading(child, verbose)
                    if rdg.type is not None:
                        rdg.type = reading_group_type
                    self.readings.append(rdg)
                else:
                    self.parse(child, verbose)
            return
        # If it is a lemma, then add it as a reading if has its own witness list (even if that list is empty, which may occur for a conjecture);
        # otherwise, assume its reading is duplicated in a <rdg> element and skip it:
        if raw_tag == "lem":
            if xml.get("wit") is not None:
                lem = reading(xml, verbose)
                self.readings.append(lem)
            return
        # If it is a reading, then add it as a reading:
        elif raw_tag == "rdg":
            rdg = reading(child, verbose)
            self.readings.append(rdg)
            return
        # If it is a witness detail, then add it as a reading, and if it does not have any targeted readings, then add a target for the previous reading (per the TEI Guidelines §12.1.4.1):
        elif raw_tag == "witDetail":
            witDetail = reading(child, verbose)
            if len(witDetail.targets) == 0 and len(self.readings) > 0:
                previous_rdg = self.readings[-1]
                witDetail.targets.append(previous_rdg.id)
            self.readings.append(witDetail)
            return

"""
Base class for storing TEI XML collation data internally.
"""
class collation():
    """
    Constructs a new collation instance with the given settings.
    """
    def __init__(self, xml, manuscript_suffixes=[], trivial_reading_types=[], missing_reading_types=[], verbose=False):
        self.manuscript_suffixes = manuscript_suffixes # list of suffixes used to distinguish manuscript subwitnesses like first hands, correctors, main texts, alternate texts, and multiple attestations from their base witnesses
        self.trivial_reading_types = set(trivial_reading_types) # set of reading types (e.g., defective, orthographic, subreading) whose readings should be collapsed under the previous substantive reading
        self.missing_reading_types = set(missing_reading_types) # set of reading types (e.g., lacunose, overlap) whose readings should be treated as missing data
        self.verbose = verbose # flag indicating whether or not to print timing and debugging details for the user
        self.witnesses = [] # a list of witness instances
        self.witness_index_by_id = {} # a dictionary mapping base witness IDs to their indices in the above list
        self.variation_units = [] # a list of variation_unit instances
        self.readings_by_witness = {} # a dictionary mapping base witness IDs to a list of reading support sets for all units (with at least two substantive readings)
        # Now parse the XML tree to populate these data structures:
        self.parse_list_wit(xml, verbose)
        self.parse_apps(xml, verbose)
        self.parse_readings_by_witness(verbose)

    """
    Given an XML tree for a collation, populates its list of witnesses from its <listWit> element.
    """
    def parse_list_wit(self, xml, verbose=False):
        self.witnesses = []
        self.witness_index_by_id = {}
        for w in xml.xpath("/tei:TEI/tei:teiHeader/tei:fileDesc/tei:sourceDesc/tei:listWit/tei:witness", namespaces={"tei": tei_ns}):
            wit = witness(w, verbose)
            self.witness_index_by_id[wit.id] = len(self.witnesses)
            self.witnesses.append(wit)
        if verbose:
            print("Finished processing %d witnesses." % len(self.witnesses))
        return

    """
    Given an XML tree for a collation, populates its list of variation units from its <app> elements.
    """
    def parse_apps(self, xml, verbose=False):
        for a in xml.xpath('//tei:app', namespaces={'tei': tei_ns}):
            vu = variation_unit(a, verbose)
            self.variation_units.append(vu)
        if verbose:
            print("Finished processing %d variation units." % len(self.variation_units))
        return

    """
    Given a witness siglum (assumed to be for a manuscript witness), returns the base siglum of the witness, stripped of all subwitness suffixes.
    """
    def get_base_wit(self, wit):
        base_wit = wit
        while (True):
            suffix_found = False
            for suffix in self.manuscript_suffixes:
                if base_wit.endswith(suffix):
                    suffix_found = True
                    base_wit = base_wit[:-len(suffix)]
                    break
            if not suffix_found:
                break
        return base_wit

    """
    Returns a dictionary mapping witness IDs to a set of their readings for a given variation unit.
    """
    def get_readings_by_witness_for_unit(self, vu, verbose=False):
        # In a first pass, populate a list of substantive readings and a map from reading IDs to the indices of their parent substantive reading in this unit:
        substantive_reading_ids = []
        reading_id_to_index = {}
        for rdg in vu.readings:
            # If this reading is missing (e.g., lacunose or inapplicable due to an overlapping variant) or targets another reading, then skip it:
            if rdg.type in self.missing_reading_types or len(rdg.targets) > 0:
                continue
            # If this reading is trivial, then map it to the last substantive index:
            if rdg.type in self.trivial_reading_types:
                reading_id_to_index[rdg.id] = len(substantive_reading_ids) - 1
                continue
            # Otherwise, the reading is substantive: add it to the map and update the last substantive index:
            substantive_reading_ids.append(rdg.id)
            reading_id_to_index[rdg.id] = len(substantive_reading_ids) - 1
        # If the list of substantive readings only contains one entry, then this variation unit is not informative;
        # return an empty dictionary:
        readings_by_witness_for_unit = {}
        if len(substantive_reading_ids) <= 1:
            return readings_by_witness_for_unit
        # Otherwise, initialize the output dictionary with empty sets for all base witnesses:
        for wit in self.witnesses:
            readings_by_witness_for_unit[wit.id] = set()
        # In a second pass, assign each base witness a set containing the readings it supports in this unit:
        for rdg in vu.readings:
            # Initialize the set indicating support for this reading (or its disambiguations):
            rdg_support = set()
            # If this is a missing reading (e.g., a lacuna or an overlap), then we can skip this reading, as its corresponding set will be empty:
            if rdg.type in self.missing_reading_types:
                continue
            # If this reading is trivial, then it will contain an entry for the index of its parent substantive reading:
            if rdg.type in self.trivial_reading_types:
                rdg_support.add(reading_id_to_index[rdg.id])
            # Otherwise, if this reading has one or more target readings, then add an entry for the index of each of those readings:
            elif len(rdg.targets) > 0:
                for t in rdg.targets:
                    rdg_support.add(reading_id_to_index[t])
            # Proceed for each witness siglum in the support for this reading:
            for wit in rdg.wits:
                # Is this siglum a base siglum?
                base_wit = wit
                if base_wit not in self.witness_index_by_id:
                    # If not, then assume it is a manuscript witness, strip any of the specified suffixes from it, 
                    # and check if the resulting siglum is a base siglum:
                    base_wit = self.get_base_wit(wit)
                    if base_wit not in self.witness_index_by_id:
                        # If it is not, then it is probably just because we've encountered a corrector or some other secondary witness not included in the witness list;
                        # report this if we're in verbose mode and move on:
                        if verbose:
                            print("Skipping witness siglum %s (base siglum %s) in variation unit %s, reading %s..." % (wit, base_wit, vu.id, rdg.id))
                        continue
                # If we've found a base siglum, then add this reading's contribution to the base witness's reading set for this unit;
                # normally the existing set will be empty, but if we reduce two suffixed sigla to the same base witness, 
                # then that witness may attest to multiple readings in the same unit:
                readings_by_witness_for_unit[wit.id] = readings_by_witness_for_unit[wit.id].union(rdg_support)
        return readings_by_witness_for_unit

    """
    Populates the internal dictionary mapping witness IDs to a list of their reading support sets for all variation units.
    """
    def parse_readings_by_witness(self, verbose=False):
        # Initialize the output dictionary with empty lists for all base witnesses:
        self.readings_by_witness = {}
        for wit in self.witnesses:
            readings_by_witness[wit.id] = []
        # Populate it for each variation unit:
        for vu in self.variation_units:
            readings_by_witness_for_unit = self.get_readings_by_witness_for_unit(vu, verbose)
            for wit in readings_by_witness_for_unit:
                readings_by_witness[wit.id].append(readings_by_witness_for_unit[wit.id])
        return

    """
    Returns the number of taxa representing the base witnesses covered in this collation.
    """
    def get_nexus_ntax(self):
        return len(self.witnesses)

    """
    Returns the number of characters (i.e., sites, variation units) covered in this collation.
    Note that not all units detailed in the collation will necessarily be included in this count;
    Only units with two or more substantive readings will be included in the NEXUS output and counted here.
    """
    def get_nexus_nchars(self):
        # If the witnesses list is empty, then by necessity the collation matrix should be empty:
        if len(self.witnesses) == 0:
            return 0
        # Otherwise, all rows should have the same number of characters; use the first row:
        wit_id = self.witnesses[0].id
        return len(self.readings_by_witness[wit_id])

    """
    Returns different symbols or lists of symbols needed to represent the states of all substantive readings in NEXUS.
    """
    def get_nexus_symbol_lists(self):
        possible_symbols = list(string.digits) + list(string.ascii_letters)
        covered_singleton_sequences = set() # which singleton sets of individual readings have been covered already?
        covered_mixed_sequences = set() # which mixed sets of readings have been covered already?
        # Proceed first for each witness, then for each variation unit:
        for wit in self.witnesses:
            wit_id = wit.id
            for rdg_support in self.readings_by_witness[wit_id]:
                # Skip any empty sets for missing readings (the '?' symbol is already reserved for these):
                if len(rdg_support) == 0:
                    continue
                # For any singleton sets, add them as tuples to the set of singleton reading sequences:
                if len(rdg_support) == 1:
                    t = tuple(rdg_support)
                    covered_singleton_sequences.add(t)
                    continue
                # For any mixed sets, add them as tuples to the set of mixed reading sequences:
                if len(rdg_support) > 1:
                    t = tuple(rdg_support)
                    covered_mixed_sequences.add(t)
                    continue
        missing_symbol = '?'
        base_symbols = possible_symbols[:len(covered_singleton_sequences)]
        equate_symbols_by_sequence = {}
        for i, t in enumerate(covered_mixed_sequences):
            equate_symbol = possible_symbols[len(covered_singleton_sequences) + i]
            equate_tuple = tuple([possible_symbols[j] for j in t])
            equate_symbols_by_sequence[equate_symbol] = equate_tuple
        return missing_symbol, base_symbols, equate_symbols_by_sequence