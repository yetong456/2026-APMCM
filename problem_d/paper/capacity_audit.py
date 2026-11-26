"""Replay the fixed predictors and vary the direct regressor's tree budget."""
from time import perf_counter

import numpy as np
import pandas as pd
from catboost import CatBoostRegressor

from screen import HERE, OUT, composition_features, fit_mixture, load_file, predict_mixture
from compare_surrogates import model_options


def summarize(scored, seed, method, trees, seconds):
    groups = {"All": scored, "Q2": scored[scored.X.eq("NO2")],
              "Q3": scored[scored.X.isin(["O3", "NO2", "FO2"])]}
    for pool, group in groups.items():
        ranked = group.sort_values(["score", "id"])
        first = ranked.iloc[0]
        yield dict(seed=seed, model=method, trees=trees, pool=pool, n=len(ranked),
                   hits50=int(ranked.head(50).V.lt(1).sum()), first_id=int(first.id),
                   first_V=first.V, regret=first.V-group.V.min(),
                   mae=(group.score-group.V).abs().mean(), fit_seconds=seconds)


def run():
    train, validation = load_file("02"), load_file("03")
    features = composition_features(train)
    new_features = composition_features(validation)
    output = []
    for seed in (26, 42):
        archived = pd.read_csv(HERE.parent / "results" / f"validation_seed{seed}.csv").set_index("id")
        archived = archived.loc[validation.id]
        options = model_options(seed)
        per_component = options["iterations"]
        start = perf_counter()
        mixture = fit_mixture(train, features, seed)
        seconds = perf_counter()-start
        prediction = predict_mixture(mixture, new_features)
        np.testing.assert_allclose(prediction, archived.mixture, rtol=0, atol=1e-7)
        output.extend(summarize(validation.assign(score=prediction), seed, "mixture",
                                3*per_component, seconds))
        # The gate sees all rows. The two disjoint branch subsets together use
        # one training set per iteration. Tree count and row exposure differ.
        for trees in (per_component, 2*per_component, 3*per_component):
            options["iterations"] = trees
            start = perf_counter()
            model = CatBoostRegressor(**options).fit(features, train.V)
            seconds = perf_counter()-start
            prediction = model.predict(new_features)
            if trees == per_component:
                np.testing.assert_allclose(prediction, archived.direct, rtol=0, atol=1e-7)
            output.extend(summarize(validation.assign(score=prediction), seed, "direct",
                                    trees, seconds))
            print(f"seed {seed}, {trees} trees, {seconds:.1f} s", flush=True)
    pd.DataFrame(output).to_csv(OUT / "capacity_control.csv", index=False)


if __name__ == "__main__":
    run()
