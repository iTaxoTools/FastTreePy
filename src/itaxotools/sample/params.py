from itaxotools.common.param import Field, Group

params = Group(
    key='root',
    children=[
        Field('alpha', label='Alpha', default='lorem'),
        Field('beta', label='Beta', value=42, doc='The answer'),
        Group(
            key='general',
            label='General',
            children=[
                Field('gamma', label='Gamma', list=[1, 2, 3], value=2),
                Field('delta', label='Delta', type=int, value=1),
                Field('epsilon', label='Epsilon',
                    type=int, range=(1, 10), value=1),
            ])
    ])
