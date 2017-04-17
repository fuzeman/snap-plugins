import snapcraft
from snapcraft.plugins import kernel

import logging

logger = logging.getLogger(__name__)


class KernelPlugin(kernel.KernelPlugin):
    @classmethod
    def schema(cls):
        schema = super().schema()

        schema['properties']['fm-kernel-flavour'] = {
            'type': 'string'
        }

        schema['properties']['fm-kernel-version'] = {
            'type': 'string'
        }

        schema['required'].extend([
            'fm-kernel-flavour',
            'fm-kernel-version'
        ])

        return schema

    @classmethod
    def get_build_properties(cls):
        return super().get_build_properties() + [
            'fm-kernel-flavour',
            'fm-kernel-version'
        ]

    def _set_kernel_targets(self):
        super()._set_kernel_targets()

        self.make_cmd.extend([
            'KERNELVERSION={}-{}'.format(self.options.fm_kernel_version, self.options.fm_kernel_flavour)
        ])

        self.make_install_targets.extend([
            'INSTALL_MOD_STRIP=1'
        ])
