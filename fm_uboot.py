import logging
import os
import shutil

import snapcraft
from snapcraft.plugins import kbuild

logger = logging.getLogger(__name__)


class UBootPlugin(kbuild.KBuildPlugin):
    @classmethod
    def schema(cls):
        schema = super().schema()

        schema['properties']['fm-uboot-board'] = {
            'type': 'string'
        }

        schema['properties']['fm-uboot-configfile'] = {
            'type': 'string'
        }

        schema['properties']['fm-uboot-image'] = {
            'type': 'string'
        }

        schema['required'] = schema['required'] + [
            'fm-uboot-image'
        ]

        return schema

    @classmethod
    def get_build_properties(cls):
        return super().get_build_properties() + [
            'fm-uboot-board',
            'fm-uboot-configfile'
        ]

    def enable_cross_compilation(self):
        logger.info('Cross compiling kernel target {!r}'.format(self.project.kernel_arch))

        self.make_cmd.append('ARCH={}'.format(
            self.project.kernel_arch
        ))

        self.make_cmd.append('CROSS_COMPILE={}'.format(
            self.project.cross_compiler_prefix
        ))

    def build(self):
        # Validate options
        if self.options.kconfigfile is not None:
            raise ValueError('"kconfigfile" option is not supported')

        if not self.options.fm_uboot_board:
            raise ValueError('Invalid value provided for the "fm-uboot-board" option')

        if not self.options.fm_uboot_image:
            raise ValueError('Invalid value provided for the "fm-uboot-image" option')

        # Run build
        super().build()

    def do_base_config(self, config_path):
        kdefconfig = '{}_defconfig'.format(self.options.fm_uboot_board)

        # Copy configuration file into `configs/` (if provided)
        if self.options.fm_uboot_configfile:
            if not os.path.exists(self.options.fm_uboot_configfile):
                raise ValueError('Unable to find configuration file: {}'.format(self.options.fm_uboot_configfile))

            logger.debug('Copying "%s" to "configs/%s"...', self.options.fm_uboot_configfile, kdefconfig)

            try:
                shutil.copy(self.options.fm_uboot_configfile, os.path.join(self.builddir, 'configs', kdefconfig))
            except Exception as ex:
                raise Exception('Unable to copy configuration file into configs/ directory: {}'.format(ex))

        # Generate configuration
        make_cmd = self.make_cmd.copy()
        make_cmd[1] = '-j1'

        self.run(make_cmd + [kdefconfig])

    def do_install(self):
        image_source_path = os.path.join(self.builddir, self.options.fm_uboot_image)

        # Ensure u-boot image exists
        if not os.path.exists(image_source_path):
            raise ValueError('U-Boot image does not exist: {}'.format(self.options.fm_uboot_image))

        # Remove existing u-boot image
        image_destination_path = os.path.join(self.installdir, self.options.fm_uboot_image)

        if os.path.exists(image_destination_path):
            os.remove(image_destination_path)

        # Link u-boot image into the install directory
        os.link(image_source_path, image_destination_path)
