=======
[![Gitter](https://badges.gitter.im/Join Chat.svg)](https://gitter.im/yosuke/rtshell?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge)
rtshell
=======

Introduction
============

rtshell provides commands used to manage individual RT components and
managers, as well as complete RT Systems. It can be used with the
OpenRTM-aist middleware or middlewares that use a compatible CORBA-based
introspection system.

Many of the commands allow components and managers running on
nameservers to be treated like a file system. Directories can be
entered, components can be cat'd and activated/deactivated/reset,
connections made and removed, and so on.

Other commands are used in conjunction with RtsProfile XML/YAML files to
manage complete RT Systems. These are rtresurrect, rtteardown, rtcryo,
rtstart and rtstop.

The commands are aimed at users of OpenRTM-aist who wish to manage
components on low-resource systems, systems where a GUI is not available
(particularly where no network connection is available to manage
components from another computer), as well as those who face other
difficulties using RTSystemEditor.  Being familiar with using a
command-line is a benefit when using these commands of rtshell.

This software is developed at the National Institute of Advanced
Industrial Science and Technology. Approval number
H23PRO-1214. The development was financially supported by
the New Energy and Industrial Technology Development Organisation
Project for Strategic Development of Advanced Robotics Elemental
Technologies.  This software is licensed under the Eclipse Public
License -v 1.0 (EPL). See LICENSE.txt.


Requirements
============

rtshell requires rtctree 3.0. It must be installed for the commands to
function.

The commands that work with RtsProfile files require rtsprofile 2.0. It
must be installed for these commands to function/

rtshell uses the new string formatting operations that were introduced
in Python 2.6. It will not function with an earlier version of Python.
It has not been tested with Python 3 and it is likely that several
changes will be necessary to make it function using this version of
Python.

rtprint, rtinject and rtlog require the Python version of OpenRTM-aist.

For Ubuntu users, if you are using a version of Ubuntu prior to 9.04,
you will need to install a suitable Python version by hand. You may want
to consider upgrading to Ubuntu 9.04 or later (10.04 offers LTS).


Installation
============

There are several methods of installation available:

  1. Download the source from either the repository (see "Repository,"
  below) or a source archive, extract it somewhere, and run the commands
  from that directory.

  2. Download the source from either the repository (see "Repository,"
  below) or a source archive, extract it somewhere, and install it into
  your Python distribution:

    a) Extract the source, e.g. to a directory ~/rtshell::

      $ cd /home/blurgle/src/
      $ tar -xvzf rtshell-3.0.0.tar.gz

    b) Run setup.py to install rtshell to your default Python
    installation::

     $ python setup.py install

    c) If necessary, set environment variables. These should be set by
    default, but if not you will need to set them yourself. On Windows,
    you will need to ensure that your Python site-packages directory is
    in the PYTHONPATH variable and the Python scripts directory is in
    the PATH variable.  Typically, these will be something like
    ``C:\Python26\Lib\site-packages\`` and ``C:\Python26\Scripts\``,
    respectively (assuming Python 2.6 installed in ``C:\Python26\``).

  3. Use the Windows installer. This will perform the same job as running
  setup.py (see #2), but saves opening a command prompt. You may still need to
  add paths to your environment variables (see step c, above).

  4. In non-Windows operating systems, you must source the shell support
  file to gain full functionaliy. Amongst other things, rtcwd will not
  work without sourcing this file. You can find this file at
  ``${prefix}/share/rtshell/shell_support`` (``${prefix}`` is the
  directory where you installed rtshell). You can source it by running
  the following command (assuming rtshell has been installed to
  ``/usr/local``)::

   source /usr/local/share/rtshell/shell_support

  So that you don't have to run this command every time you open a
  terminal, you can add it to your shell's startup file. For example, if
  you are using a bash shell and installed rtshell to ``/usr/local``, add
  the following line to the ``.bashrc`` file in your home directory::

    source /usr/local/share/rtshell/shell_support


Repository
==========

The latest source is stored in a Git repository at github, available at
``http://github.com/gbiggs/rtshell``. You can download it as a zip file
or tarball by clicking the "Download Source" link in the top right of
the page.  Alternatively, use Git to clone the repository. This is
better if you wish to contribute patches::

  $ git clone git://github.com/gbiggs/rtshell.git


Documentation
=============

Documentation is available in the form of man pages (on Windows, these
are available as HTML files). These will be installed under
``${prefix}/share/man``.  You must add this folder to your system's
``$MANPATH`` environment variable to be able to use them. For example,
if you installed rtshell into /usr/local, add the following line to your
``.bashrc``::

  export MANPATH=/usr/local/share/man:${MANPATH}


Running the tests
=================

The command tests can be run from the source directory using a command
like the following::

~/src/rtshell $ ./test/test_cmds.py ~/share/OpenRTM-aist/examples/rtcs/

The argument to the test_cmds.py command is a directory containing RTC
shared libraries that can be loaded into a manager. It must contain the
libraries for Motor, Controller and Sensor.

An individual command's tests can be run by specifying those tests after
the command. For example::

$ ./test/test_cmds.py ~/share/OpenRTM-aist/examples/rtcs/ rtactTests

This will run only the tests for the rtact command.


Changelog
=========

4.0
---

- Adapt to OpenRTM's new data type specification method.
- Changed all os.sep occurrences to '/' for consistency with URLs.
- New command: rtvlog (Display RT Component log events).
- rtact/rtdeact/rtreset: Allow changing multiple components at once.
- rtcon: Support making connections involving three or more ports.
- rtdis: Support removing connections involving three or more ports.
- rtlog: Added end pointer to simpkl log format to speed up searches.
- rtmgr: Support corbaloc:: direct connection to managers.
- rtmgr: Allow multiple occurrences of any commands.
- rtmgr: Execute commands in the order specified.

3.0
---

- Merged rtcshell and rtsshell into a single toolkit.
- Added complete documentation for every command (man pages, HTML, PDF).
- New command: rtdoc (Print component documentation - thanks to Yosuke
  Matsusaka).
- New command: rtexit (Make a component exit).
- New command: rtlog (Log and replay data streams).
- New command: rtcheck (Check a system matches an RtsProfile file).
- New command: rtcomp (Create composite components).
- New command: rtstodot (Visualise RT Systems - thanks to Yosuke Matsusaka).
- New command: rtvis
- rtconf bash completion now completes set names, parameter names and values.
- Merged rtcwd and bash_completion bash files into a single file.
- Overhauled rtconf command line, added option to get a parameter value
  directly.
- Handle zombies properly.
- Display zombies in rtls.
- Delete zombies in rtdel (including all zombies found).
- Support path filters in rtctree to speed up tree creation.
- rtcat: Option to print a single port's information.
- rtcat: Changes --ll to -ll.
- rtcat: Display information about composite components.
- rtcryo: Print RtsProfile to standard output by default.
- rtdis: Disconnect-by-ID allows removing only one connection.
- rtinject/rtprint: Added support for user data types.
- rtprint: Option to exit after receiving one round of data.
- rtprint: Added support for user-defined formatters.
- rtprint: Added ability to print raw Python code.
- rtinject: Accept raw Python input from stdin.
- rtresurrect: Don't recreate existing connections.
- rtteardown: Fail if the connector ID doesn't match.
- rtresurrect/rtstart/rtstop/rtteardown: Accept input from standard input.
- Refactored former rtsshell commands into rtshell-style libraries.
- Added tests.


rtcshell-2.0
------------

- Fixes for Windows
- Fixed problems handling paths referencing parent directories
- New command: rtdel
- New command: rtinject
- New command: rtprint
- rtcat: Print the number of unknown connections
- Major refactoring: all commands can now be imported and called from Python
  scripts easily
- New Bash completion script (thanks to Keisuke Suzuki)
- Support csh in rtcwd
- rtcat: Print new information available from rtctree for execution contexts
- rtls: Change recurse option from -r to -R to match ls
- rtls: Handle unknown objects; display them like dead files

rtsshell-2.0
------------

- Added bash-completion script.
- Added planning capability.

