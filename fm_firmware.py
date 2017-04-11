import os
import shutil

from snapcraft import BasePlugin


class FirmwarePlugin(BasePlugin):
    @classmethod
    def schema(cls):
        schema = super().schema()

        schema['properties']['fm-firmware'] = {
            'type': 'array'
        }

        return schema

    @classmethod
    def get_build_properties(cls):
        return super().get_build_properties() + [
            'fm-firmware'
        ]

    def enable_cross_compilation(self):
        pass

    def build(self):
        # Ensure "firmware" directory exists
        os.makedirs(os.path.join(self.installdir, 'firmware'))

        # Copy firmware into installation directory
        self._run(self.builddir)

    def _run(self, search_path, _base_path=None):
        if _base_path is None:
            _base_path = search_path

        for name in os.listdir(search_path):
            if name == 'WHENCE':
                continue

            if name.startswith('LICENSE.'):
                continue

            # Build paths
            path = os.path.join(search_path, name)
            rel_path = os.path.relpath(path, _base_path)

            # Check path should be included
            match, scan = self._matches(rel_path)

            if not match:
                continue

            # Process item
            if scan:
                if not os.path.isdir(path):
                    continue

                # Scan directory (if not an exact match)
                self._run(path, _base_path)
            else:
                # Copy file (or directory) to the install directory
                self._copy(path, os.path.join(self.installdir, 'firmware', rel_path))

    def _copy(self, source_path, destination_path):
        # Ensure `source_path` exists
        if not os.path.exists(source_path):
            return False

        # Copy file
        if os.path.isfile(source_path):
            shutil.copy(source_path, destination_path)
            return True

        # Ensure destination directory exists
        os.makedirs(destination_path)

        # Copy items into destination directory
        for name in os.listdir(source_path):
            self._copy(
                os.path.join(source_path, name),
                os.path.join(destination_path, name)
            )

        return True

    def _matches(self, path):
        for item in self.options.fm_firmware:
            if item.startswith(path):
                return True, item != path

        return False, False
