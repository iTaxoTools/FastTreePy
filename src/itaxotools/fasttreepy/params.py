from itaxotools.common.param import Field, Group

params = Group(key='root', children=[
            Field('show_progress', label='Show Progress', type=bool, default=True),
            ])
