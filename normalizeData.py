import pandas as pd

df0 = pd.read_pickle('output_initiated_all_220')
df0.index = range(0, len(df0))
for i in range(1, len(df0.index)):
    if len(df0[3][i]) == len(df0[7][i]):
        df0[3][i] = [df0[3][i][j] * df0[6][i][0] / df0[6][i][j] for j in range(len(df0[3][i]))]
        df0[4][i] = [df0[4][i][j] * df0[7][i][0] / df0[7][i][j] for j in range(len(df0[4][i]))]
    else:
        df0[3][i] = None
        df0[4][i] = None
        print('missing')

df0 = df0[df0[3].notnull()]
df0.reset_index()
df0.index = range(0, len(df0))

# df0.to_pickle('output_initiated_all_normalized_to_nasdaq_220')