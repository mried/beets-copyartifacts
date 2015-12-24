import os
import sys

# Use unittest2 on Python < 2.7
try:
    import unittest2 as unittest
except ImportError:
    import unittest

# Make sure we use local version of beetsplug and not system namespaced version for tests
try:
    del sys.modules["beetsplug"]
except KeyError:
    pass

# Get the path to the beets source
beetspath = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'beets'))

# Check that the beets directory exists
if not os.path.isdir(beetspath):
    raise RuntimeError("A directory named beets with the beets source needs to be parallel to this plugin's source directory")

# Put the beets directory at the front of the search path
sys.path.insert(0, beetspath)

from testsupport import CopyArtifactsTestCase
from beets import plugins

import beetsplug

# Add copyartifacts path to pluginpath and load
beetsplug.__path__.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'beetsplug')))
plugins.load_plugins(['copyartifacts'])


class CopyArtifactsFromNestedDirectoryTest(CopyArtifactsTestCase):
    """
    Tests to check that copyartifacts copies or moves artifact files from a nested directory
    structure. i.e. songs in an album are imported from two directories corresponding to
    disc numbers or flat option is used
    """
    def setUp(self):
        super(CopyArtifactsFromNestedDirectoryTest, self).setUp()

    def test_dont_copy_wrong_artifacts(self):
        """
        Test if artifacts in sub folders containing files handled by beets aren't copied.
        Setup a test structure:
          the_album/
            track_1.mp3
            artifact.file
            artifact.file2
            sub_folder/
              sub_artifact.file
          top_sub_folder/
            top_sub_artifact.file
          singleton.mp3
          top_artifact.file

        After importing the singleton and the album, the files should have the following layout:
          Tag Artist/
            Tag Album/
              artifact.file
              artifact.file2
              Tag Title 1.mp3
              sub_folder/
                sub_artifact.file
          singletons/
            top_sub_folder/
              top_sub_artifact.file
            Tag Title 1.mp3
            top_artifact.file
        """
        self._create_flat_import_dir()

        album_path = os.path.join(self.import_dir, 'the_album')
        sub_folder_path = os.path.join(album_path, 'sub_folder')
        top_sub_folder_path = os.path.join(self.import_dir, 'top_sub_folder')
        os.makedirs(sub_folder_path)
        os.makedirs(top_sub_folder_path)

        open(os.path.join(sub_folder_path, 'sub_artifact.file'), 'a').close()
        open(os.path.join(top_sub_folder_path, 'top_sub_artifact.file'), 'a').close()
        open(os.path.join(self.import_dir, 'top_artifact.file'), 'a').close()

        singleton_path = os.path.join(self.import_dir, 'singleton.mp3')
        self._create_medium(singleton_path, 'full.mp3')

        self._setup_import_session(autotag=False, singletons=True, import_dir=singleton_path)
        self._run_importer()

        self.assert_in_lib_dir('singletons', 'top_artifact.file')
        self.assert_in_lib_dir('singletons', 'top_sub_folder', 'top_sub_artifact.file')
        self.assert_not_in_lib_dir('singletons', 'the_album', 'artifact.file')
        self.assert_not_in_lib_dir('singletons', 'the_album', 'artifact.file2')
        self.assert_not_in_lib_dir('singletons', 'the_album', 'sub_folder', 'sub_artifact.file')
        self.assert_not_in_lib_dir('singletons', 'Tag Artist', 'Tag Album', 'artifact.file')
        self.assert_not_in_lib_dir('singletons', 'Tag Artist', 'Tag Album', 'artifact.file2')
        self.assert_not_in_lib_dir('singletons', 'Tag Artist', 'Tag Album', 'sub_folder', 'sub_artifact.file')

        self._setup_import_session(autotag=False, import_dir=album_path)
        self._run_importer()

        self.assert_in_lib_dir('Tag Artist', 'Tag Album', 'artifact.file')
        self.assert_in_lib_dir('Tag Artist', 'Tag Album', 'artifact.file2')
        self.assert_in_lib_dir('Tag Artist', 'Tag Album', 'sub_folder', 'sub_artifact.file')
        self.assert_not_in_lib_dir('Tag Artist', 'Tag Album', 'top_sub_folder', 'top_sub_artifact.file')
        self.assert_not_in_lib_dir('Tag Artist', 'Tag Album', 'top_artifact.file')
        self.assert_not_in_lib_dir('Tag Artist', 'Tag Album', 'the_album', 'artifact.file')
        self.assert_not_in_lib_dir('Tag Artist', 'Tag Album', 'the_album', 'artifact.file2')
        self.assert_not_in_lib_dir('Tag Artist', 'Tag Album', 'the_album', 'sub_folder', 'sub_artifact.file')


if __name__ == '__main__':
    unittest.main()
