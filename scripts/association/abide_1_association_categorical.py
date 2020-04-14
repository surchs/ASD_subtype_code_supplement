import sys
import pathlib as pal
sys.path.append(str(pal.Path(__file__).resolve().parents[2]))
import asdfc
import argparse
import numpy as np
import pandas as pd
from statsmodels.sandbox.stats import multicomp as smi


def associate_categorical(group, case, control):
    # Hardcoded variables
    regressors = 'AGE_AT_SCAN+fd_scrubbed+SITE_ID'
    part_thr = 20
    dist_thr = 0.99
    scale = 20

    # Paths
    root_p = pal.Path(__file__).resolve().parents[2] / 'data'
    pheno_p = root_p / 'pheno/ABIDE1_Pheno_PSM_matched_minimum_10.tsv'
    weight_d = root_p / f'processed/weights/abide_1/MIST_{scale}'
    weight_t = f'roi_{{}}_mist_{scale}_abide_1_{"_and_".join(regressors.split("+"))}_core_{part_thr:d}_within_{dist_thr*100:.0f}_nocereb.npy'
    labels_p = root_p / f'ATLAS/MIST/Parcel_Information/MIST_{scale}_nocereb.csv'
    out_d = root_p / f'table/associations/'
    out_p = out_d / f'abide_categorical_assoc_mist_{scale}_with_{group}_{part_thr:d}_within_{dist_thr*100:.0f}_nocereb.tsv'
    if not out_d.is_dir():
        out_d.mkdir()

    pheno = pd.read_csv(pheno_p, sep='\t')
    pheno.reset_index(inplace=True)
    labels = pd.read_csv(labels_p, sep=';')
    
    res_list = list()
    for seed_id in range(labels.shape[0]):
        seed_name = labels.iloc[seed_id]['label']
        roi_number = labels.iloc[seed_id]['roi']
        weight = np.load(weight_d / weight_t.format(roi_number))
        for sbt_id in range(weight.shape[1]):
            results = asdfc.stats.t_test(weight[:, sbt_id], pheno, group, case, control)
            results['seed_id'] = roi_number
            results['seed'] = seed_name
            results['sd'] = np.std(weight[:, sbt_id])
            results['subtype'] = sbt_id+1
            results['subtype_name'] = f'{seed_name}_{sbt_id+1}'
            res_list.append(results)
    table = pd.DataFrame(data=res_list)
    # Add FDR correction
    table.loc[:, ('FDR')] = smi.multipletests(table.p, alpha=0.05, method='fdr_bh')[0]
    table.loc[:, ('q_value')] = smi.multipletests(table.p, alpha=0.05, method='fdr_bh')[1]
    table.to_csv(out_p, sep='\t', index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("contrast", type=str,
                        help="specify the categorical variable you want to contrast for. Only supports binary groups")
    parser.add_argument("case", type=str,
                        help="specify the group variable label corresponding to cases")
    parser.add_argument("control", type=str,
                        help="specify the group variable label corresponding to controls")
    args = parser.parse_args()
    associate_categorical(args.contrast, args.case, args.control)