#!/usr/bin/env python3

from lxml import etree as et

from .common import xml_ns, tei_ns


class Witness:
    """Base class for storing TEI XML witness data internally.

    This corresponds to a witness element in the collation.

    Attributes:
        id: The ID string of this Witness. It should be unique.
        type: A string representing the type of witness. Examples include "corrector", "version", and "father".
    """

    def __init__(self, xml: et.Element, verbose: bool = False):
        """Constructs a new Witness instance from the TEI XML input.

        Args:
            xml: A witness element.
            verbose: An optional flag indicating whether or not to print status updates.
        """
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
            print("New Witness %s with type %s" % (self.id, self.type))
