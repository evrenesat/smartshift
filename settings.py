# coding=utf-8
__author__ = 'Evren Esat Ozkan'

LIGHT_LEVELS_FOR_HOURS = [
    {
        'hours': [23, 0, 1, 2, 3, 4, 5, 6, 7],
        'light_levels': [
            [range(1, 70), 0.5],
            [range(70, 120), 0.8],
        ]
    },
    {
        'hours': [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20],
        'light_levels': [
            [range(1, 70), 0.7],
            [range(70, 300), 0.9],
        ]
    },
    {
        'hours': [21, 22],
        'light_levels': [
            [range(1, 70), 0.6],
            [range(70, 300), 0.8],
        ]
    },
]

REDSHIFT_PRESETS = {
    'off': 'redshift -x',
    #'base': "redshift -o -l 38:27 -b "
    'base': "redshift -O 5500 -b"
}
FIXED_BRIGHTNESS_APPS = (
    #(['app_name','list','for fixed'], 'preset_name', 'brightness_level (a value between 0-1) '),
    (['PyCharm', '/bin/bash', 'Reditr', 'altyazılı izle'], 'off', ''),

)
