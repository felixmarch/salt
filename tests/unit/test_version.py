# -*- coding: utf-8 -*-
'''
    :codeauthor: Pedro Algarvio (pedro@algarvio.me)


    tests.unit.version_test
    ~~~~~~~~~~~~~~~~~~~~~~~

    Test salt's regex git describe version parsing
'''

# Import python libs
from __future__ import absolute_import
import re

# Import Salt Testing libs
from tests.support.unit import TestCase

# Import Salt libs
from salt.version import SaltStackVersion, versions_report


class VersionTestCase(TestCase):
    def test_version_parsing(self):
        strip_initial_non_numbers_regex = re.compile(r'(?:[^\d]+)?(?P<vs>.*)')
        expect = (
            ('v0.12.0-19-g767d4f9', (0, 12, 0, 0, '', 0, 19, 'g767d4f9'), None),
            ('v0.12.0-85-g2880105', (0, 12, 0, 0, '', 0, 85, 'g2880105'), None),
            ('debian/0.11.1+ds-1-3-ga0afcbd',
             (0, 11, 1, 0, '', 0, 3, 'ga0afcbd'), '0.11.1-3-ga0afcbd'),
            ('0.12.1', (0, 12, 1, 0, '', 0, 0, None), None),
            ('0.12.1', (0, 12, 1, 0, '', 0, 0, None), None),
            ('0.17.0rc1', (0, 17, 0, 0, 'rc', 1, 0, None), None),
            ('v0.17.0rc1-1-g52ebdfd', (0, 17, 0, 0, 'rc', 1, 1, 'g52ebdfd'), None),
            ('v2014.1.4.1', (2014, 1, 4, 1, '', 0, 0, None), None),
            ('v2014.1.4.1rc3-n/a-abcdefgh', (2014, 1, 4, 1, 'rc', 3, -1, 'abcdefgh'), None),
            ('v3.4.1.1', (3, 4, 1, 1, '', 0, 0, None), None),
            ('v3000', (3000, None, None, 0, '', 0, 0, None), None)

        )

        for vstr, full_info, version in expect:
            saltstack_version = SaltStackVersion.parse(vstr)
            self.assertEqual(
                saltstack_version.full_info, full_info
            )
            if version is None:
                version = strip_initial_non_numbers_regex.search(vstr).group('vs')
            self.assertEqual(saltstack_version.string, version)

    def test_version_comparison(self):
        examples = (
            ('debian/0.11.1+ds-1-3-ga0afcbd', '0.11.1+ds-2'),
            ('v0.12.0-85-g2880105', 'v0.12.0-19-g767d4f9'),
            ('v0.17.0rc1-1-g52ebdfd', '0.17.0rc1'),
            ('v0.17.0', 'v0.17.0rc1'),
            ('Hydrogen', '0.17.0'),
            ('Helium', 'Hydrogen'),
            ('v2014.1.4.1-n/a-abcdefgh', 'v2014.1.4.1rc3-n/a-abcdefgh'),
            ('v2014.1.4.1-1-abcdefgh', 'v2014.1.4.1-n/a-abcdefgh'),
            ('v2016.12.0rc1', 'v2016.12.0b1'),
            ('v2016.12.0beta1', 'v2016.12.0alpha1'),
            ('v2016.12.0alpha1', 'v2016.12.0alpha0'),
            ('v3000.1', 'v3000'),
            ('v3000rc2', 'v3000rc1'),
            ('v3001', 'v3000'),
            ('v4023rc1', 'v4022rc1'),
            ('v3000', 'v3000rc1'),
            ('v3000', 'v2019.2.1'),
            ('v3000.1', 'v2019.2.1'),
            # we created v3000.0rc1 tag on repo
            # but we should not be using this
            # version scheme in the future
            # but still adding test for it
            ('v3000', 'v3000.0rc1'),
        )
        for higher_version, lower_version in examples:
            self.assertTrue(SaltStackVersion.parse(higher_version) > lower_version)
            self.assertTrue(SaltStackVersion.parse(lower_version) < higher_version)
            assert SaltStackVersion.parse(lower_version) != higher_version

    def test_unparsable_version(self):
        with self.assertRaises(ValueError):
            SaltStackVersion.from_name('Drunk')

        with self.assertRaises(ValueError):
            SaltStackVersion.parse('Drunk')

    def test_version_report_lines(self):
        '''
        Validate padding in versions report is correct
        '''
        # Get a set of all version report name lenghts including padding
        line_lengths = set([
           len(line.split(':')[0]) for line in list(versions_report())[4:]
           if line != ' ' and line != 'System Versions:'
        ])
        # Check that they are all the same size (only one element in the set)
        assert len(line_lengths) == 1

    def test_string_new_version(self):
        '''
        Validate string property method
        using new versioning scheme
        '''
        maj_ver = '3000'
        ver = SaltStackVersion(major=maj_ver)
        assert not ver.minor
        assert not ver.bugfix
        assert maj_ver == ver.string

    def test_string_new_version_minor(self):
        '''
        Validate string property method
        using new versioning scheme alongside
        minor version
        '''
        maj_ver = 3000
        min_ver = 1
        ver = SaltStackVersion(major=maj_ver, minor=min_ver)
        assert ver.minor == min_ver
        assert not ver.bugfix
        assert ver.string == '{0}.{1}'.format(maj_ver, min_ver)

    def test_string_old_version(self):
        '''
        Validate string property method
        using old versioning scheme alongside
        minor version
        '''
        maj_ver = '2019'
        min_ver = '2'
        ver = SaltStackVersion(major=maj_ver, minor=min_ver)
        assert ver.bugfix == 0
        assert ver.string == '{0}.{1}.0'.format(maj_ver, min_ver)
