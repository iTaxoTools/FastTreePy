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
                Field('gamma', label='Gamma', type=int, list=[1, 2, 3], default=2),
                Field('delta', label='Delta', type=bool, value=True),
                Field('string', label='STRING', type=str, value='True'),
                Field('int', label='INTEGER', type=int, value=1),
                Field('float', label='FLOAT', type=float, value=1.2),
                Field('epsilon', label='Epsilon',
                    type=int, range=(1, 10), value=1),
                Group(
                    key='special',
                    label='Special',
                    children=[
                        Field('sigma', label='SSigma', value='st'),
                        Field('taph', label='Taph', value='ts'),
                ]),
                Group(
                    key='special2',
                    label='Special2',
                    children=[
                        Field('sigma', label='SigmaSgma', value='st'),
                        Field('taph', label='Taph', value='ts'),
                        Group(
                            key='special',
                            label='Special',
                            children=[
                                Field('sigma', label='SaSigma', value='st'),
                                Field('taph', label='Taph', value='ts'),
                        ]),
                ]),
            ]),
        Group(
            key='general2',
            label='General2',
            children=[
                Field('gamma', label='Gamma', type=int, list=[1, 2, 3], default=2),
                Field('delta', label='Delta', type=bool, value=True),
                Field('string', label='STRING', type=str, value='True'),
                Field('int', label='INTEGER', type=int, value=1),
                Field('float', label='FLOAT', type=float, value=1.2),
                Field('epsilon', label='Epsilon',
                    type=int, range=(1, 10), value=1),
                Group(
                    key='special',
                    label='Special',
                    children=[
                        Field('sigma', label='Sigma', value='st'),
                        Field('taph', label='Taph', value='ts'),
                ]),
                Group(
                    key='special2',
                    label='Special2',
                    children=[
                        Field('sigma', label='SigmaSgma', value='st'),
                        Field('taph', label='Taph', value='ts'),
                        Group(
                            key='special',
                            label='Special',
                            children=[
                                Field('sigma', label='SaSigma', value='st'),
                                Field('taph', label='Taph', value='ts'),
                        ]),
                ]),
            ]),
    ])
