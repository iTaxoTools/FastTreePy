from itaxotools.common.param import Field, Group

params = Group(key='root', children=[
            Group(key='sequence',
                  label='Sequence',
                  children=[
                Field(key='ncodes',
                      label='Type',
                      type=int,
                      list={4: 'Nucleotide',
                            20: 'Protein'},
                      default=4),
                Field(key='pseudo',
                      label='Use distance pseudocounts',
                      doc=("Use pseudocounts to estimate distances between\n"
                           "sequences with little or no overlap. Recommended\n"
                           "for highly gapped sequences (weight=1)."),
                      type=bool,
                      default=False),
                Field(key='quote',
                      label='Quote full names',
                      doc=("Quote sequence names in the output and allow\n"
                           "spaces, commas, parentheses and colons in them,\n"
                           "but not single quote characters (fasta files only)."),
                      type=bool,
                      default=False),
                ]),
            Group(key='model',
                  label='Model Options',
                  children=[
                Field(key='ml_model',
                      label='ML model',
                      doc=("Maximum likelihood model:\n"
                           " - JTT: Jones-Taylor-Thorton 1992 (a.a. only)\n"
                           " - WAG: Whelan-And-Goldman 2001 (a.a. only)\n"
                           " - LG: Le-Gascuel 2008 (a.a. only)\n"
                           " - JC: Jukes-Cantor (nt only)\n"
                           " - GTR: Generalized time-reversible (nt only)"),
                      type=str,
                      list={'jtt': 'JTT', # aa
                            'wag': 'WAG', # aa
                            'lg':  'LG',  # aa
                            'jc':  'JC', # nt
                            'gtr': 'GTR'}, # nt
                      default='jtt'),
                Field(key='ncat',
                      label='CAT number',
                      doc=("The number of rate categories of sites.\n"
                           "Enter 1 for no CAT model (default 20)."),
                      type=int,
                      range=(1, None),
                      default=20),
                Field(key='second',
                      label='2nd-level top hits heuristic',
                      doc=("Reduces memory usage and running time but\n"
                           "may lead to marginal reductions in tree quality."),
                      type=bool,
                      default=True),
                Field(key='fastest',
                      label='Faster neighbor-joining',
                      doc=("Speed up the neighbor-joining phase by\n"
                           "turning off local hill-climbing search.\n"
                           "Also use top-hits heuristic more aggressively.\n"
                           "Recommended for over 50,000 sequences."),
                      type=bool,
                      default=True),
                ]),
            Group(key='topology',
                  label='Topology Refinement',
                  children=[
                Field(key='spr',
                      label='SPR rounds',
                      doc=("Number of Subtree-Prune-Regraft rounds\n"
                           "(default 2)."),
                      type=int,
                      default=2),
                Field(key='mlnni',
                      label='ML-NNI limit',
                      doc=("Limit the number of rounds of maximum-likelihood\n"
                           "nearest-neighbor interchanges. If set to -1,\n"
                           "do 2*log(N) rounds, where N is the number of\n"
                           "unique sequences (default). If set to 0, turn off\n"
                           "both min-evo NNIs and SPRs"),
                      type=int,
                      default=-1),
                Field(key='exhaustive',
                      label='Exhaustive NNIs',
                      doc=("Turn off heuristics to avoid constant subtrees\n"
                           "(affects both ML and ME NNIs). Additionally,\n"
                           "always optimize all 5 branches at each NNI\n"
                           "in 2 rounds."),
                      type=bool,
                      default=False),
                ])
            ])
