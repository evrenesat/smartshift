#!/usr/bin/python
import Image
import ImageStat
import subprocess as sp
from time import sleep, time, strftime
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


class SmartShift(object):
    brightness_tracehold = 65

    get_active_windows_cmd = "xprop -id $(xprop -root 32x '\t$0' _NET_ACTIVE_WINDOW | cut -f 2) WM_CLASS"

    brightness_for = [
        {
            'hours': [22, 0, 1, 2, 3, 4, 5, 6, 7],
            'light_levels': [
                [range(1, 70), 0.5],
                [range(70, 120), 0.8],
            ]
        },
        {
            'hours': [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21],
            'light_levels': [
                [range(1, 70), 0.57],
                [range(70, 120), 0.9],
            ]
        }
    ]
    for_darkness = 0.6
    for_lightness = 0.9
    default_brightness = 0  # dark yada light bunun ustune yazar

    redshift_presets = {
        'off': 'redshift -x',
        #'base': "redshift -o -l 38:27 -b "
        'base': "redshift -O 5500 -b"
    }

    fixed_brightness = (
        #(['app_name','list','for fixed'], 'preset_name', 'brightness_level (a value between 0-1) '),
        (['pycharm', 'terminal', 'FocusProxy'], 'off', ''),

    )
    current_environment = 0
    last_brigthness = 0
    ten_mins_marker = 0
    last_brigthness_check = 0


    def get_brightness_for_hour(self):
        h = int(strftime('%H'))
        for ho in self.brightness_for:


    def get_active_window_class_with_xprop(self):
        name = sh(self.get_active_windows_cmd)[1]
        return (name.split('=')[1]).replace('"', '')

    def get_active_window_class_with_xlib(self):
        #FIXME: not working for java windows, always returns "FocusProxy"
        cur_window = display.get_input_focus().focus
        cur_class = None
        try:
            while cur_class is None:
                if not cur_window:
                    return
                cur_class = cur_window.get_wm_class()
                if cur_class is None:
                    cur_window = cur_window.query_tree().parent
            print cur_class[1]
            return cur_class[1]
        except Exception, e:
            print e, cur_class, cur_window
            return cur_class[1] if cur_class else ''

    def set_brightness(self, preset='base', value=''):
        value = str(value)
        if (preset + value) != self.last_brigthness:
            sh(self.redshift_presets[preset] + value)
            self.last_brigthness = preset + value

    def check_brightness(self, aEvent):
        #print aEvent.type
        if aEvent.type in [18, 17, 22]:
            name = self.get_active_window_class_with_xlib()
            if not name:
                return
            for b in self.fixed_brightness:
                if filter(lambda x: x in name, b[0]):
                    self.set_brightness(b[1], b[2] if len(b) == 3 else '')
                else:
                    self.set_brightness('base', self.default_brightness)
            self.set_current_default()
            # elif time() - self.last_brigthness_check > 600:
            #     # 1 saattir pencere degismemisse zorla calistiriyoruz.
            #     self.last_brigthness = 0

    def brightness(self):
        sh("gst-launch -v v4l2src ! decodebin ! ffmpegcolorspace ! pngenc ! filesink location=/tmp/brightest.png")
        #http://stackoverflow.com/questions/3490727/what-are-some-methods-to-analyze-image-brightness-using-python
        im = Image.open('/tmp/brightest.png').convert('L')
        stat = ImageStat.Stat(im)
        print im.getextrema(), stat.rms
        return stat.rms[0]

    def recheck_needed(self):
        """
        eger son calismamizdan bu yana 10 dakika gectiyse ortamin aydinlik miktarini kontrol eder.
        :return: bool
        """
        if time() - self.last_brigthness_check > 300:
            self.last_brigthness_check = time()
            return True

    def set_current_default(self):
        """
        eger brightness metodundan donen deger brighness_tracehold'dan fazla ise default arka isigi
        aydinlik (0.8) ortama gore ayarlar, yoksa karanlik (0.6) oratama gore ayarlar.
        :return: None
        """
        if self.recheck_needed():
            self.current_environment = self.brightness()
            print "environment", self.current_environment
            if self.current_environment > self.brightness_tracehold:
                self.default_brightness = self.for_lightness
                print "set default for lightness"
            else:
                self.default_brightness = self.for_darkness
                print "set default for darkness"


if __name__ == "__main__":
    ss = SmartShift()
    display = Display()
    root = display.screen().root
    root.change_attributes(event_mask=X.SubstructureNotifyMask)
    try:
        while True:
            ev = display.next_event()
            ss.check_brightness(ev)
    except KeyboardInterrupt:
        sh('redshift -x')


