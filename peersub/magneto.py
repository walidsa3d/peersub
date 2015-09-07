from collections import defaultdict

from requests.utils import unquote


def parse(magnet_uri):
    """returns a dictionary of parameters contained in the uri"""
    data = defaultdict(list)
    if not magnet_uri.startswith('magnet:'):
        return data
    else:
        magnet_uri = magnet_uri.strip("magnet:?")
        trackers = []
        for segment in magnet_uri.split('&'):
            key, value = segment.split("=")
            if key == 'dn':
                data['name'] = unquote(value).replace('+', '.')
            elif key == 'xt':
                data['infoHash'] = value.strip('urn:btih:')
            elif key == 'tr':
                data['trackers'].append(unquote(value))
            else:
                data[key] = value
    return data


def prettyprint(magnetdata):
    for k, v in magnetdata.iteritems():
        if type(v) is list:
            print "{} : {}".format(k, ', '.join(v))
        else:
            print "{} : {}".format(k, v)
