#!/usr/bin/env python3

from lxml import etree as et

from .common import xml_ns, tei_ns

class Reading():
    """Base class for storing TEI XML reading data internally.
    
    This can correspond to a lem, rdg, or witDetail element in the collation.

    Attributes:
        id: The ID string of this reading, which should be unique within its parent app element.
        type: A string representing the type of reading. Examples include "reconstructed", "defective", "orthographic", "subreading", "ambiguous", "overlap", and "lac". The default value is "substantive".
        text: Serialization of the contents of this element.
        wits: A list of sigla referring to witnesses that support this reading.
        targets: A list of other reading ID strings to which this reading corresponds. For substantive readings, this should be empty. For ambiguous readings, it should contain references to the readings that might correspond to this one. For overlap readings, it should contain a reference to the reading from the overlapping variation unit responsible for the overlap. 
        certainties: A dictionary mapping target reading IDs to floating-point certainty values.
    """
    def __init__(self, xml:et.Element=None, verbose:bool=False):
        """Constructs a new Reading instance from the TEI XML input.

        Args:
            xml: A lem, rdg, or witDetail element.
            verbose: An optional flag indicating whether or not to print status updates.
        """
        self.type = ""
        self.text = ""
        self.id = ""
        self.targets = []
        self.certainties = {}
        self.wits = []
        if xml is not None:
            self.parse(xml, verbose)
            if verbose:
                if len(self.wits) == 0:
                    if self.text != "":
                        print("New Reading %s with type %s, no witnesses, and text %s" % (self.id, self.type, self.text))
                    else:
                        print("New Reading %s with type %s, no witnesses, and no text" % (self.id, self.type))
                else:
                    if self.text != "":
                        print("New Reading %s with type %s, witnesses %s, and text %s" % (self.id, self.type, ", ".join([wit for wit in self.wits]), self.text))
                    else:
                        print("New Reading %s with type %s, witnesses %s, and no text" % (self.id, self.type, ", ".join([wit for wit in self.wits])))

    def parse(self, xml:et.Element, verbose:bool=False):
        """Given an XML element, recursively parses it and its subelements.

        Args:
            xml: A lem, rdg, or witDetail element.
            verbose: An optional flag indicating whether or not to print status updates.
        """
        # Determine what this element is:
        raw_tag = xml.tag.replace("{%s}" % tei_ns, "")
        # If it is a reading or lemma, then copy its witnesses, and recursively process its children:
        if raw_tag in ["rdg", "lem"]:
            # If it has a type, then save that; otherwise, default to "substantive":
            self.type = xml.get("type") if xml.get("type") is not None else "substantive"
            # Populate its list of the entries in its wit attribute (stripping any "#" prefixes), split over spaces:
            self.wits = [w.strip("#") for w in xml.get("wit").split()] if xml.get("wit") is not None else []
            # Populate its text recursively using its children:
            self.text = xml.text if xml.text is not None else ""
            for child in xml:
                self.parse(child, verbose)
            # Strip any surrounding whitespace left over from spaces added between word elements:
            self.text = self.text.strip()
            # Populate its ID, using its xml:id if it has one; otherwise, use its n attribute if it has one; otherwise, use its text:
            self.id = ""
            if xml.get("{%s}id" % xml_ns) is not None:
                self.id = xml.get("{%s}id" % xml_ns)
            elif xml.get("n") is not None:
                self.id = xml.get("n")
            else:
                self.id = self.text
            return
        # If it is a witness detail (e.g., an ambiguous reading), then copy its target readings and witnesses, and recursively process its children:
        if raw_tag == "witDetail":
            # If it has a type, then save that; otherwise, default to "substantive":
            self.type = xml.get("type") if xml.get("type") is not None else "substantive"
            # Populate its list of target reading IDs in its target attribute (stripping any "#" prefixes), split over spaces:
            self.targets = [t.strip("#") for t in xml.get("target").split()] if xml.get("target") is not None else []
            # Populate its list of the entries in its wit attribute (stripping any "#" prefixes), split over spaces:
            self.wits = [w.strip("#") for w in xml.get("wit").split()] if xml.get("wit") is not None else []
            # Populate its certainties map and text recursively using its children:
            self.certainties = {}
            for t in self.targets:
                self.certainties[t] = 0
            self.text = xml.text if xml.text is not None else ""
            for child in xml:
                self.parse(child, verbose)
            # Normalize its certainties map:
            norm = sum(self.certainties.values())
            if norm == 0:
                # If the norm is zero, then presumably no certainty elements were included under this element;
                # just set the value for each target to 1 and normalize as usual:
                for t in self.targets:
                    self.certainties[t] = 1
                    norm += 1
            if norm > 0:
                for t in self.certainties:
                    self.certainties[t] = self.certainties[t]/norm
            # Strip any surrounding whitespace left over from spaces added between word elements:
            self.text = self.text.strip()
            # Populate its ID, using its xml:id if it has one; otherwise, use its n attribute if it has one; otherwise, use its text:
            self.id = ""
            if xml.get("{%s}id" % xml_ns) is not None:
                self.id = xml.get("{%s}id" % xml_ns)
            elif xml.get("n") is not None:
                self.id = xml.get("n")
            else:
                self.id = self.text
            return
        # If it is a certainty measurement, then store its value in this reading's certainties map
        # (overwriting any previous values for this reading in the map, since they shouldn't be specified more than once):
        if raw_tag == "certainty":
            # Get its target reading IDs (stripping any "#" prefixes):
            targets = [t.strip("#") for t in xml.get("target").split()] if xml.get("target") is not None else []
            # Now set the entry for each target reading to that degree;
            # if no degree is specified, then assume that all targets are equally likely and assign them all a value of 1 (we will normalize at the end):
            degree = float(xml.get("degree")) if xml.get("degree") is not None else 1
            for t in targets:
                self.certainties[t] = degree
            return
        # If it is a word, then serialize its text and tail, 
        # recursively processing any subelements,
        # and add a space after it:
        if raw_tag == "w":
            self.text += xml.text if xml.text is not None else ""
            for child in xml:
                self.parse(child, verbose)
            self.text += xml.tail if xml.tail is not None else ""
            self.text += " "
            return
        # If it is an abbreviation, then serialize its text and tail, 
        # recursively processing any subelements:
        if raw_tag == "abbr":
            self.text += xml.text if xml.text is not None else ""
            for child in xml:
                self.parse(child, verbose)
            self.text += xml.tail if xml.tail is not None else ""
            return
        # If it is an overline-rendered element, then add an overline to each character in its contents:
        if raw_tag == "hi":
            # Keep track of how long the text currently is, so we can modify just the portion we're about to add:
            starting_ind = len(self.text)
            self.text += xml.text if xml.text is not None else ""
            # for child in xml:
            #     self.parse(child, verbose)
            # NOTE: other rendering types could be supported here
            if xml.get("rend") is not None:
                old_text = self.text[starting_ind:]
                rend = xml.get("rend")
                if rend == "overline":
                    new_text = "".join([c + "\u0305" for c in old_text])
                    self.text = self.text[:starting_ind] + new_text
            self.text += xml.tail if xml.tail is not None else ""
            return
        # If it is a space, then serialize as a single space:
        if raw_tag == "space":
            text = "["
            if xml.get("unit") is not None and xml.get("extent") is not None:
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
            text += xml.tail if xml.tail is not None else ""
            self.text += text
            return
        # If it is an expansion, then serialize it in parentheses:
        if raw_tag == "ex":
            self.text += "("
            self.text += xml.text if xml.text is not None else ""
            # for child in xml:
            #     self.parse(child, verbose)
            self.text += ")"
            self.text += xml.tail if xml.tail is not None else ""
            return
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
            text += xml.tail if xml.tail is not None else ""
            self.text += text
            return
        # If it is a supplied element, then recursively set the contents in brackets:
        if raw_tag == "supplied":
            self.text += "["
            self.text += xml.text if xml.text is not None else ""
            for child in xml:
                self.parse(child, verbose)
            self.text += "]"
            self.text += xml.tail if xml.tail is not None else ""
            return
        # If it is an unclear element, then add an underdot to each character in its contents:
        if raw_tag == "unclear":
            # Keep track of how long the text currently is, so we can modify just the portion we're about to add:
            starting_ind = len(self.text)
            self.text += xml.text if xml.text is not None else ""
            for child in xml:
                self.parse(child, verbose)
            old_text = self.text[starting_ind:].strip() # strip any trailing spaces (in case there were entire words whose presence is unclear)
            new_text = ""
             # Add a dot under each character other than spaces:
            for c in old_text:
                new_text += c
                if c != " ":
                    new_text += "\u0323"
            self.text = self.text[:starting_ind] + new_text
            self.text += xml.tail if xml.tail is not None else ""
            return
        # If it is a choice element, then recursively set the contents in brackets, separated by slashes:
        if raw_tag == "choice":
            self.text += "["
            self.text += xml.text if xml.text is not None else ""
            for child in xml:
                self.parse(child, verbose)
                self.text = self.text.strip() + "/" # add a slash between each possibility
            self.text = self.text.strip("/") # remove the last one we added
            self.text += "]"
            self.text += xml.tail if xml.tail is not None else ""
            return
        # If it is a ref element, then set its text (stripped of "#" characters) in diagonal brackets:
        if raw_tag == "ref":
            self.text += "<"
            self.text += xml.get("target").strip("#") if xml.get("target") is not None else ""
            self.text += ">"
            self.text += xml.tail if xml.tail is not None else ""
            return