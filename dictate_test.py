#!/usr/bin/env python
# coding: utf8

import deptest
import datetime
import copy
from dictate import retrieve_dict, hash_dict, map_dict


DICT_SAMPLE = {
    'id': 'T001',
    'name': 'reorx',
    'nature': {
        'luck': 1,
    },
    'people': ['foo', 'bar'],
    'disks': [
        {
            'is_primary': True,
            'last_modified': datetime.datetime.now(),
            'volums': [
                {
                    'name': 'EVA-01',
                    'size': 1048,
                    'block': [1, 2, 3]
                }
            ]
        }
    ],
    'extra': float(1.234)
}


def make_d(**kwargs):
    d = copy.deepcopy(DICT_SAMPLE)
    d.update(kwargs)
    return d


def test_retrieve_dict():
    d = make_d()
    assert d['name'] == retrieve_dict(d, 'name')
    assert d['people'][1] == retrieve_dict(d, 'people.[1]')
    assert d['nature']['luck'] == retrieve_dict(d, 'nature.luck')
    assert d['disks'][0]['volums'][0]['size'] == retrieve_dict(d, 'disks.[0].volums.[0].size')


@deptest.depend_on('test_retrieve_dict')
def test_map_dict():
    d = make_d()
    mapping = map_dict(d)
    for k, v in mapping.iteritems():
        assert retrieve_dict(d, k) == v


def test_hash_dict():
    d1 = make_d()
    d2 = make_d()
    assert d1 is not d2
    assert hash_dict(d1) == hash_dict(d2)

    # change d2
    d2['id'] = 'T002'
    assert hash_dict(d1) != hash_dict(d2)

    # acturally a test for validate_dict,
    # to test whether dict is changed or not after validate process
    d3 = make_d()
    hash_before = hash_dict(d3)
    assert hash_dict(d3) == hash_before
