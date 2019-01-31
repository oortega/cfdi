# -*- coding: utf-8 -*-

def _read_file(path):
    with open(path, 'rb') as f:
        data = f.read()
    return data