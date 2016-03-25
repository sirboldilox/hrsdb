"""
Config reader 
"""

from configparser import ConfigParser, NoSectionError, ParsingError

# Defaults


class SiteConfig(ConfigParser):
    """Configuration options for the site.
    Raises exceptions if the required sections are missing
    """
    required_sections = ['flask', 'database']


    @classmethod
    def from_file(cls, filename):
        conf = SiteConfig()
        if not conf.read([filename]):
            raise ParsingError("Failed to parse file: %s" % filename)

        # Check sections
        for section in cls.required_sections:
            if not conf.has_section(section):
                raise NoSectionError("Missing section: %s" % section) 

        return conf

