# -*- coding: UTF-8 -*-

import os


class Variables:
    # Project variables
    PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))

    # Database variables
    DATABASE_PATH = 'datas'
    LOCAL_DICT_MAX_SIZE = 5 * (1024 * 1024)  # 5 Mb
    LOCAL_DICT_MIN_COUNT = 100  # 100 elements
    LOCAL_DICT_CLEAN_COEF = (2 / 3)

    # API Dictionary variables
    DICTIONARY_API_HOST = '127.0.0.1'
    DICTIONARY_API_PORT = 5000
    DICTIONARY_API_URL = 'http://{}:{}'.format(
        DICTIONARY_API_HOST,
        DICTIONARY_API_PORT
    )
