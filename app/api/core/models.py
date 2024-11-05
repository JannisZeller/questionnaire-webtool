from flask import current_app

import numpy as np
import pandas as pd
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TextClassificationPipeline,
)

from typing import Literal

from ...config import load_env_json

# import torch
# print(torch.cuda.is_available())

# from ...core.utils import hprint


class Scorer:
    def __init__(self) -> None:
        self.tokenizer = AutoTokenizer.from_pretrained("./models/scorer/tokenizer")

        lang_model = AutoModelForSequenceClassification.from_pretrained("./models/scorer/model")
        lang_model = lang_model.to("cpu")
        lang_model = lang_model.eval()
        self.lang_model = lang_model

        print(f"Scorer initiated (device={self.lang_model.device}).")

    def __del__(self) -> None:
        print("Scorer deleted.")

    def predict(
        self,
        texts: list[str]
    ) -> np.ndarray:
        model = self.lang_model.eval()
        tokenizer = self.tokenizer

        pipe = TextClassificationPipeline(model=model, tokenizer=tokenizer)
        # y_pred = np.array([])

        preds = pipe(texts)
        df_preds = pd.DataFrame(preds)
        y_pred = (df_preds["label"]
            .str.removeprefix("LABEL_")
            .astype(int)
            .values
        )
        # y_pred = np.hstack([y_pred, y_pred_batch])

        return y_pred


class Clusterer:
    def __init__(self) -> None:
        self.dimensions = pd.read_csv("./models/clusterer/dimensions.csv")
        self.scaler = pd.read_csv("./models/clusterer/scaler.csv")
        self.centroids = pd.read_csv("./models/clusterer/centroids.csv")
        sclr_cols = self.scaler.drop(columns="minmax").columns.to_list()
        cntr_cols = self.centroids.drop(columns="cluster").columns.to_list()
        assert sclr_cols == cntr_cols
        print("Clusterer initiated.")

    def __del__(self) -> None:
        print("Clusterer deleted.")

    def predict(self, scores: np.ndarray) -> int:
        if scores.ndim == 1:
            scores = np.expand_dims(scores, 0)
        x = self.__apply_dimensions(scores)
        x = self.__apply_scaler(x)
        y = self.__apply_centroids(x)
        return y

    def __apply_dimensions(self, scores: np.ndarray) -> np.ndarray:
        return scores @ self.dimensions.values

    def __apply_scaler(self, dimscores: np.ndarray) -> np.ndarray:
        sclr = self.scaler
        mins = sclr[sclr["minmax"]=="min"].drop(columns="minmax").values
        maxs = sclr[sclr["minmax"]=="max"].drop(columns="minmax").values
        return (dimscores - mins) / (maxs - mins)

    def __apply_centroids(self, sclscores: np.ndarray) -> np.ndarray:
        centers = self.centroids.drop(columns="cluster").values
        cluster_names = self.centroids["cluster"].values
        x = np.repeat(sclscores, 4, axis=0)
        x = (x - centers)**2
        x = np.mean(x, axis=-1)
        y = np.argmin(x, axis=-1).astype(np.int32)

        return cluster_names[y]


class Regressor:
    def __init__(self, mode: Literal["regression", "summation"]) -> None:
        if mode == "summation":
            self.df_coefs = pd.read_csv("./models/summator.csv")
        if mode == "regression":
            self.df_coefs = pd.read_csv("./models/regressor.csv")
        self.mode = mode
        print(f"Regressor initiated (mode={mode}).")

    def __del__(self) -> None:
        print("Regressor deleted.")

    def dimscores(self, scores: np.ndarray) -> pd.DataFrame:
        if scores.ndim == 1:
            scores = np.expand_dims(scores, 0)

        n_samples = scores.shape[0]
        scores = np.concatenate(
            [scores, np.ones((n_samples, 1))],
            axis=1,
            dtype=float,
        )

        x = self.__apply_dimensions(scores)
        df = pd.DataFrame(x)
        df.columns = self.df_coefs.columns
        return df

    def __apply_dimensions(self, scores: np.ndarray) -> np.ndarray:
        return scores @ self.df_coefs.values.astype(float)



# cnfg = load_env_json("./env/config.jsonc")

# if cnfg["PRELOAD_MODELS"]:
#     scorer = Scorer()
#     regressor = Regressor(cnfg["DIMSCORES_MODE"])
#     clusterer = Clusterer()

def get_model_instances() -> (tuple[Scorer, Regressor, Clusterer] | tuple[None, None, None]):
    cnfg = load_env_json("./env/config.jsonc")
    if cnfg.get("PRELOAD_MODELS", False):
        regressor_mode = cnfg.get("DIMSCORES_MODE", "regression")
        scorer = Scorer()
        regressor = Regressor(regressor_mode)
        clusterer = Clusterer()
        return scorer, regressor, clusterer
    else:
        return None, None, None
