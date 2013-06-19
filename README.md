pyAPT
=====

Python interface to Thorlab's APT motion controllers. Depends on `libftdi1` and `pylibftdi`.

Development is ongoing, and I will be adding functionality as I need them in
the course of my DPhil.

Note on stage limits
====================

The stage limits (maximum acceleration, velocity, etc) as quoted on the
Thorlabs website, or in their user manuals, often don't agree with reality. The
best way to get these limits is to install the APT User software, which seems
to have built-in limits for the various stages. These correspond much better to
the actual performance of stages.
