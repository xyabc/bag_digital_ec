# -*- coding: utf-8 -*-
########################################################################################################################
#
# Copyright (c) 2014, Regents of the University of California
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
# following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following
#   disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the
#    following disclaimer in the documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
########################################################################################################################

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
# noinspection PyUnresolvedReferences,PyCompatibility
from builtins import *

import os
import pkg_resources

from bag.design import Module


yaml_file = pkg_resources.resource_filename(__name__, os.path.join('netlist_info', 'inv.yaml'))


# noinspection PyPep8Naming
class digital_ec_templates__inv(Module):
    """Module for library digital_ec_templates cell inv.

    Fill in high level description here.
    """

    param_list = ['lch', 'wp', 'wn', 'fgp', 'fgn', 'nduml', 'ndumr', 'intent', ]

    def __init__(self, bag_config, parent=None, prj=None, **kwargs):
        Module.__init__(self, bag_config, yaml_file, parent=parent, prj=prj, **kwargs)
        for par in self.param_list:
            self.parameters[par] = None

    def design(self):
        """To be overridden by subclasses to design this module.

        This method should fill in values for all parameters in
        self.parameters.  To design instances of this module, you can
        call their design() method or any other ways you coded.

        To modify schematic structure, call:

        rename_pin()
        delete_instance()
        replace_instance_master()
        reconnect_instance_terminal()
        restore_instance()
        array_instance()
        """
        pass

    def design_specs(self, lch, wp, wn, fgp, fgn, nduml, ndumr, intent, **kwargs):
        """Set the design parameters of this passgate directly.

        Parameters
        ----------
        lch : float
            channel length, in meters.
        wp : float or int
            pmos width, in meters or number of fins.
        wn : float or int
            nmos width, in meters or number of fins.
        fgp : int
            number of pmos fingers.
        fgn : int
            number of nmos fingers.
        nduml : int
            number of left dummies.
        ndumr : int
            number of right dummies.
        intent : str
            the device intent of the transistors.
        """
        local_dict = locals()
        for par in self.param_list:
            if par not in local_dict:
                raise Exception('Parameter %s not defined' % par)
            self.parameters[par] = local_dict[par]

        # error checking
        if fgp % 2 == 1 or fgn % 2 == 1:
            raise ValueError('Only even number of pmos/nmos fingers are supported.')

        # find total number of fingers, number of left/right dummies, and fix dummy nets
        delta = abs(fgp - fgn)
        if fgp > fgn:
            fg_tot = fgp + nduml + ndumr
            p_nduml, p_ndumr = nduml, ndumr
            n_nduml, n_ndumr = nduml + delta // 2, ndumr + delta // 2
        else:
            fg_tot = fgn + nduml + ndumr
            n_nduml, n_ndumr = nduml, ndumr
            p_nduml, p_ndumr = nduml + delta // 2, ndumr + delta // 2

        self.instances['XP'].design(w=wp, l=lch, nf=fgp, intent=intent)
        self.instances['XDP'].design(w=wp, l=lch, nf=p_nduml + p_ndumr, intent=intent)
        self.instances['XN'].design(w=wn, l=lch, nf=fgn, intent=intent)
        self.instances['XDN'].design(w=wn, l=lch, nf=n_nduml + n_ndumr, intent=intent)

    def get_layout_params(self, **kwargs):
        """Returns a dictionary with layout parameters.

        This method computes the layout parameters used to generate implementation's
        layout.  Subclasses should override this method if you need to run post-extraction
        layout.

        Parameters
        ----------
        kwargs :
            any extra parameters you need to generate the layout parameters dictionary.
            Usually you specify layout-specific parameters here, like metal layers of
            input/output, customizable wire sizes, and so on.

        Returns
        -------
        params : dict[str, any]
            the layout parameters dictionary.
        """
        layout_params = dict(
            lch=self.parameters['lch'],
            wp=self.parameters['wp'],
            wn=self.parameters['wn'],
            fgp=self.parameters['fgp'],
            fgn=self.parameters['fgn'],
            nduml=self.parameters['nduml'],
            ndumr=self.parameters['ndumr'],
            threshold=self.parameters['intent'],
            rename_dict=self.get_layout_pin_mapping(),
        )

        layout_params.update(kwargs)
        return layout_params

    def get_layout_pin_mapping(self):
        """Returns the layout pin mapping dictionary.

        This method returns a dictionary used to rename the layout pins, in case they are different
        than the schematic pins.

        Returns
        -------
        pin_mapping : dict[str, str]
            a dictionary from layout pin names to schematic pin names.
        """
        return {}
