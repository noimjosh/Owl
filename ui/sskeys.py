'''
Module for storing keys in Streamlit session state.
'''
import streamlit as st
from io import StringIO


ss = st.session_state
newCase = 'New case...'
loadConfig = 'Load config...'

# Dictionary of dictionaries for each case.
if 'cases' not in ss:
    ss.cases = {newCase: {'iname0': '', 'status': 'unkown', 'summary': ''},
                loadConfig: {'iname0': '', 'status': 'unkown', 'summary': ''}}

# Variable for storing name of current case.
if 'currentCase' not in ss:
    ss.currentCase = newCase


def allCaseNames() -> list:
    return list(ss.cases)


def onlyCaseNames() -> list:
    caseList = list(ss.cases)
    caseList.remove(newCase)
    caseList.remove(loadConfig)
    return caseList


def runOnce(func):
    key = func.__name__
    if getKey(key) is None:
        func()
    init(key, 1)


def getIndex(item, choices):
    try:
        i = choices.index(item)
    except ValueError:
        return None

    return i


def currentCaseName() -> str:
    return ss.currentCase


def switchToCase(key):
    ss.currentCase = ss['_'+key]


def isIncomplete():
    return (currentCaseName() == '' or getKey('iname0') in [None, '']
            or (getKey('status') == 'married' and getKey('iname1') in [None, '']))


def caseHasNoPlan():
    return getKey('plan') is None


def titleBar(nkey, choices=None):
    if choices is None:
        choices = onlyCaseNames()
    helpmsg = 'Select an exising case, or create a new one from scratch, or from a config file.'
    return st.sidebar.selectbox('Select case', choices, help=helpmsg,
                                index=getIndex(currentCaseName(), choices), key='_'+nkey,
                                on_change=switchToCase, args=[nkey])


def sideTitleBar(nkey, choices=None):
    if choices is None:
        choices = onlyCaseNames()
    helpmsg = 'Select an exising case, or create a new one from scratch, or from a config file.'
    return st.selectbox('Select case', choices, help=helpmsg,
                        index=getIndex(currentCaseName(), choices), key='_'+nkey,
                        on_change=switchToCase, args=[nkey])


def currentCaseDic() -> dict:
    return ss.cases[ss.currentCase]


def setCurrentCase(case):
    if case not in ss.cases:
        raise RuntimeError('Case %s not found in dictionary' % case)
    ss.currentCase = case


def duplicateCase():
    import owlbridge as owb

    for i in range(1, 10):
        dupname = ss.currentCase + '(%d)' % i
        if dupname not in ss.cases:
            break
    else:
        raise RuntimeError('Exhausted number of duplicates')

    iostring = StringIO()
    newplan = owb.clone(getKey('plan'), dupname, logstreams=[iostring])
    ss.cases[dupname] = ss.cases[ss.currentCase].copy()
    ss.cases[dupname]['name'] = dupname
    ss.cases[dupname]['plan'] = newplan
    ss.cases[dupname]['summary'] = ''
    ss.cases[dupname]['logs'] = iostring
    ss.currentCase = dupname

    # keynames = ['name', 'status', 'plan', 'summary', 'logs', 'startDate',
    #            'timeList', 'plots',
    #            'objective', 'withMedicare', 'bequest', 'netSpending',
    #            'noRothConversions', 'maxRothConversion',
    #            'rateType', 'fixedType', 'varyingType', 'yfrm', 'yto',
    #            'divRate', 'heirsTx', 'gainTx', 'profile', 'survivor', ]
    # keynamesJ = ['fxRate', 'mean', 'sdev', ]
    # keynamesI = ['iname', 'yob', 'life', 'txbl', 'txDef', 'txFree',
    #             'ssAge', 'ssAmt', 'pAge', 'pAmt', 'df',
    #             'init%0_', 'init%1_', 'init%2_', 'init%3_',
    #             'fin%0_', 'fin%1_', 'fin%2_', 'fin%3_', ]


def createCaseFromConfig(confile):
    import owlbridge as owb
    name, dic = owb.createCaseFromConfig(confile)
    if name == '':
        return False
    elif name in ss.cases:
        st.error("Case name '%s' already exists." % name)
        return False

    ss.cases[name] = dic
    setCurrentCase(name)
    return True


def createCase(case):
    if case == 'newcase':
        # Widget stored case name in _newname.
        casename = ss._newcase

    if casename == '' or casename in ss.cases:
        return

    ss.cases[casename] = {'name': casename, 'summary': '', 'logs': None}
    setCurrentCase(ss._newcase)


def renameCase(key):
    if ss.currentCase == newCase or ss.currentCase == loadConfig:
        return
    newname = ss['_'+key]
    plan = getKey('plan')
    if plan:
        plan.rename(newname)
    ss.cases[newname] = ss.cases.pop(ss.currentCase)
    ss.cases[newname]['name'] = newname
    setCurrentCase(newname)


def deleteCurrentCase():
    if ss.currentCase == newCase or ss.currentCase == loadConfig:
        return
    del ss.cases[ss.currentCase]
    setCurrentCase(newCase)


def dump():
    print('State Dump:', ss)


def pull(key):
    # print('pulling', key, 'from', '_'+key, 'as', ss['_'+key])
    return setKey(key, ss['_'+key])


def setKey(key, val):
    # print('storing', key, 'as', val)
    ss.cases[ss.currentCase][key] = val
    return val


def init(key, val):
    if key not in ss.cases[ss.currentCase]:
        # print('init', key, 'as', val)
        ss.cases[ss.currentCase][key] = val


def getKey(key):
    if key in ss.cases[ss.currentCase]:
        return ss.cases[ss.currentCase][key]
    else:
        return None


def getDict(key=ss.currentCase):
    return ss.cases[key]


def getIntNum(text, nkey, disabled=False, callback=pull, step=1, max_value=None):
    return st.number_input(text,
                           value=int(getKey(nkey)),
                           disabled=disabled,
                           min_value=0,
                           max_value=max_value,
                           step=step,
                           on_change=callback, args=[nkey], key='_'+nkey)


def getNum(text, nkey, disabled=False, callback=pull, step=10., min_value=0., max_value=None, format='%.1f'):
    return st.number_input(text,
                           value=float(getKey(nkey)),
                           disabled=disabled,
                           step=step,
                           min_value=min_value,
                           max_value=max_value,
                           format=format,
                           on_change=callback, args=[nkey], key='_'+nkey)


def getText(text, nkey, disabled=False, callback=pull, placeholder=None):
    return st.text_input(text,
                         value=getKey(nkey),
                         disabled=disabled,
                         on_change=callback, args=[nkey], key='_'+nkey,
                         placeholder=placeholder)


def getRadio(text, choices, nkey, callback=pull):
    return st.radio(text, choices,
                    index=choices.index(getKey(nkey)),
                    on_change=callback, args=[nkey], key='_'+nkey,
                    horizontal=True)


def getToggle(text, nkey, callback=pull):
    return st.toggle(text, value=getKey(nkey),
                     on_change=callback, args=[nkey], key='_'+nkey)
