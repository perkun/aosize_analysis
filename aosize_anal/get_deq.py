import pandas as pd


class AspectRange:
    def __init__(self):
        self.min_aspect = 0
        self.max_aspect = 0
        self.avg_kmppx = 0
        self.deq_min = 0
        self.deq_max = 0
        self.deq_nominal = 0
        self.valid = False


def get_deq_unweighted(database):
    data = pd.read_sql_query("SELECT * from Images WHERE deq_nominal != 0",
                             database.con)
    mean_deq = data['deq_nominal'].mean()
    deq_plus = data['deq_max'].mean() - mean_deq
    deq_minus = mean_deq - data['deq_min'].mean()

    return mean_deq, deq_plus, deq_minus


def get_deq_weighted(database, aspect_ranges):
    data = pd.read_sql_query(
        "SELECT id, deq_min, deq_max, deq_nominal, kmppx, aspect "
        "FROM Images WHERE kmppx != 0", database.con)

    # weight by kmppx
    for ar in aspect_ranges:
        filt = (data['aspect'] >= ar.min_aspect) & (
            data['aspect'] < ar.max_aspect)
        flt_data = data[filt]
        if flt_data.empty:
            print(f"[{ar.min_aspect}, {ar.max_aspect}] range is empty")
            ar.valid = False
            continue

        inverse_kmppx_df = 1.0/flt_data['kmppx']

        ar.deq_nominal = (flt_data['deq_nominal']*inverse_kmppx_df).sum() / \
            inverse_kmppx_df.sum()

        ar.deq_min = (flt_data['deq_min']*inverse_kmppx_df).sum() / \
            inverse_kmppx_df.sum()

        ar.deq_max = (flt_data['deq_max']*inverse_kmppx_df).sum() / \
            inverse_kmppx_df.sum()

        ar.avg_kmppx = flt_data['kmppx'].mean()

        ar.valid = True

    deq_min_sum = 0
    deq_max_sum = 0
    deq_nominal_sum = 0
    weights_sum = 0

    for ar in aspect_ranges:
        if not ar.valid:
            continue
        deq_min_sum += ar.deq_min / ar.avg_kmppx
        deq_max_sum += ar.deq_max / ar.avg_kmppx
        deq_nominal_sum += ar.deq_nominal / ar.avg_kmppx
        weights_sum += 1.0/ar.avg_kmppx

    deq_min = deq_min_sum / weights_sum
    deq_max = deq_max_sum / weights_sum
    deq_nominal = deq_nominal_sum / weights_sum

    deq_plus = deq_max - deq_nominal
    deq_minus = deq_nominal - deq_min

    database.execute("UPDATE Results SET "
                     f"deq_nominal = {deq_nominal}, "
                     f"deq_min = {deq_min}, "
                     f"deq_max = {deq_max}, "
                     f"deq_plus = {deq_plus}, "
                     f"deq_minus = {deq_minus} "
                     "WHERE id = 1")

    return deq_nominal, deq_plus, deq_minus, aspect_ranges

    # store results in database (for plots, etc)

