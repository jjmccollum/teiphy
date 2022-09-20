#!/usr/bin/env python3

from lxml import etree as et

from .common import xml_ns, tei_ns


class Witness:
    """Base class for storing TEI XML witness data internally.

    This corresponds to a witness element in the collation.

    Attributes:
        id: The ID string of this Witness. It should be unique.
        type: A string representing the type of witness. Examples include "corrector", "version", and "father".
        date_range: A tuple containing a low and high date for this Witness.
    """

    def __init__(self, xml: et.Element, verbose: bool = False):
        """Constructs a new Witness instance from the TEI XML input.

        Args:
            xml: A witness element.
            verbose: An optional flag indicating whether or not to print status updates.
        """
        # Use its xml:id if it has one; otherwise, use its n attribute if it has one; otherwise, use its text:
        self.id = ""
        if xml.get("{%s}id" % xml_ns) is not None:
            self.id = xml.get("{%s}id" % xml_ns)
        elif xml.get("n") is not None:
            self.id = xml.get("n")
        else:
            self.id = xml.text
        # If it has a type, then save that; otherwise, default to "manuscript":
        self.type = xml.get("type") if xml.get("type") is not None else "manuscript"
        # If it has an origDate descendant, then use the dates in its attributes:
        self.date_range = tuple([None, None])
        for orig_date in xml.xpath(".//tei:origDate", namespaces={"tei": tei_ns}):
            date_range = [None, None]
            # Try the @when attribute first; if it is set, then it accounts for both ends of the date range:
            if orig_date.get("when") is not None:
                date_range[0] = int(orig_date.get("when"))
                date_range[1] = date_range[0]
            # Failing that, try the @from and @to attributes:
            elif orig_date.get("from") is not None or orig_date.get("to") is not None:
                if orig_date.get("from") is not None or orig_date.get("to") is not None:
                    date_range[0] = int(orig_date.get("from"))
                if orig_date.get("to") is not None:
                    date_range[1] = int(orig_date.get("to"))
            # Failing that, try the @notBefore and @notAfter attributes:
            elif orig_date.get("notBefore") is not None or orig_date.get("notAfter") is not None:
                if orig_date.get("notBefore") is not None:
                    date_range[0] = int(orig_date.get("notBefore"))
                if orig_date.get("notAfter") is not None:
                    date_range[1] = int(orig_date.get("notAfter"))
            # If, at this point, only one end of the date range is defined, then set the other end to match it:
            if date_range[0] is None and date_range[1] is not None:
                date_range[0] = date_range[1]
            elif date_range[0] is not None and date_range[1] is None:
                date_range[1] = date_range[0]
            self.date_range = tuple(date_range)
            break

        if verbose:
            print("New Witness (id: %s, type: %s, date_range: %s)" % (self.id, self.type, str(self.date_range)))
