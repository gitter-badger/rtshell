#!/usr/bin/env python
# -*- Python -*-
# -*- coding: utf-8 -*-

'''rtshell

Copyright (C) 2009-2010
    Geoffrey Biggs
    RT-Synthesis Research Group
    Intelligent Systems Research Institute,
    National Institute of Advanced Industrial Science and Technology (AIST),
    Japan
    All rights reserved.
Licensed under the Eclipse Public License -v 1.0 (EPL)
http://www.opensource.org/licenses/eclipse-1.0.txt

Tests for the commands.

'''


import os
import os.path
import rtsprofile.rts_profile
import subprocess
import sys
import tempfile
import time
import unittest


COMP_LIB_PATH='/usr/local/share/OpenRTM-aist/examples/rtcs'


class RTCLaunchFailedError(Exception):
    pass


def call_process(args):
    p = subprocess.Popen(args, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    output = p.communicate()
    output = (output[0].strip(), output[1].strip())
    return_code = p.returncode
    return output[0], output[1], return_code


def start_process(args):
    p = subprocess.Popen(args, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    return p


def find_omninames():
    # If on Windows, ...
    # Else use ps
    procs, stderr, ret_code = call_process(['ps', '-e'])
    for p in procs.split('\n'):
        if 'omniNames' in p:
            return p.split()[0]
    return None


def launch_comp(name):
    p = start_process([os.path.join('./test', name), '-f', './test/rtc.conf'])
    p.poll()
    if p.returncode is not None:
        raise RTCLaunchFailedError
    return p


def stop_comp(p):
    p.terminate()
    p.wait()


def start_ns():
    # Check if omniNames is running
    pid = find_omninames()
    if pid:
        # Return none to indicate the name server is not under our control
        return None
    else:
        # Start omniNames and return the PID
        return start_process('rtm-naming')


def stop_ns(p):
    if p:
        call_process(['killall', 'omniNames'])


def wait_for_comp(comp, state='Inactive', tries=40, res=0.05):
    while tries > 0:
        stdout, stderr, ret = call_process(['./rtls', '-l',
            os.path.join('/localhost/local.host_cxt', comp)])
        if stdout != '':
            if stdout.split()[0] == state:
                return
        tries -= 1
        time.sleep(res)
    raise RTCLaunchFailedError


def make_zombie(comp='zombie_comp'):
    c = launch_comp(comp)
    wait_for_comp('Zombie0.rtc')
    c.kill()
    c.wait()


def clean_zombies():
    call_process(['./rtdel', '-z'])


def launch_manager(tries=40, res=0.05):
    p = start_process(['rtcd', '-d', '-f', './test/rtc.conf'])
    while tries > 0:
        stdout, stderr, ret = call_process(['./rtls',
            '/localhost/local.host_cxt/manager.mgr'])
        if stdout == '' and stderr == '':
            return p
        tries -= 1
        time.sleep(res)
    raise RTCLaunchFailedError


def stop_manager(mgr):
    mgr.terminate()
    mgr.wait()


def add_obj_strs(args, obj1=None, obj2=None):
    if obj1 is not None:
        args.append('/localhost/local.host_cxt/{0}'.format(obj1))
    if obj2 is not None:
        args.append('/localhost/local.host_cxt/{0}'.format(obj2))
    return args


def test_notacomp(tester, cmd, obj1=None, obj2=None, extra_opts=[]):
    stdout, stderr, ret = call_process(add_obj_strs(['./{0}'.format(cmd)],
        obj1=obj1, obj2=obj2) + extra_opts)
    tester.assertEqual(stdout, '')
    tester.assertEqual(stderr,
        '{0}: Not a component: /localhost/local.host_cxt/{1}'.format(
            os.path.basename(cmd), obj1))
    tester.assertEqual(ret, 1)


def test_notacomp2(tester, cmd, obj1=None, obj2=None, extra_opts=[]):
    stdout, stderr, ret = call_process(add_obj_strs(['./{0}'.format(cmd)],
        obj1=obj1, obj2=obj2) + extra_opts)
    tester.assertEqual(stdout, '')
    tester.assertEqual(stderr,
        '{0}: Not a component: /localhost/local.host_cxt/{1}'.format(
            os.path.basename(cmd), obj2))
    tester.assertEqual(ret, 1)


def test_noobject(tester, cmd, obj1=None, obj2=None, extra_opts=[]):
    stdout, stderr, ret = call_process(add_obj_strs(['./{0}'.format(cmd)],
        obj1=obj1, obj2=obj2) + extra_opts)
    tester.assertEqual(stdout, '')
    tester.assertEqual(stderr,
        '{0}: No such object: /localhost/local.host_cxt/{1}'.format(
            os.path.basename(cmd), obj1))
    tester.assertEqual(ret, 1)


def test_noobject2(tester, cmd, obj1=None, obj2=None, extra_opts=[]):
    stdout, stderr, ret = call_process(add_obj_strs(['./{0}'.format(cmd)],
        obj1=obj1, obj2=obj2) + extra_opts)
    tester.assertEqual(stdout, '')
    tester.assertEqual(stderr,
        '{0}: No such object: /localhost/local.host_cxt/{1}'.format(
            os.path.basename(cmd), obj2))
    tester.assertEqual(ret, 1)


def test_zombie(tester, cmd, obj1=None, obj2=None, extra_opts=[]):
    stdout, stderr, ret = call_process(add_obj_strs(['./{0}'.format(cmd)],
        obj1=obj1, obj2=obj2) + extra_opts)
    tester.assertEqual(stdout, '')
    tester.assertEqual(stderr,
        '{0}: Zombie object: /localhost/local.host_cxt/{1}'.format(
            os.path.basename(cmd), obj1))
    tester.assertEqual(ret, 1)


def test_portnotfound(tester, cmd, obj1=None, obj2=None, extra_opts=[]):
    stdout, stderr, ret = call_process(add_obj_strs(['./{0}'.format(cmd)],
        obj1=obj1, obj2=obj2) + extra_opts)
    tester.assertEqual(stdout, '')
    tester.assertEqual(stderr,
        '{0}: Port not found: /localhost/local.host_cxt/{1}'.format(
            os.path.basename(cmd), obj1))
    tester.assertEqual(ret, 1)


def test_port2notfound(tester, cmd, obj1=None, obj2=None, extra_opts=[]):
    stdout, stderr, ret = call_process(add_obj_strs(['./{0}'.format(cmd)],
        obj1=obj1, obj2=obj2) + extra_opts)
    tester.assertEqual(stdout, '')
    tester.assertEqual(stderr,
        '{0}: Port not found: /localhost/local.host_cxt/{1}'.format(
            os.path.basename(cmd), obj2))
    tester.assertEqual(ret, 1)


def test_sourceportnotfound(tester, cmd, obj1=None, obj2=None, extra_opts=[]):
    stdout, stderr, ret = call_process(add_obj_strs(['./{0}'.format(cmd)],
        obj1=obj1, obj2=obj2) + extra_opts)
    tester.assertEqual(stdout, '')
    tester.assertEqual(stderr,
        '{0}: No source port specified.'.format(os.path.basename(cmd)))
    tester.assertEqual(ret, 1)


def test_destportnotfound(tester, cmd, obj1=None, obj2=None, extra_opts=[]):
    stdout, stderr, ret = call_process(add_obj_strs(['./{0}'.format(cmd)],
        obj1=obj1, obj2=obj2) + extra_opts)
    tester.assertEqual(stdout, '')
    tester.assertEqual(stderr,
        '{0}: No destination port specified.'.format(os.path.basename(cmd)))
    tester.assertEqual(ret, 1)


class rtactTests(unittest.TestCase):
    def setUp(self):
        self._ns = start_ns()
        self._std = launch_comp('std_comp')
        make_zombie()
        self._mgr = launch_manager()
        wait_for_comp('Std0.rtc')

    def tearDown(self):
        stop_comp(self._std)
        clean_zombies()
        stop_manager(self._mgr)
        stop_ns(self._ns)

    def test_success(self):
        stdout, stderr, ret = call_process(['./rtact',
            '/localhost/local.host_cxt/Std0.rtc'])
        self.assertEqual(stdout, '')
        self.assertEqual(stderr, '')
        self.assertEqual(ret, 0)
        stdout, stderr, ret = call_process(['./rtcat',
            '/localhost/local.host_cxt/Std0.rtc'])
        self.assertEqual(stdout.split()[1], 'Active')

    def test_context(self):
        test_notacomp(self, './rtact')

    def test_manager(self):
        test_notacomp(self, './rtact', obj1='manager.mgr')

    def test_port(self):
        test_notacomp(self, './rtact', obj1='Std0.rtc:in')

    def test_trailing_slash(self):
        test_notacomp(self, './rtact', obj1='Std0.rtc/')
        stdout, stderr, ret = call_process(['./rtcat',
            '/localhost/local.host_cxt/Std0.rtc'])
        self.assertEqual(stdout.split()[1], 'Inactive')

    def test_no_object(self):
        test_noobject(self, './rtact', obj1='NotAComp0.rtc')

    def test_zombie_object(self):
        test_zombie(self, './rtact', obj1='Zombie0.rtc')


def rtact_suite():
    return unittest.TestLoader().loadTestsFromTestCase(rtactTests)


class rtdeactTests(unittest.TestCase):
    def setUp(self):
        self._ns = start_ns()
        self._std = launch_comp('std_comp')
        make_zombie()
        self._mgr = launch_manager()
        call_process(['./rtact', '/localhost/local.host_cxt/Std0.rtc'])
        wait_for_comp('Std0.rtc', state='Active')

    def tearDown(self):
        stop_comp(self._std)
        clean_zombies()
        stop_manager(self._mgr)
        stop_ns(self._ns)

    def test_success(self):
        stdout, stderr, ret = call_process(['./rtdeact',
            '/localhost/local.host_cxt/Std0.rtc'])
        self.assertEqual(stdout, '')
        self.assertEqual(stderr, '')
        self.assertEqual(ret, 0)
        stdout, stderr, ret = call_process(['./rtcat',
            '/localhost/local.host_cxt/Std0.rtc'])
        self.assertEqual(stdout.split()[1], 'Inactive')

    def test_context(self):
        test_notacomp(self, './rtdeact')

    def test_manager(self):
        test_notacomp(self, './rtdeact', obj1='manager.mgr')

    def test_port(self):
        test_notacomp(self, './rtdeact', obj1='Std0.rtc:in')

    def test_trailing_slash(self):
        test_notacomp(self, './rtdeact', obj1='Std0.rtc/')
        stdout, stderr, ret = call_process(['./rtcat',
            '/localhost/local.host_cxt/Std0.rtc'])
        self.assertEqual(stdout.split()[1], 'Active')

    def test_no_object(self):
        test_noobject(self, './rtdeact', obj1='NotAComp0.rtc')

    def test_zombie_object(self):
        test_zombie(self, './rtdeact', obj1='Zombie0.rtc')


def rtdeact_suite():
    return unittest.TestLoader().loadTestsFromTestCase(rtdeactTests)


class rtresetTests(unittest.TestCase):
    def setUp(self):
        self._ns = start_ns()
        self._err = launch_comp('err_comp')
        make_zombie()
        self._mgr = launch_manager()
        call_process(['./rtact', '/localhost/local.host_cxt/Err0.rtc'])
        wait_for_comp('Err0.rtc', state='Error')

    def tearDown(self):
        stop_comp(self._err)
        clean_zombies()
        stop_manager(self._mgr)
        stop_ns(self._ns)

    def test_success(self):
        stdout, stderr, ret = call_process(['./rtreset',
            '/localhost/local.host_cxt/Err0.rtc'])
        self.assertEqual(stdout, '')
        self.assertEqual(stderr, '')
        self.assertEqual(ret, 0)
        stdout, stderr, ret = call_process(['./rtcat',
            '/localhost/local.host_cxt/Err0.rtc'])
        self.assertEqual(stdout.split()[1], 'Inactive')

    def test_context(self):
        test_notacomp(self, './rtreset')

    def test_manager(self):
        test_notacomp(self, './rtreset', obj1='manager.mgr')

    def test_port(self):
        test_notacomp(self, './rtreset', obj1='Err0.rtc:in')

    def test_trailing_slash(self):
        test_notacomp(self, './rtreset', obj1='Err0.rtc/')
        stdout, stderr, ret = call_process(['./rtcat',
            '/localhost/local.host_cxt/Err0.rtc'])
        self.assertEqual(stdout.split()[1], 'Error')

    def test_no_object(self):
        test_noobject(self, './rtreset', obj1='NotAComp0.rtc')

    def test_zombie_object(self):
        test_zombie(self, './rtreset', obj1='Zombie0.rtc')


def rtreset_suite():
    return unittest.TestLoader().loadTestsFromTestCase(rtresetTests)


class rtcatTests(unittest.TestCase):
    def setUp(self):
        self._ns = start_ns()
        self._std = launch_comp('std_comp')
        make_zombie()
        self._mgr = launch_manager()
        wait_for_comp('Std0.rtc')

    def tearDown(self):
        stop_comp(self._std)
        clean_zombies()
        stop_manager(self._mgr)
        stop_ns(self._ns)

    def test_context(self):
        test_noobject(self, './rtcat')

    def test_no_object(self):
        test_noobject(self, './rtcat', obj1='NotAComp0.rtc')

    def test_no_object_port(self):
        test_noobject(self, './rtcat', obj1='NotAComp0.rtc:notaport')

    def test_rtc(self):
        stdout, stderr, ret = call_process(['./rtcat',
            '/localhost/local.host_cxt/Std0.rtc'])
        self.assert_(stdout.startswith('Std0.rtc'))
        self.assert_('Inactive' in stdout)
        self.assert_('Category' in stdout)
        self.assert_('Execution Context' in stdout)
        self.assert_('DataInPort: in' in stdout)
        self.assertEqual(stderr, '')
        self.assertEqual(ret, 0)

    def test_manager(self):
        stdout, stderr, ret = call_process(['./rtcat',
            '/localhost/local.host_cxt/manager.mgr'])
        self.assert_(stdout.startswith('Name: manager'))
        self.assert_('Modules:' in stdout)
        self.assert_('Loaded modules:' in stdout)
        self.assertEqual(stderr, '')
        self.assertEqual(ret, 0)

    def test_port(self):
        stdout, stderr, ret = call_process(['./rtcat',
            '/localhost/local.host_cxt/Std0.rtc:in'])
        self.assertEqual(stdout, '+DataInPort: in')
        stdout, stderr, ret = call_process(['./rtcat', '-l',
            '/localhost/local.host_cxt/Std0.rtc:in'])
        self.assert_(stdout.startswith('-DataInPort: in'))
        self.assert_('dataport.data_type' in stdout)
        self.assert_('TimedLong' in stdout)
        self.assertEqual(stderr, '')
        self.assertEqual(ret, 0)

    def test_port_not_rtc(self):
        test_notacomp(self, './rtcat', obj1='manager.mgr:in')

    def test_port_trailing_slash(self):
        test_noobject(self, './rtcat', obj1='Std0.rtc:in/')

    def test_bad_port(self):
        test_portnotfound(self, './rtcat', obj1='Std0.rtc:out')

    def test_rtc_trailing_slash(self):
        test_noobject(self, './rtcat', obj1='Std0.rtc/')

    def test_zombie_object(self):
        test_zombie(self, './rtcat', obj1='Zombie0.rtc')


def rtcat_suite():
    return unittest.TestLoader().loadTestsFromTestCase(rtcatTests)


class rtcheckTests(unittest.TestCase):
    def setUp(self):
        self._ns = start_ns()
        self._std = launch_comp('std_comp')
        self._output = launch_comp('output_comp')
        wait_for_comp('Std0.rtc')
        wait_for_comp('Output0.rtc')

    def tearDown(self):
        stop_comp(self._std)
        stop_comp(self._output)
        stop_ns(self._ns)

    def test_noprobs(self):
        call_process(['./rtresurrect', './test/sys.rtsys'])
        call_process(['./rtstart', './test/sys.rtsys'])
        stdout, stderr, ret = call_process(['./rtcheck', './test/sys.rtsys'])
        self.assertEqual(stdout, '')
        self.assertEqual(stderr, '')
        self.assertEqual(ret, 0)

    def test_not_activated(self):
        call_process(['./rtresurrect', './test/sys.rtsys'])
        call_process(['./rtstart', './test/sys.rtsys'])
        call_process(['./rtdeact', '/localhost/local.host_cxt/Std0.rtc'])
        wait_for_comp('Std0.rtc', state='Inactive')
        stdout, stderr, ret = call_process(['./rtcheck', './test/sys.rtsys'])
        self.assertEqual(stdout, '')
        self.assertEqual(stderr,
                'Component /localhost/local.host_cxt/Std0.rtc '\
                'is in incorrect state Inactive')
        self.assertEqual(ret, 1)

    def test_not_connected(self):
        call_process(['./rtresurrect', './test/sys.rtsys'])
        call_process(['./rtstart', './test/sys.rtsys'])
        call_process(['./rtdis', '/localhost/local.host_cxt/Std0.rtc'])
        stdout, stderr, ret = call_process(['./rtcheck', './test/sys.rtsys'])
        self.assertEqual(stdout, '')
        self.assertEqual(stderr, 'No connection between '\
                '/localhost/local.host_cxt/Output0.rtc:out and '\
                '/localhost/local.host_cxt/Std0.rtc:in')
        self.assertEqual(ret, 1)


def rtcheck_suite():
    return unittest.TestLoader().loadTestsFromTestCase(rtcheckTests)


class rtcompTests(unittest.TestCase):
    def setUp(self):
        self._ns = start_ns()
        self._mgr = launch_manager()
        self._load_mgr()

    def tearDown(self):
        stop_manager(self._mgr)
        stop_ns(self._ns)


    def _load_mgr(self):
        stdout, stderr, ret = call_process(['./rtmgr',
            '/localhost/local.host_cxt/manager.mgr', '-l',
            os.path.join(COMP_LIB_PATH, 'Controller.so'), '-i',
            'ControllerInit', '-c', 'Controller'])
        self.assertEqual(ret, 0)
        stdout, stderr, ret = call_process(['./rtmgr',
            '/localhost/local.host_cxt/manager.mgr', '-l',
            os.path.join(COMP_LIB_PATH, 'Sensor.so'), '-i',
            'SensorInit', '-c', 'Sensor'])
        self.assertEqual(ret, 0)
        stdout, stderr, ret = call_process(['./rtmgr',
            '/localhost/local.host_cxt/manager.mgr', '-l',
            os.path.join(COMP_LIB_PATH, 'Motor.so'), '-i',
            'MotorInit', '-c', 'Motor'])
        self.assertEqual(ret, 0)

    def test_success(self):
        stdout, stderr, ret = call_process(['./rtcomp',
            '/localhost/local.host_cxt/manager.mgr', '-c',
            '/localhost/local.host_cxt/Controller0.rtc', '-p',
            '/localhost/local.host_cxt/Sensor0.rtc:in', '-p',
            '/localhost/local.host_cxt/Motor0.rtc:out'])
        self.assertEqual(stdout, '')
        self.assertEqual(stderr, '')
        self.assertEqual(ret, 0)
        self._assert_comp_exists('CompositeRTC.rtc')

    def test_set_name(self):
        stdout, stderr, ret = call_process(['./rtcomp',
            '/localhost/local.host_cxt/manager.mgr', '-c',
            '/localhost/local.host_cxt/Controller0.rtc', '-p',
            '/localhost/local.host_cxt/Sensor0.rtc:in', '-p',
            '/localhost/local.host_cxt/Motor0.rtc:out', '-n',
            'Blurgle'])
        self.assertEqual(stdout, '')
        self.assertEqual(stderr, '')
        self.assertEqual(ret, 0)
        self._assert_comp_exists('Blurgle.rtc')

    def _assert_comp_exists(self, name):
        wait_for_comp(name)
        stdout, stderr, ret = call_process(['./rtls',
            '/localhost/local.host_cxt/{0}'.format(name)])
        self.assertEqual(stdout, name)
        self.assertEqual(stderr, '')
        self.assertEqual(ret, 0)


def rtcomp_suite():
    return unittest.TestLoader().loadTestsFromTestCase(rtcompTests)


class rtconTests(unittest.TestCase):
    def setUp(self):
        self._ns = start_ns()
        self._std = launch_comp('std_comp')
        self._output = launch_comp('output_comp')
        self._err = launch_comp('err_comp')
        wait_for_comp('Std0.rtc')
        wait_for_comp('Output0.rtc')

    def tearDown(self):
        stop_comp(self._std)
        stop_comp(self._output)
        stop_comp(self._err)
        stop_ns(self._ns)

    def test_connect(self):
        stdout, stderr, ret = call_process(['./rtcon',
            '/localhost/local.host_cxt/Std0.rtc:in',
            '/localhost/local.host_cxt/Output0.rtc:out'])
        self.assertEqual(stdout, '')
        self.assertEqual(stderr, '')
        self.assertEqual(ret, 0)
        stdout, stderr, ret = call_process(['./rtcat', '-l',
            '/localhost/local.host_cxt/Std0.rtc:in'])
        self.assert_('/localhost/local.host_cxt/Output0.rtc:out' in stdout)
        stdout, stderr, ret = call_process(['./rtcat', '-l',
            '/localhost/local.host_cxt/Output0.rtc:out'])
        self.assert_('/localhost/local.host_cxt/Std0.rtc:in' in stdout)


    def test_set_props(self):
        stdout, stderr, ret = call_process(['./rtcon',
            '/localhost/local.host_cxt/Std0.rtc:in',
            '/localhost/local.host_cxt/Output0.rtc:out',
            '-p', 'dataport.subscription_type=new'])
        self.assertEqual(stdout, '')
        self.assertEqual(stderr, '')
        self.assertEqual(ret, 0)
        stdout, stderr, ret = call_process(['./rtcat', '-ll',
            '/localhost/local.host_cxt/Std0.rtc:in'])
        self.assert_('dataport.subscription_type      new' in stdout)
        stdout, stderr, ret = call_process(['./rtcat', '-ll',
            '/localhost/local.host_cxt/Output0.rtc:out'])
        self.assert_('dataport.subscription_type      new' in stdout)


    def test_bad_prop(self):
        stdout, stderr, ret = call_process(['./rtcon',
            '/localhost/local.host_cxt/Std0.rtc:in',
            '/localhost/local.host_cxt/Output0.rtc:out',
            '-p', 'dataport.subscription_type'])
        self.assertEqual(stdout, '')
        self.assert_(
            'Bad property format: dataport.subscription_type' in stderr)
        self.assertEqual(ret, 2)
        stdout, stderr, ret = call_process(['./rtcat', '-l',
            '/localhost/local.host_cxt/Std0.rtc:in'])
        self.assert_('Connected to: /localhost/local.host_cxt/Output0.rtc:out'\
                not in stdout)


    def test_set_name(self):
        stdout, stderr, ret = call_process(['./rtcon',
            '/localhost/local.host_cxt/Std0.rtc:in',
            '/localhost/local.host_cxt/Output0.rtc:out',
            '-n', 'test_conn'])
        self.assertEqual(stdout, '')
        self.assertEqual(stderr, '')
        self.assertEqual(ret, 0)
        stdout, stderr, ret = call_process(['./rtcat', '-ll',
            '/localhost/local.host_cxt/Std0.rtc:in'])
        self.assert_('test_conn' in stdout)
        stdout, stderr, ret = call_process(['./rtcat', '-ll',
            '/localhost/local.host_cxt/Output0.rtc:out'])
        self.assert_('test_conn' in stdout)


    def test_set_id(self):
        stdout, stderr, ret = call_process(['./rtcon',
            '/localhost/local.host_cxt/Std0.rtc:in',
            '/localhost/local.host_cxt/Output0.rtc:out',
            '-i', 'conn_id'])
        self.assertEqual(stdout, '')
        self.assertEqual(stderr, '')
        self.assertEqual(ret, 0)
        stdout, stderr, ret = call_process(['./rtcat', '-ll',
            '/localhost/local.host_cxt/Std0.rtc:in'])
        self.assert_('conn_id' in stdout)
        stdout, stderr, ret = call_process(['./rtcat', '-ll',
            '/localhost/local.host_cxt/Output0.rtc:out'])
        self.assert_('conn_id' in stdout)


    def test_no_source_port(self):
        test_sourceportnotfound(self, './rtcon', obj1='Std0.rtc',
                obj2='Output0.rtc:out')
        test_sourceportnotfound(self, './rtcon', obj1='Output0.rtc',
                obj2='Std0.rtc:in')


    def test_not_enough_targets(self):
        stdout, stderr, ret = call_process(['./rtcon', 'Std0.rtc:in'])
        self.assertEqual(stdout, '')
        self.assert_('Usage:' in stderr)
        self.assertEqual(ret, 1)


    def test_too_many_targets(self):
        stdout, stderr, ret = call_process(['./rtcon', 'Std0.rtc:in',
            'Output0.rtc:out', 'Err0.rtc:in'])
        self.assertEqual(stdout, '')
        self.assert_('Usage:' in stderr)
        self.assertEqual(ret, 1)


    def test_no_dest_port(self):
        test_destportnotfound(self, './rtcon', obj1='Std0.rtc:in',
                obj2='Output0.rtc')
        test_destportnotfound(self, './rtcon', obj1='Output0.rtc:out',
                obj2='Std0.rtc')


    def test_bad_source_port(self):
        test_portnotfound(self, './rtcon', obj1='Std0.rtc:noport',
                obj2='Output0.rtc:out')
        test_portnotfound(self, './rtcon', obj1='Output0.rtc:noport',
                obj2='Std0.rtc:in')


    def test_bad_source_rtc(self):
        test_noobject(self, './rtcon', obj1='NotAComp0.rtc:in',
                obj2='Output0.rtc:out')
        test_noobject(self, './rtcon',
                obj1='NotAComp0.rtc:out',
                obj2='Std0.rtc:in')


    def test_bad_dest_port(self):
        test_port2notfound(self, './rtcon', obj1='Std0.rtc:in',
                obj2='Output0.rtc:noport')
        test_port2notfound(self, './rtcon', obj1='Output0.rtc:out',
                obj2='Std0.rtc:noport')


    def test_bad_dest_rtc(self):
        test_noobject2(self, './rtcon', obj1='Std0.rtc:in',
                obj2='NotAComp0.rtc:out')
        test_noobject2(self, './rtcon', obj1='Output0.rtc:out',
                obj2='NotAComp0.rtc:in')

    def test_bad_polarity(self):
        stdout, stderr, ret = call_process(['./rtcon',
            '/localhost/local.host_cxt/Std0.rtc:in',
            '/localhost/local.host_cxt/Err0.rtc:in'])
        self.assertEqual(stdout, '')
        self.assertEqual(stderr, 'rtcon: Wrong port type.')
        self.assertEqual(ret, 1)

    def test_context(self):
        test_notacomp(self, './rtcon', obj1='', obj2='Output0.rtc:out')
        test_notacomp2(self, './rtcon', obj1='Std0.rtc:in', obj2='')

    def test_manager(self):
        test_notacomp(self, './rtcon', obj1='manager.mgr',
            obj2='Output0.rtc:out')
        test_notacomp2(self, './rtcon', obj1='Std0.rtc:in', obj2='manager.mgr')


def rtcon_suite():
    return unittest.TestLoader().loadTestsFromTestCase(rtconTests)


class rtconfTests(unittest.TestCase):
    def setUp(self):
        self._ns = start_ns()
        self._std = launch_comp('std_comp')
        make_zombie()
        wait_for_comp('Std0.rtc')

    def tearDown(self):
        stop_comp(self._std)
        clean_zombies()
        stop_ns(self._ns)

    def test_list(self):
        stdout, stderr, ret = call_process(['./rtconf',
            '/localhost/local.host_cxt/Std0.rtc', 'list'])
        self.assert_('+default*' in stdout)
        self.assert_('+set1' in stdout)
        self.assert_('+set2' in stdout)
        self.assertEqual(stderr, '')
        self.assertEqual(ret, 0)

    def test_list_long(self):
        stdout, stderr, ret = call_process(['./rtconf',
            '/localhost/local.host_cxt/Std0.rtc', 'list', '-l'])
        self.assertEqual(stdout,
                '-default*\n  param  0\n'\
                '-set1\n  param  1\n'\
                '-set2\n  param  2')
        self.assertEqual(stderr, '')
        self.assertEqual(ret, 0)

    def test_list_hidden_set_error(self):
        stdout, stderr, ret = call_process(['./rtconf', '-s', '__hidden__',
            '/localhost/local.host_cxt/Std0.rtc', 'list'])
        self.assertEqual(stdout, '')
        self.assertEqual(stderr, 'rtconf: No such configuration set: __hidden__')
        self.assertEqual(ret, 1)

    def test_list_hidden_set_ok(self):
        stdout, stderr, ret = call_process(['./rtconf', '-s', '__hidden__',
            '-a', '/localhost/local.host_cxt/Std0.rtc', 'list'])
        self.assertEqual(stdout, '+__hidden__')
        self.assertEqual(stderr, '')
        self.assertEqual(ret, 0)

    def test_list_bad_set(self):
        stdout, stderr, ret = call_process(['./rtconf', '-s', 'noset',
            '/localhost/local.host_cxt/Std0.rtc', 'list'])
        self.assertEqual(stdout, '')
        self.assertEqual(stderr, 'rtconf: No such configuration set: noset')
        self.assertEqual(ret, 1)

    def test_set_default(self):
        stdout, stderr, ret = call_process(['./rtconf',
            '/localhost/local.host_cxt/Std0.rtc', 'set', 'param', '42'])
        self.assertEqual(stdout, '')
        self.assertEqual(stderr, '')
        self.assertEqual(ret, 0)
        stdout, stderr, ret = call_process(['./rtconf',
            '/localhost/local.host_cxt/Std0.rtc', 'get', 'param'])
        self.assertEqual(stdout, '42')
        stdout, stderr, ret = call_process(['./rtconf', '-s', 'set1',
            '/localhost/local.host_cxt/Std0.rtc', 'get', 'param'])
        self.assertEqual(stdout, '1')
        stdout, stderr, ret = call_process(['./rtconf', '-s', 'set2',
            '/localhost/local.host_cxt/Std0.rtc', 'get', 'param'])
        self.assertEqual(stdout, '2')

    def test_set_other(self):
        stdout, stderr, ret = call_process(['./rtconf', '-s', 'set1',
            '/localhost/local.host_cxt/Std0.rtc', 'set', 'param', '42'])
        self.assertEqual(stdout, '')
        self.assertEqual(stderr, '')
        self.assertEqual(ret, 0)
        stdout, stderr, ret = call_process(['./rtconf', '-s', 'default',
            '/localhost/local.host_cxt/Std0.rtc', 'get', 'param'])
        self.assertEqual(stdout, '0')
        stdout, stderr, ret = call_process(['./rtconf', '-s', 'set1',
            '/localhost/local.host_cxt/Std0.rtc', 'get', 'param'])
        self.assertEqual(stdout, '42')
        stdout, stderr, ret = call_process(['./rtconf', '-s', 'set2',
            '/localhost/local.host_cxt/Std0.rtc', 'get', 'param'])
        self.assertEqual(stdout, '2')

    def test_set_hidden_error(self):
        stdout, stderr, ret = call_process(['./rtconf', '-s', '__hidden__',
            '/localhost/local.host_cxt/Std0.rtc', 'set', 'param', '42'])
        self.assertEqual(stdout, '')
        self.assertEqual(stderr, 'rtconf: No such configuration set: __hidden__')
        self.assertEqual(ret, 1)

    def test_set_hidden_ok(self):
        stdout, stderr, ret = call_process(['./rtconf', '-s', '__hidden__',
            '-a', '/localhost/local.host_cxt/Std0.rtc', 'set', 'param', '42'])
        self.assertEqual(stdout, '')
        self.assertEqual(stderr, '')
        self.assertEqual(ret, 0)
        stdout, stderr, ret = call_process(['./rtconf', '-s', '__hidden__',
            '-a', '/localhost/local.host_cxt/Std0.rtc', 'get', 'param'])
        self.assertEqual(stdout, '42')
        stdout, stderr, ret = call_process(['./rtconf', '-s', 'default',
            '/localhost/local.host_cxt/Std0.rtc', 'get', 'param'])
        self.assertEqual(stdout, '0')
        stdout, stderr, ret = call_process(['./rtconf', '-s', 'set1',
            '/localhost/local.host_cxt/Std0.rtc', 'get', 'param'])
        self.assertEqual(stdout, '1')
        stdout, stderr, ret = call_process(['./rtconf', '-s', 'set2',
            '/localhost/local.host_cxt/Std0.rtc', 'get', 'param'])
        self.assertEqual(stdout, '2')

    def test_get_default(self):
        stdout, stderr, ret = call_process(['./rtconf',
            '/localhost/local.host_cxt/Std0.rtc', 'get', 'param'])
        self.assertEqual(stdout, '0')
        self.assertEqual(stderr, '')
        self.assertEqual(ret, 0)

    def test_get_other(self):
        stdout, stderr, ret = call_process(['./rtconf', '-s', 'set2',
            '/localhost/local.host_cxt/Std0.rtc', 'get', 'param'])
        self.assertEqual(stdout, '2')
        self.assertEqual(stderr, '')
        self.assertEqual(ret, 0)

    def test_get_bad_set(self):
        stdout, stderr, ret = call_process(['./rtconf', '-s', 'noset',
            '/localhost/local.host_cxt/Std0.rtc', 'get', 'param'])
        self.assertEqual(stdout, '')
        self.assertEqual(stderr, 'rtconf: No such configuration set: noset')
        self.assertEqual(ret, 1)

    def test_get_bad_param(self):
        stdout, stderr, ret = call_process(['./rtconf',
            '/localhost/local.host_cxt/Std0.rtc', 'get', 'noparam'])
        self.assertEqual(stdout, '')
        self.assertEqual(stderr,
                'rtconf: No such configuration parameter: noparam')
        self.assertEqual(ret, 1)

    def test_get_hidden_error(self):
        stdout, stderr, ret = call_process(['./rtconf', '-s', '__hidden__',
            '/localhost/local.host_cxt/Std0.rtc', 'get', 'param'])
        self.assertEqual(stdout, '')
        self.assertEqual(stderr, 'rtconf: No such configuration set: __hidden__')
        self.assertEqual(ret, 1)

    def test_get_hidden_ok(self):
        stdout, stderr, ret = call_process(['./rtconf', '-s', '__hidden__',
            '-a', '/localhost/local.host_cxt/Std0.rtc', 'get', 'param'])
        self.assertEqual(stdout, '3')
        self.assertEqual(stderr, '')
        self.assertEqual(ret, 0)

    def test_act(self):
        stdout, stderr, ret = call_process(['./rtconf',
            '/localhost/local.host_cxt/Std0.rtc', 'act', 'set1'])
        self.assertEqual(stdout, '')
        self.assertEqual(stderr, '')
        self.assertEqual(ret, 0)
        stdout, stderr, ret = call_process(['./rtconf',
            '/localhost/local.host_cxt/Std0.rtc', 'list'])
        self.assertEqual(stdout, '+default\n+set1*\n+set2')

    def test_act_bad_set(self):
        stdout, stderr, ret = call_process(['./rtconf',
            '/localhost/local.host_cxt/Std0.rtc', 'act', 'noset'])
        self.assertEqual(stdout, '')
        self.assertEqual(stderr, 'rtconf: No such configuration set: noset')
        self.assertEqual(ret, 1)

    def test_act_hidden_error(self):
        stdout, stderr, ret = call_process(['./rtconf',
            '/localhost/local.host_cxt/Std0.rtc', 'act', '__hidden__'])
        self.assertEqual(stdout, '')
        self.assertEqual(stderr, 'rtconf: No such configuration set: __hidden__')
        self.assertEqual(ret, 1)

    def test_act_hidden_ok(self):
        stdout, stderr, ret = call_process(['./rtconf', '-a',
            '/localhost/local.host_cxt/Std0.rtc', 'act', '__hidden__'])
        self.assertEqual(stdout, '')
        self.assert_('SDOPackage.InternalError' in stderr)
        self.assertEqual(ret, 1)

    def test_context(self):
        test_noobject(self, './rtconf', obj1='')

    def test_manager(self):
        test_noobject(self, './rtconf', obj1='manager.rtc',
                extra_opts=['list'])

    def test_port(self):
        test_notacomp(self, './rtconf', obj1='Std0.rtc:in')

    def test_trailing_slash(self):
        test_noobject(self, './rtconf', obj1='Std0.rtc/')

    def test_bad_comp(self):
        test_noobject(self, './rtconf', obj1='NotAComp0.rtc')

    def test_zombie(self):
        test_zombie(self, './rtconf', obj1='Zombie0.rtc')


def rtconf_suite():
    return unittest.TestLoader().loadTestsFromTestCase(rtconfTests)


class rtcryoTests(unittest.TestCase):
    def setUp(self):
        self._ns = start_ns()
        self._std = launch_comp('std_comp')
        self._output = launch_comp('output_comp')
        wait_for_comp('Std0.rtc')
        wait_for_comp('Output0.rtc')
        stdout, stderr, ret = call_process(['./rtresurrect',
            './test/sys.rtsys'])
        self.assertEqual(stdout, '')
        self.assertEqual(stderr, '')
        self.assertEqual(ret, 0)

    def tearDown(self):
        stop_comp(self._std)
        stop_comp(self._output)
        stop_ns(self._ns)

    def test_freeze_to_stdout_xml(self):
        stdout, stderr, ret = call_process(['./rtcryo', '-x'])
        self.assertEqual(stderr, '')
        self.assertEqual(ret, 0)
        self._check_rtsys_xml(stdout)

    def test_freeze_to_file_xml(self):
        f, fn = tempfile.mkstemp(prefix='rtshell_test_')
        os.close(f)
        stdout, stderr, ret = call_process(['./rtcryo', '-x', '-o', fn])
        rtsys = self._load_rtsys(fn)
        os.remove(fn)
        self.assertEqual(stdout, '')
        self.assertEqual(stderr, '')
        self.assertEqual(ret, 0)
        self._check_rtsys_xml(rtsys)

    def test_freeze_to_stdout_yaml(self):
        stdout, stderr, ret = call_process(['./rtcryo', '-y'])
        self.assertEqual(stderr, '')
        self.assertEqual(ret, 0)
        self._check_rtsys_yaml(stdout)

    def test_freeze_to_file_yaml(self):
        f, fn = tempfile.mkstemp(prefix='rtshell_test_')
        os.close(f)
        stdout, stderr, ret = call_process(['./rtcryo', '-y', '-o', fn])
        rtsys = self._load_rtsys(fn)
        os.remove(fn)
        self.assertEqual(stdout, '')
        self.assertEqual(stderr, '')
        self.assertEqual(ret, 0)
        self._check_rtsys_yaml(rtsys)

    def test_freeze_abstract(self):
        stdout, stderr, ret = call_process(['./rtcryo', '-a',
            'This is an abstract'])
        self.assertEqual(stderr, '')
        self.assertEqual(ret, 0)
        orig = self._load_rtsys('./test/sys.rtsys')
        self.assertNotEqual(stdout, orig)
        self.assert_('rts:abstract="This is an abstract"' in stdout)

    def test_freeze_sysname(self):
        stdout, stderr, ret = call_process(['./rtcryo', '-n',
            'system name'])
        self.assertEqual(stderr, '')
        self.assertEqual(ret, 0)
        orig = self._load_rtsys('./test/sys.rtsys')
        self.assertNotEqual(stdout, orig)
        self.assert_('rts:id="RTSystem :Me.system name.0"' in stdout)

    def test_freeze_version(self):
        stdout, stderr, ret = call_process(['./rtcryo', '-v',
            '42'])
        self.assertEqual(stderr, '')
        self.assertEqual(ret, 0)
        orig = self._load_rtsys('./test/sys.rtsys')
        self.assertNotEqual(stdout, orig)
        self.assert_('rts:id="RTSystem :Me.RTSystem.42"' in stdout)

    def test_freeze_vendor(self):
        stdout, stderr, ret = call_process(['./rtcryo', '-e',
            'UnitTest'])
        self.assertEqual(stderr, '')
        self.assertEqual(ret, 0)
        orig = self._load_rtsys('./test/sys.rtsys')
        self.assertNotEqual(stdout, orig)
        self.assert_('rts:id="RTSystem :UnitTest.RTSystem.0"' in stdout)

    def _check_rtsys_xml(self, rtsys):
        self.assert_(rtsys.startswith('<?xml'))
        # Components
        self.assert_('rts:instanceName="Std0"' in rtsys)
        self.assert_('rts:instanceName="Output0"' in rtsys)
        # Configuration sets and parameters
        self.assert_('rts:ConfigurationSets rts:id="default"' in rtsys)
        self.assert_('rts:ConfigurationSets rts:id="__hidden__"' in rtsys)
        self.assert_('rts:ConfigurationSets rts:id="set1"' in rtsys)
        self.assert_('rts:ConfigurationSets rts:id="set2"' in rtsys)
        self.assert_('rts:name="param"' in rtsys)
        self.assert_('rts:data="0"' in rtsys)
        self.assert_('rts:data="1"' in rtsys)
        self.assert_('rts:data="2"' in rtsys)
        self.assert_('rts:data="3"' in rtsys)
        # Connections
        self.assert_('rts:DataPortConnectors' in rtsys)
        self.assert_('rts:name="in_out"' in rtsys)
        self.assert_('rts:sourceDataPort' in rtsys)
        self.assert_('rts:portName="Output0.out"' in rtsys)
        self.assert_('rts:targetDataPort' in rtsys)
        self.assert_('rts:portName="Std0.in"' in rtsys)
        # Can it be loaded?
        rtsprofile.rts_profile.RtsProfile(xml_spec=rtsys)

    def _check_rtsys_yaml(self, rtsys):
        self.assert_(rtsys.startswith('rtsProfile:'))
        # Components
        self.assert_('instanceName: Std0' in rtsys)
        self.assert_('instanceName: Output0' in rtsys)
        # Configuration sets and parameters
        self.assert_('id: default' in rtsys)
        self.assert_('id: __hidden__' in rtsys)
        self.assert_('id: set1' in rtsys)
        self.assert_('id: set2' in rtsys)
        self.assert_('name: param' in rtsys)
        self.assert_("data: '0'" in rtsys)
        self.assert_("data: '1'" in rtsys)
        self.assert_("data: '2'" in rtsys)
        self.assert_("data: '3'" in rtsys)
        # Connections
        self.assert_('dataPortConnectors' in rtsys)
        self.assert_('name: in_out' in rtsys)
        self.assert_('sourceDataPort' in rtsys)
        self.assert_('portName: Output0.out' in rtsys)
        self.assert_('targetDataPort' in rtsys)
        self.assert_('portName: Std0.in' in rtsys)
        # Can it be loaded?
        rtsprofile.rts_profile.RtsProfile(yaml_spec=rtsys)

    def _load_rtsys(self, fn):
        with open(fn, 'r') as f:
            return f.read()


def rtcryo_suite():
    return unittest.TestLoader().loadTestsFromTestCase(rtcryoTests)


def suite():
    return unittest.TestSuite([rtact_suite(), rtdeact_suite(),
        rtreset_suite(), rtcat_suite(), rtcheck_suite(), rtcomp_suite(),
        rtcon_suite(), rtconf_suite(), rtcryo_suite()])


if __name__ == '__main__':
    if len(sys.argv) >= 2:
        COMP_LIB_PATH = sys.argv[1]
        sys.argv = [sys.argv[0]] + sys.argv[2:]
    unittest.main()

