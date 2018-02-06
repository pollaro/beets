from beets.plugins import BeetsPlugin
from beets import util
from beets import logging
import os
import subprocess

PIL = 1
IMAGEMAGICK = 2

log = logging.getLogger('beets')

def pil_convert(path_in):
    """Conversion using PIL"""
    from PIL import Image
    try:
        imageIn = Image.open(util.syspath(path_in))
        filename,ext = os.splitext(path_in)
        imageOut = filename + '.jpg'
        imageIn.save(imageOut)
    except IOError:
        log.error(u'PIL did not convert file {0} to jpg', util.displayable_path(path_in))
        return path_in

def im_convert(path_in, path_out=None):
    """Conversion using IMAGEMAGICK"""
    try:
        filename,ext = os.splitext(path_in)
        fileout = filename + '.jpg'
        util.command_output(['magick convert', util.syspath(path_in),util.syspath(fileout)])
    except subprocess.CalledProcessError:
        log.warning(u'ImageMagick failed to save {0} to jpg',util.displayable_path(path_in))
        return path_in

backend = {
    PIL: pil_convert,
    IMAGEMAGICK: im_convert,
}

class jpgArt(BeetsPlugin):
    """Plugin that changes cover files to jpg"""

    def __init__(self):
        """create the object with the method"""
        self.method = self._check_method()
        self.register_listener('import',self.convertJpg)
        if not self.method:
            raise NoImageProError(u'PIL or IMAGEMAGICK required and not found')
        log.debug(u'conversion is done with {0}', self.method)

    def convertJpg(self, path_in):
        """conver any type of image to jpg"""
        function = backend[self.method[0]]
        return function(path_in)

    @staticmethod
    def _check_method():
        """Return the method used"""
        version = get_im_version()
        if version:
            return IMAGEMAGICK, version

        version = get_pil_version()
        if version:
            return PIL, version

def get_im_version():
    """Return Image Magick version or None if it is unavailable
    Try invoking ImageMagick's "convert".
    """
    try:
        out = util.command_output(['convert', '--version'])

        if b'imagemagick' in out.lower():
            pattern = br".+ (\d+)\.(\d+)\.(\d+).*"
            match = re.search(pattern, out)
            if match:
                return (int(match.group(1)),
                        int(match.group(2)),
                        int(match.group(3)))
            return (0,)

    except (subprocess.CalledProcessError, OSError) as exc:
        log.debug(u'ImageMagick check `convert --version` failed: {}', exc)
        return None

def get_pil_version():
    """Return Image Magick version or None if it is unavailable
    Try importing PIL."""
    try:
        __import__('PIL', fromlist=[str('Image')])
        return (0,)
    except ImportError:
        return None
