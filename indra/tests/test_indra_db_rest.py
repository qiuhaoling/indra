from __future__ import absolute_import, print_function, unicode_literals
from builtins import dict, str

from datetime import datetime

from nose.plugins.attrib import attr
from indra.sources import indra_db_rest as dbr


def __check_request(seconds, *args, **kwargs):
    now = datetime.now()
    stmts = dbr.get_statements(*args, **kwargs)
    assert stmts, "Got no statements."
    time_taken = datetime.now() - now
    assert time_taken.seconds < seconds


@attr('nonpublic')
def test_simple_request():
    __check_request(5, 'MAP2K1', 'MAPK1', stmt_type='Phosphorylation')


@attr('nonpublic')
def test_null_request():
    try:
        dbr.get_statements()
    except dbr.IndraDBRestError:
        return
    except BaseException as e:
        assert False, "Raised wrong exception: " + str(e)
    assert False, "Null request did not raise any exception."


@attr('nonpublic')
def test_large_request():
    __check_request(20, agents=['AKT1'])


@attr('nonpublic')
def test_bigger_request():
    __check_request(30, agents=['MAPK1'])


@attr('nonpublic')
def test_too_big_request():
    try:
        __check_request(30, agents=['TP53'])
    except dbr.IndraDBRestError as e:
        if '502: Bad Gateway' in str(e):
            pass  # This is the error that indicates the too much data.
        else:
            assert False, 'Unexpected error occured: %s' % str(e)
    except BaseException as e:
        assert False, 'A very unexpected error occured: %s' % str(e)


@attr('nonpublic')
def test_famplex_namespace():
    stmts = dbr.get_statements('PDGF@FPLX', 'FOS', stmt_type='IncreaseAmount')
    print(len(stmts))
    assert all([s.agent_list()[0].db_refs.get('FPLX') == 'PDGF' for s in stmts]),\
        'Not all subjects match.'
    assert all([s.agent_list()[1].name == 'FOS' for s in stmts]),\
        'Not all objects match.'


@attr('nonpublic')
def test_paper_query():
    stmts_1 = dbr.get_statements_for_paper('PMC5770457', 'pmcid')
    assert len(stmts_1)
    stmts_2 = dbr.get_statements_for_paper('8436299')
    assert len(stmts_2)