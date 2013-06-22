#!/usr/bin/python
import Image
import ImageStat
import subprocess as sp
from time import sleep, time
import math
from Xlib.display import Display
from Xlib import X, Xatom
#apt-get install gstreamer-tools, redshift

def sh(cmd):
    # print cmd
    k = sp.Popen(cmd, shell=True, stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE, close_fds=False)
    error = k.stderr.read()
    output = k.stdout.read().strip()
    if error:
        output = error + output
    k.wait()
    return not error, (output or 'OK')


class Autolighter(object):
    brightness_tracehold = 80
    redshift_base = "redshift -o -l 38:27 -b %s"
    get_active_windows_cmd = "xprop -id $(xprop -root 32x '\t$0' _NET_ACTIVE_WINDOW | cut -f 2) WM_CLASS"

    for_darkness = 0.6
    for_lightness = 0.8
    default_brightness = 0  # dark yada light bunun ustune yazar

    fixed_brightness = (
        #(['app_name','list','for fixed', 'brightness_level'], 'a value between 0-1'), 0 min 1 max
        (['pycharm', 'terminal', 'FocusProxy'], 1),

    )
    last_brigthness = 0
    ten_mins_marker = 0
    last_brigthness_check = 0

    def get_active_window_class_with_xprop(self):
        name = sh(self.get_active_windows_cmd)[1]
        return (name.split('=')[1]).replace('"', '')

    def get_active_window_class_with_xlib(self):
        #FIXME: not working for java windows, always returns "FocusProxy"
        cur_window = display.get_input_focus().focus
        cur_class = None
        while cur_class is None:
            cur_class = cur_window.get_wm_class()
            if cur_class is None:
                cur_window = cur_window.query_tree().parent
        return cur_class[1]

    def check_brightness(self, aEvent):
        # print aEvent.type
        if aEvent.type in [17, 22]:
            name = self.get_active_window_class_with_xlib()
            for b in self.fixed_brightness:
                if filter(lambda x: x in name, b[0]):
                    if b[1] != self.last_brigthness:
                        self.last_brigthness = b[1]
                        sh(self.redshift_base % b[1])
                elif self.last_brigthness != self.default_brightness:
                    sh(self.redshift_base % self.default_brightness)
                    self.last_brigthness = self.default_brightness
            self.set_current_default()
                # elif time() - self.last_brigthness_check > 600:
                #     # 1 saattir pencere degismemisse zorla calistiriyoruz.
                #     self.last_brigthness = 0

    def brightness(self):
        sh("gst-launch -v v4l2src ! decodebin ! ffmpegcolorspace ! pngenc ! filesink location=/tmp/brightest.png")
        #http://stackoverflow.com/questions/3490727/what-are-some-methods-to-analyze-image-brightness-using-python
        im = Image.open('/tmp/brightest.png')
        stat = ImageStat.Stat(im)
        r, g, b = stat.mean
        return math.sqrt(0.241 * (r ** 2) + 0.691 * (g ** 2) + 0.068 * (b ** 2))

    def recheck_needed(self):
        """
        eger son calismamizdan bu yana 10 dakika gectiyse ortamin aydinlik miktarini kontrol eder.
        :return: bool
        """
        if time() - self.last_brigthness_check > 60:
            self.last_brigthness_check = time()
            return True

    def set_current_default(self):
        """
        eger brightness metodundan donen deger brighness_tracehold'dan fazla ise default arka isigi
        aydinlik (0.8) ortama gore ayarlar, yoksa karanlik (0.6) oratama gore ayarlar.
        :return: None
        """
        if self.recheck_needed():
            current_environment = self.brightness()
            print "environment", current_environment
            if current_environment > self.brightness_tracehold:
                self.default_brightness = self.for_lightness
                print "set default for lightness"
            else:
                self.default_brightness = self.for_darkness
                print "set default for darkness"


if __name__ == "__main__":
    al = Autolighter()
    display = Display()
    root = display.screen().root
    root.change_attributes(event_mask=X.SubstructureNotifyMask)
    while True:
        ev = display.next_event()
        al.check_brightness(ev)



