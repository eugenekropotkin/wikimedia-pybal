# -*- coding: utf-8 -*-
"""
  PyBal unit tests
  ~~~~~~~~~~~~~~~~

  This module contains tests for `pybal.monitor`.

"""
import unittest

import pybal.monitor
import pybal.util
import twisted.internet

from .fixtures import PyBalTestCase


class MonitoringProtocolTestCase(PyBalTestCase):
    """Test case for `pybal.monitor.MonitoringProtocol`."""

    def setUp(self):
        super(MonitoringProtocolTestCase, self).setUp()
        self.monitor = pybal.monitor.MonitoringProtocol(
            self.coordinator, None, self.config)
        self.monitor.__name__ = 'TestMonitor'
        self.reactor = twisted.internet.reactor

    def testRun(self):
        """Test `MonitoringProtocol.run`."""
        self.monitor.run()
        self.assertTrue(self.monitor.active)
        with self.assertRaises(AssertionError):
            self.monitor.run()

    def testStop(self):
        """Test `MonitoringProtocol.stop`."""
        self.monitor.run()
        self.monitor.stop()
        self.assertFalse(self.monitor.active)

    def testStopBeforeShutdown(self):
        """`MonitoringProtocol` stops on system shutdown."""
        self.monitor.run()
        self.reactor.fireSystemEvent('shutdown')
        self.assertFalse(self.monitor.active)

    def testName(self):
        """Test `MonitoringProtocol._resultUp`."""
        self.assertEquals(self.monitor.name(), 'TestMonitor')

    def testResultUp(self):
        """Test `MonitoringProtocol._resultUp`."""
        self.monitor._resultUp()
        self.assertTrue(self.coordinator.up)

    def testResultUpInactive(self):
        """`MonitoringProtocol._resultUp` should not change state when monitor
        is inactive, unless this is the first check."""
        self.monitor.firstCheck = False
        self.monitor._resultUp()
        self.assertIsNone(self.coordinator.up)

    def testResultDown(self):
        """Test `MonitoringProtocol._resultDown`."""
        self.monitor._resultDown()
        self.assertFalse(self.monitor.up)

    def testResultDownInactive(self):
        """`MonitoringProtocol._resultDown` should not change state when
        monitor is inactive, unless this is the first check."""
        self.monitor.firstCheck = False
        self.monitor._resultDown()
        self.assertIsNone(self.coordinator.up)

    def testGetConfigString(self):
        """Test `MonitoringProtocol._getConfigString`."""
        self.config['testmonitor.strValue'] = 'abc'
        self.assertEquals(self.monitor._getConfigString('strValue'), 'abc')

        self.config['testmonitor.badStrValue'] = 123
        with self.assertRaises(ValueError):
            self.monitor._getConfigString('badStrValue')

    def testGetConfigInt(self):
        """Test `MonitoringProtocol._getConfigInt`."""
        self.config['testmonitor.intValue'] = 123
        self.assertEquals(self.monitor._getConfigInt('intValue'), 123)

    def testGetConfigBool(self):
        """Test `MonitoringProtocol._getConfigBool`."""
        self.config['testmonitor.boolValue'] = 'false'
        self.assertFalse(self.monitor._getConfigBool('boolValue'))

    def testGetConfigStringList(self):
        """Test `MonitoringProtocol._getConfigStringList`."""
        self.config['testmonitor.strListValue'] = '"abc"'
        self.assertEquals(
            self.monitor._getConfigStringList('strListValue'), 'abc')

        self.config['testmonitor.strListValue'] = '["abc", "def"]'
        self.assertEquals(
            self.monitor._getConfigStringList('strListValue'), ['abc', 'def'])

        self.config['testmonitor.badStrListValue'] = '["abc", 123]'
        with self.assertRaises(ValueError):
            self.monitor._getConfigStringList('badStrListValue')

        self.config['testmonitor.emptyStrListValue'] = '[]'
        with self.assertRaises(ValueError):
            self.monitor._getConfigStringList('emptyStrListValue')
