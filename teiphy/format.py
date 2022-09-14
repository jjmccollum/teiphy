from enum import Enum


class FormatUnknownException(Exception):
    pass


class Format(Enum):
    NEXUS = 'NEXUS'
    HENNIG86 = 'HENNIG86'
    CSV = 'CSV'
    TSV = 'TSV'
    EXCEL = 'EXCEL'
    STEMMA = 'STEMMA'

    @classmethod
    def infer(cls, suffix: str):
        suffix_map = {
            ".nex": cls.NEXUS,
            ".nexus": cls.NEXUS,
            ".nxs": cls.NEXUS,
            ".tnt": cls.HENNIG86,
            ".csv": cls.CSV,
            ".tsv": cls.TSV,
            ".xlsx": cls.EXCEL,
        }

        suffix_lower = suffix.lower()
        if suffix_lower in suffix_map:
            return suffix_map[suffix_lower]

        allowed_suffixes = ', '.join(suffix_map.keys())
        raise FormatUnknownException(
            f"Cannot infer format from suffix '{suffix}'. " f"Please set explicitly or use one of: {allowed_suffixes}."
        )
