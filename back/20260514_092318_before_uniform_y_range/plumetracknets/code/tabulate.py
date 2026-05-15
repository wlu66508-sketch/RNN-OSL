#!/usr/bin/env python
"""Summarize evaluation CSV files under a model directory.

Run directly, for example:
    python tabulate.py --base_dir ~/plume/plumezoo/
"""

import argparse
from pathlib import Path


ELIGIBLE_DATASETS = [
    'constantx5b5',
    'switch15x5b5',
    'switch30x5b5',
    'switch45x5b5',
    'noisy3x5b5',
    'noisy6x5b5',
    'constantx5b5_0.8',
    'constantx5b5_0.6',
    'constantx5b5_0.4',
    'constantx5b5_0.2',
]

COL_ORDER = [
    'total',
    'constantx5b5',
    'switch45x5b5',
    'noisy3x5b5',
    'noisy6x5b5',
    'switch30x5b5',
    'switch15x5b5',
    'constantx5b5_0.8',
    'constantx5b5_0.6',
    'constantx5b5_0.4',
    'constantx5b5_0.2',
    'model_dir',
]


def build_counts_df(base_dir):
    import pandas as pd
    import tqdm

    base_path = Path(base_dir).expanduser()
    fnames = list(base_path.rglob('*_summary.csv'))

    counts = []
    for fname in tqdm.tqdm(fnames):
        summary_df = pd.read_csv(fname)
        dataset = fname.name.replace('_summary.csv', '')
        counts.append({
            'dataset': dataset,
            'HOME': sum(summary_df['reason'] == 'HOME'),
            'OOB': sum(summary_df['reason'] == 'OOB'),
            'OOT': sum(summary_df['reason'] == 'OOT'),
            'total': len(summary_df['reason']),
            'seed': str(fname).split('seed')[-1].split('/')[0],
            'model_dir': str(fname).replace(f'{dataset}_summary.csv', '').replace(str(base_path), ''),
            'fname': str(fname),
        })

    return pd.DataFrame(counts)


def main(argv=None):
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--base_dir', default='./')
    args = parser.parse_args(argv)

    base_path = Path(args.base_dir).expanduser()
    print("Batch/CLI mode")
    print(base_path)

    counts_df = build_counts_df(base_path)
    print(counts_df.shape)
    counts_df = counts_df.query("dataset in @ELIGIBLE_DATASETS")
    print(counts_df.shape)

    if counts_df.empty:
        print("No eligible summary CSV files found.")
        return

    pivot_df = counts_df.pivot(index='model_dir', columns='dataset', values='HOME').reset_index()
    pivot_df['total'] = pivot_df.sum(axis=1, skipna=True)

    for col in COL_ORDER:
        if col not in pivot_df.columns:
            pivot_df[col] = 0

    pivot_df = pivot_df[COL_ORDER]
    pivot_df = pivot_df.sort_values(by='total', ascending=False)

    pivot_df.to_csv(base_path / 'tabulated.tsv', sep='\t', index=False)
    pivot_df.to_csv(base_path / 'tabulated.csv', index=False)


if __name__ == "__main__":
    main()
