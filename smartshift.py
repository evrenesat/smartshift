#!/usr/bin/python
import Image
import ImageStat
import subprocess as sp
from time import sleep, time, strftime
import math
from Xlib.display import Display
from Xlib import X, Xatom
from settings import *

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
    get_active_windows_cmd = "xprop -id $(xprop -root 32x '\t$0' _NET_ACTIVE_WINDOW | cut -f 2) WM_NAME WM_CLASS"
    current_brightness = 0
    current_environment = 0
    last_brigthness = 0
    ten_mins_marker = 0
    last_brigthness_check = 0

    def get_brightness_for_hour(self):
        h = int(strftime('%H'))
        for setting in LIGHT_LEVELS_FOR_HOURS:
            if h in setting['hours']:
                for ll in setting['light_levels']:
                    if self.current_environment in ll[0]:
                        print "selected light level for %s > %s:  %s" % (h, self.current_environment, ll[1])
                        return ll[1]

        print "NOT FOUND: light level for %s > %s" % (h, self.current_environment)

    def get_active_window_class_with_xprop(self):
        return sh(self.get_active_windows_cmd)[1]
        # try:
        #     name = sh(self.get_active_windows_cmd)[1]
        #     return (name.split('=')[1]).replace('"', '')
        # except IndexError:
        #     return name.replace('"', '')

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
            cur_window.get_wm_name()
            return cur_class[1]
        except Exception, e:
            print e, cur_class, cur_window, cur_window.get_wm_name()
            return cur_class[1] if cur_class else ''

    def set_brightness(self, preset='base', value=''):
        value = str(value)
        if (preset + value) != self.last_brigthness:
            sh(REDSHIFT_PRESETS[preset] + value)
            self.last_brigthness = preset + value

    def check_brightness(self, aEvent):
        #print aEvent.type
        if aEvent.type in [18, 17, 22]:
            name = self.get_active_window_class_with_xprop()
            print name
            if not name:
                return
            for b in FIXED_BRIGHTNESS_APPS:
                if filter(lambda x: x in name, b[0]):
                    self.set_brightness(b[1], b[2] if len(b) == 3 else '')
                else:
                    self.set_brightness('base', self.current_brightness)
            if self.recheck_needed():
                self.get_evironment_brightness()

    def get_evironment_brightness(self):
        sh("gst-launch -v v4l2src ! decodebin ! ffmpegcolorspace ! pngenc ! filesink location=/tmp/brightest.png")
        #http://stackoverflow.com/questions/3490727/what-are-some-methods-to-analyze-image-brightness-using-python
        im = Image.open('/tmp/brightest.png').convert('L')
        stat = ImageStat.Stat(im)
        print im.getextrema(), stat.rms
        self.current_environment = int(stat.rms[0])
        self.current_brightness = self.get_brightness_for_hour()

    def recheck_needed(self):
        """
        eger son calismamizdan bu yana 10 dakika gectiyse ortamin aydinlik miktarini kontrol eder.
        :return: bool
        """
        if time() - self.last_brigthness_check > 300:
            self.last_brigthness_check = time()
            return True



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


