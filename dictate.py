#!/usr/bin/env python
# -*- coding: utf-8 -*-

from hashlib import md5


__version__ = '0.1.0'


def _parse_key(k):
    if k.startswith('[') and k.endswith(']'):
        k = int(k[1:-1])
    return k


def _combine_key(keys):
    return '.'.join(keys)


def retrieve_dict(doc, dot_path):
    """Retrive value from a nested dict, using path like this:
        foo.bar.[0].player
    :raises: KeyError, for not be able to find the value by path
    :raises: ValueError, for invalid path format
    """
    def recurse_dict(d, keys, used):
        try:
            k = keys.pop(0)
        except IndexError:
            return d

        # d must be list or dict at this time
        if not isinstance(d, (list, dict)):
            used_path = _combine_key(used)
            raise KeyError(
                'Failed to get {} after {}: {} is not a list or dict'.format(k, used_path, used_path))

        pk = _parse_key(k)
        try:
            d = d[pk]
        except IndexError:
            used_path = _combine_key(used)
            raise KeyError(
                'Failed to get {} after {}: {} not exist'.format(k, used_path, k))
        except KeyError:
            used_path = _combine_key(used)
            raise KeyError(
                'Failed to get {} after {}: {} not exist'.format(k, used_path, k))

        used.append(k)
        return recurse_dict(d, keys, used)

    keys = dot_path.split('.')

    return recurse_dict(doc, keys, [])


def map_dict(o):
    def recurse_doc(mapping, d, pk):
        if isinstance(d, dict):
            for k, v in d.iteritems():
                if pk is None:
                    ck = k
                else:
                    ck = pk + '.' + k
                recurse_doc(mapping, v, ck)
        elif isinstance(d, list):
            for loop, i in enumerate(d):
                ck = pk + '.' + '[%s]' % loop
                recurse_doc(mapping, i, ck)
        else:
            mapping[pk] = d
        return mapping

    return recurse_doc({}, o, None)


def hash_dict(o):
    """
    As dict is not hashable, this function is to generate a hash string
    from a dict unnormally, use every key & value of the dict,
    join then up and compute its md5 value.
    """
    seprator = '\n'
    mapping = map_dict(o)
    keys = mapping.keys()

    # get rid the random effect of dict keys, to ensure same dict will result to same value.
    keys.sort()

    string = seprator.join(['%s:%s' % (k, mapping[k]) for k in keys])
    return md5(string).hexdigest()


def diff_dicts(new, origin):
    """Only compare the first layer, return a the dict that represent
    add, remove, modify changes from new to origin

    NOTE: If one of the two dicts comes from another, eg. from .copy(),
    # make sure new and origin are totally different from each other,
    that means, the result may not be as you think. So use deepcopy in case.
    """
    diff = {
        '+': {},
        '-': [],
        '~': {}
    }
    for k, v in new.iteritems():
        if k not in origin:
            diff['+'][k] = v
            continue
        if v != origin[k]:
            diff['~'][k] = v

    for k in origin:
        if k not in new:
            diff['-'].append(k)

    return diff
