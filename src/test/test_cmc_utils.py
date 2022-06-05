"""Testing suite for cmc_Utils.py"""

import configparser
import os
import unittest
import src.cmc_api.cmc_utils as cmc_utils


class CmcUtilsTest(unittest.TestCase):
    """Testing Class for cmc_utils file"""

    def test_create_config_file(self):
        """Testing function create_config_file()"""
        cmc_utils.create_config_file()
        my_config = 'config.ini'
        self.assertTrue(expr=os.path.isfile(my_config))

    def test_get_configuration_file(self):
        """Testing the ger_configuration_file()"""
        config, configuration = cmc_utils.get_configuration_file()
        self.assertIsInstance(obj=config, cls=configparser.ConfigParser)
        self.assertIsInstance(obj=configuration, cls=configparser.SectionProxy)

    def test_read_configuration_file_without_config_key(self):
        """Testing the function read_configuration_file """
        config, configuration = cmc_utils.read_configuration_file()
        self.assertIsInstance(obj=config, cls=configparser.ConfigParser)
        self.assertIsInstance(obj=configuration, cls=configparser.SectionProxy)

    def test_read_configuration_file_wit_config_key(self):
        """Testing the function read_configuration_file """
        _, configuration = cmc_utils.read_configuration_file(config_key="current_day_used")
        self.assertNotIsInstance(obj=configuration, cls=configparser.SectionProxy)

    def tearDown(self) -> None:
        os.remove('config.ini')

if __name__ == '__main__':
    unittest.main()
