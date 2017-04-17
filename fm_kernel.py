import snapcraft
from snapcraft.plugins import kernel

import logging

logger = logging.getLogger(__name__)


class KernelPlugin(kernel.KernelPlugin):
    def _set_kernel_targets(self):
        super()._set_kernel_targets()

        self.make_install_targets.extend([
            'INSTALL_MOD_STRIP=1'
        ])
