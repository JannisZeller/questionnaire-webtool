import numpy as np
import pandas as pd

import re



# PCK Data
# ------------------------------------------------------------------------------
mc_item_rubics = {
    'A5a.': 1,
    'A5b.': 0,
    'A5c.': 0,
    'A5d.': 1,
    'A5e.': 0,
    'A5f.': 1,
    'A7a.': 1,
    'A7b.': 0,
    'A7c.': 1,
    'A7d.': 0,
    'A8a.': 0,
    'A8b.': 1,
    'A8c.': 1,
    'A8d.': 0,
    'A8e.': 1,
    'A19a.': 1,
    'A19b.': 0,
    'A19c.': 0,
    'A19d.': 0,
    'A19e.': 1,
}
mc_items  = list(mc_item_rubics.keys())

max_scores_mc = {
    'A5.'  : 6,
    'A7.'  : 4,
    'A8.'  : 5,
    'A19.' : 5,
}
mc_tasks = list(max_scores_mc.keys())

max_scores = {
    'A1a.' : 1,
    'A1b.' : 2,
    'A2.'  : 2,
    'A3.'  : 2,
    'A4.'  : 2,
    'A5.'  : 2,
    'A6.'  : 2,
    'A7.'  : 2,
    'A8.'  : 2,
    'A9.'  : 2,
    'A10.' : 2,
    'A11.' : 1,
    'A12.' : 1,
    'A13.' : 1,
    'A14a.': 1,
    'A14b.': 1,
    'A15.' : 1,
    'A16.' : 1,
    'A17.' : 2,
    'A18.' : 2,
    'A19.' : 2,
    'A20.' : 1,
    'A21a.': 1,
    'A21b.': 1,
    'A22.' : 1,
    'A23.' : 3,
    'A24.' : 2
}
tasks = list(max_scores.keys())

text_items = [
    'A1a.',
    'A1b.1',
    'A1b.2',
    'A2.1',
    'A2.2',
    'A3.1',
    'A3.2',
    'A4.1',
    'A4.2',
    'A6.',
    'A9.1',
    'A9.2',
    'A10.',
    'A11.',
    'A12.',
    'A13.',
    'A14a.',
    'A14b.',
    'A15.',
    'A16.1',
    'A16.2',
    'A17.',
    'A18b.',
    'A20.',
    'A21a.',
    'A21b.',
    'A22.',
    'A23.1',
    'A23.2',
    'A23.3',
    'A24.1',
    'A24.2'
]
text_tasks = list(np.setdiff1d(tasks, mc_tasks))

max_scores_dims = {
    "Gesamtscore":              43,
    "Reproduzieren":            23,
    "Anwenden":                 8,
    "Kreieren":                 9,
    "Analysieren":              13,
    "Evaluieren":               5,
    "Instruktionsstrategien":   10,
    "Schülervorstellungen":     12,
    "Experimente":              7,
    "Fachdidaktische Konzepte": 14,
}
uncert_dims = {
    "Analysieren":	            1.00,
    "Anwenden":	                1.26,
    "Evaluieren":	            0.51,
    "Experimente":	            1.04,
    "Fachdidaktische Konzepte": 1.12,
    "Gesamtscore":              2.40,
    "Instruktionsstrategien":   1.09,
    "Kreieren":                 1.20,
    "Reproduzieren":            1.64,
    "Schülervorstellungen":     1.27,
}


# General Table Tools
# ------------------------------------------------------------------------------

def item_dots(df: pd.DataFrame, col: str=None) -> pd.DataFrame:
    """Unifies the item-columns names to the "A1a. / A1b.1 / A5a." format.

    Parameters
    ----------
    df : pd.DataFrame
        A DataFrame with either the item-ids as colnames or one column
        containing the item-ids.
    col : str=None
        Optional. The column containing the item names.
    """

    if col is None:
        names = df.columns.to_list()
    else:
        names = df[col].to_list()

    new_names = []
    for n in names:
        if "_" in n:
            n = re.sub("_", ".", n)
        else:
            n = f"{n}."
        new_names.append(n)

    if col is None:
        df.columns = new_names
    else:
        df[col] = new_names

    return df


def reorder_column(df: pd.DataFrame, column: str, before: str) -> pd.DataFrame:
    """Wrapper to reorder a specific column in of a pandas dataset.

    Parameters
    ----------
    df : pd.DataFrame
        The dataframe containing the columns to reorder.
    column : str
        The column to reorder.
    before : str
        The column, that the other column should be inserted before.

    Returns
    -------
    pd.DataFrame
        The dataframe with reordered columns.
    """
    columns = df.columns.to_list()
    columns.remove(column)
    idx = columns.index(before)
    columns.insert(idx, column)
    df = df[columns]
    return df


def merge_columns(
    df: pd.DataFrame,
    columns: list[str],
    new_colname: str = None,
) -> pd.DataFrame:
    """Wrapper to sum columns together (primary for MC-columns). The crux is
    that in case all of the columns entries are `np.nan` the resulting
    merged column keeps this `np.nan`.

    Parameters
    ----------
    df : pd.DataFrame
        The dataframe containing the columns to sum.
    columns : list[str]
        Columns to sum together.
    new_colname : str = None
        New columns name.

    Returns
    -------
    pd.DataFrame
        The dataframe with reordered columns.
    """
    # Copy to prevent inplace operations on parameter
    df = df.copy()

    if new_colname is None:
        new_colname = "".join(columns)
    # print(f"Merging {columns} to '{new_colname}'.")

    # Extracting rows where all columns are NaN
    all_na = (df.loc[:, columns].isna().mean(axis=1).to_numpy()) == 1.0
    df[new_colname] = df.loc[:, columns].sum(axis=1, skipna=True)

    df = reorder_column(df, new_colname, columns[0])
    df = df.drop(columns=columns)

    # Replace rows where all columns were NaN
    df.loc[all_na, new_colname] = np.nan
    return df


def merge_and_clip(
    df: pd.DataFrame,
    columns: list[str],
    new_colname: str = None,
    a_min: float = 0,
    a_max: float = 1,
) -> pd.DataFrame:
    """Wrapper to sum columns together (primary for MC-columns). The crux is
    that in case all of the columns entries are `np.nan` the resulting
    merged column keeps this `np.nan`.

    Parameters
    ----------
    df : pd.DataFrame
        The dataframe containing the columns to sum.
    columns : list[str]
        Columns to sum together.
    new_colname : str = None
        New columns name. If `None` the old column names get joined.
    a_min : float = 0
        The min value for the clip.
    a_max : float = 1
        The max value for the clip

    Returns
    -------
    pd.DataFrame
        The dataframe with merged and clipped columns.
    """
    if new_colname is None:
        new_colname = "".join(columns)
    try:
        df = merge_columns(df, columns, new_colname)
        df[new_colname] = np.clip(df[new_colname].values, a_min=a_min, a_max=a_max)
    except KeyError:
        print(f"Warning: not all of {columns} are available in dataframe.")
    return df


def merge_columns_starting_with(
    df: pd.DataFrame,
    prefix: str,
) -> pd.DataFrame:
    """Wrapper to sum columns together (primary for MC-columns) that start
    with a common string.

    Parameters
    ----------
    df : pd.DataFrame
        The dataframe containing the columns to sum.
    prefix : str
        The prefix of the columns to sum over. The new column name will be
        `f"{prefix}."`.

    Returns
    -------
    pd.DataFrame
        The dataframe with summed columns.
    """
    df = df.copy()
    if prefix.endswith("."):
        prefix = re.sub("\\.", "", prefix)
    new_col = prefix + "."

    cols_to_sum = [col for col in df.columns.to_list() if col.startswith(prefix)]

    df = merge_columns(df, cols_to_sum, new_col)

    return df



# Zero Score Placeholders
# ------------------------------------------------------------------------------

def df_mc_zero() -> pd.DataFrame:
    """Retrieves a dataframe with only zero-mc scores. Used if no MC-responses
    are available for a user.

    Returns
    -------
    pd.DataFrame
        DataFrame in the correct format (MC after scoring) containing only 0
        scores.
    """
    cols = mc_tasks + ["ID"]
    zeros = np.zeros((1, len(cols)))
    df = pd.DataFrame(zeros, columns=cols)
    df["ID"] = "id"
    return df


def df_text_zero() -> pd.DataFrame:
    """Retrieves a dataframe with only zero-text scores. Used if no text
    -responses are available for a user.

    Returns
    -------
    pd.DataFrame
        DataFrame in the correct format (text after scoring) containing only 0
        scores.
    """
    cols = text_tasks + ["ID"]
    zeros = np.zeros((1, len(cols)))
    df = pd.DataFrame(zeros, columns=cols)
    df["ID"] = "id"
    return df




# Multiple Choice Scoring
# ------------------------------------------------------------------------------

def pivot_mc_item_df(df_mc: pd.DataFrame) -> pd.DataFrame:
    """Pivots MC-items DataFrame to wide format. Automatically fills missings
    with 99.

    Parameters
    ----------
    df_mc : pd.DataFrame
        Dataframe containing the single item responses (True vs. False) as rows
        in the "item_id"-column.

    Returns
    -------
    pd.DataFrame
        DataFrame containing the responses as a single row with the columns
        being item-names.
    """

    df_mc = df_mc.set_index("item").T
    missing_items = np.setdiff1d(mc_items, df_mc.columns.to_list())
    if len(missing_items) > 0:
        df_mc[missing_items] = 99
    df_mc = df_mc[mc_items]
    return df_mc


def score_mc_items(
    df: pd.DataFrame,
    mc_item_rubics: dict[str, bool]=mc_item_rubics
) -> pd.DataFrame:
    """Scores the multiple choice items

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe containing the single item responses (True vs. False).
    mc_item_rubics : dict[str, bool]=mc_item_rubics
        Dict containing the actual correct True/False values of the single
        items.

    Returns
    -------
    pd.DataFrame
        DataFrame containing the scores (1 / 0) for the single multiple choice
        items. Score == 1 if the response matches the rubics, else 0.
    """
    # df_ret = pd.DataFrame()
    # cols = df.columns.to_list()
    for item, ans in mc_item_rubics.items():
        val = df[item].values
        if val != 99:
            df[item] = (df[item] == ans).astype(int)
        else:
            df[item] = 0
    return df


def construct_kprim_thresholds(max: dict[str, int]) -> dict[str, list]:
    """ Wrapper to define kprim-thresholds for grading of multiple choice
    questions with given number of choices.

    Parameters
    ----------
    max : dict
        Dictionary with item names as keys and maximum scores as values.

    Returns
    -------
    thresholds : dict
        Dictionary with item names as keys and kprim thresholds as list-values.
    """
    thresholds = {}
    for item, max_pts in max.items():
        if max_pts==3:
            thresholds[item] = [2, 3]
        if max_pts==4:
            thresholds[item] = [3, 4]
        if max_pts==5:
            thresholds[item] = [3, 4]
        if max_pts==6:
            thresholds[item] = [4, 5]
        if max_pts==7:
            thresholds[item] = [4, 6]
        if max_pts==9:
            thresholds[item] = [5, 8]
        if max_pts==12:
            thresholds[item] = [7, 10]
    return thresholds


def apply_kprim_thresholds(
    df: pd.DataFrame,
    thresholds_dict: dict[str, list[float]]
) -> pd.DataFrame:
    """Function to apply kprim-thresholds to a dataframe. All keys of the
    `thresholds_dict` must match a column name of `df`.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame to apply the thresholds.
    thresholds_dict : dict[str, list[float]]
        Threshold dictionary containing item names and threshold lists

    Returns
    -------
    pd.DataFrame
        Dataframe with applied thresholds at the columns specified in the
        thresholds_dict.
    """
    df_ret = df.copy() # Copying df because updates are later performed inplace!
    for item, thresholds in thresholds_dict.items():
        thresholds = [-np.inf] + thresholds + [np.inf]
        for k in range(len(thresholds)-1):
            row_idx = (df[item] >= thresholds[k]) & (df[item] < thresholds[k+1])
            df_ret.loc[row_idx, item] = k
    return df_ret


def score_mc_tasks(df: pd.DataFrame, mc_tasks: list[str]=mc_tasks) -> pd.DataFrame:
    """ Function to score multiple-choice (mc) items. `df` must contain the
    suitable expected columns of the mc items specified in
    `src.data.aux_data.load_pck_auch_data()`. The kprim thresholds get
    inferred automatically based on the number of columns per mc item.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with MC items to score.
    mc_items : list[str]
        List of the MC item names to score. The columns names of the columns
        which get scored have to start with one of the MC item names

    Returns
    -------
    pd.DataFrame
        DataFrame with MC items scored accoring to the Kprim-rubrics.
    """
    # print("\nKprim MC-Scoring.")

    for col in mc_tasks:
        df = merge_columns_starting_with(df, col)

    max_points_only_mc = {
        key:value for (key, value) in max_scores_mc.items() if key in mc_tasks
    }

    mc_thresholds = construct_kprim_thresholds(max_points_only_mc)

    df = apply_kprim_thresholds(df, mc_thresholds)

    return df



# Text Cleaning
# ------------------------------------------------------------------------------

def get_abbreviation_replacement_tuples() -> list[tuple[str, str]]:
    """A list of regex abbreviations. For end of words (word boundaries) after
    priods (.) see: https://stackoverflow.com/a/18005390.

    Returns
    -------
    list[tuple[str, str]]
        List of tuples where the first entry of each tuple is the regex to
        be replaced and the second entry is the replacement.
    """
    # suffix for end of word with or without period
    dot_sfx = r"\.?(?=\s|\:|$)"

    return [
        (r"(?<!\S)<-{1,2}(?!\S)", "<ARROW>"),
        (r"(?<!\S)-{1,2}>(?!\S)", "<ARROW>"),
        (r"(?<!\S)<-{1,2}>(?!\S)", "<ARROW>"),
        (r"\bWW" + dot_sfx, "Wechselwirkung"),
        (r"\bU-Gespräch" + dot_sfx, "Unterrichtsgespräch"),
        (r"\bSt" + dot_sfx, "Stunde"),
        (r"\b[N,n]r" + dot_sfx, "Nummer"),
        (r"\bN I" + dot_sfx, "erstes Newtonsches Gesetz"),
        (r"\bN II" + dot_sfx, "zweites Newtonsches Gesetz"),
        (r"\bN III" + dot_sfx, "drittes Newtonsches Gesetz"),
        (r"\bMittelw" + dot_sfx, "Mittelwert"),
        (r"\bkin" + dot_sfx, "kinetisch"),
        (r"\bi\.?\s?d\.?R\.?" + dot_sfx, "in der Regel"),
        (r"\bgleichf" + dot_sfx, "gleichförmig"),
        (r"\bfachl" + dot_sfx, "fachlich"),
        (r"\bdidakt" + dot_sfx, "didaktisch"),
        (r"\bdopp" + dot_sfx, "doppelt"),
        (r"\ballg(em)?" + dot_sfx, "arithmetisch"),
        (r"\b&\b", "und"),
        (r"\bu" + dot_sfx, "und"),
        (r"\barithm" + dot_sfx, "arithmetisch"),
        (r"\bausbauf" + dot_sfx, "ausbaufähig"),
        (r"\babf" + dot_sfx, "ausbaufähig"),
        (r"\b[Bb]eschl" + dot_sfx, "beschleuni"),
        (r"\b[Bb]eschlng" + dot_sfx, "Beschleunigung"),
        (r"\bbest" + dot_sfx, "bestimmt"),
        (r"\b[Bb]ew" + dot_sfx, "Bewegung"),
        (r"\b[Bb]sp\.?l?" + dot_sfx, "Beispiel"),
        (r"\bbspw" + dot_sfx, "beispielsweise"),
        (r"\bbzgl" + dot_sfx, "bezüglich"),
        (r"\bbzw" + dot_sfx, "beziehungsweise"),
        (r"\b[ck]onst" + dot_sfx, "konstant"),
        (r"\bd\.?\s?h" + dot_sfx, "das heißt"),
        (r"\bDiagr" + dot_sfx, "Diagramm"),
        (r"\bdyn" + dot_sfx, "dynamisch"),
        (r"\beig\.?t?l?" + dot_sfx, "eigentlich"),
        (r"\b[Ee]rg" + dot_sfx, "Ergebnis"),
        (r"\betc(et)?" + dot_sfx, "und so weiter"),
        (r"\bevent" + dot_sfx, "eventuell"),
        (r"\bevt?l" + dot_sfx, "eventuell"),
        (r"\bExp?" + dot_sfx, "Experiment"),
        (r"\bGeschw(ind)?" + dot_sfx, "Geschwindigkeit"),
        (r"\bggb?fs?" + dot_sfx, "gegebenenfalls"),
        (r"\bgrav" + dot_sfx, "Gravitation"),
        (r"\bgrundsätzl" + dot_sfx, "grundsätzlich"),
        (r"\bi\.?\s?G\.?" + dot_sfx, "im Gegensatz"),
        (r"\b[Ii]mp" + dot_sfx, "Impuls"),
        (r"\bk\.?\s?A" + dot_sfx, "keine Ahnung"),
        (r"\bKi" + dot_sfx, "Kind"),
        (r"\bkl" + dot_sfx, "klein"),
        (r"\b[Mm]ö?gl\.?\s?weise" + dot_sfx, "möglicherweise"),
        (r"\bmöglich weise\b", "möglicherweise"),
        (r"\bmö?gl" + dot_sfx, "möglich"),
        (r"\bneg" + dot_sfx, "negativ"),
        (r"\bod?" + dot_sfx, "oder"),
        (r"\bphys?" + dot_sfx, "physikalisch"),
        (r"\bphys(ik)?" + dot_sfx, "physikalisch"),
        (r"\bquadr" + dot_sfx, "quadratisch"),
        (r"\b[SS](ch)?" + dot_sfx, "Schüler"),
        (r"\b[Ss][uo][Ss]" + dot_sfx, "Schüler"),
        (r"selbstständiges A" + dot_sfx, "selbstständiges Arbeiten"),
        (r"\bselbstst" + dot_sfx, "selbstständig"),
        (r"\bUF" + dot_sfx, "Unterrichtsfach"),
        (r"\bung" + dot_sfx, "ungefähr"),
        (r"\bungl" + dot_sfx, "ungleich"),
        (r"\buntersch(iedl)?" + dot_sfx, "unterschiedlich"),
        (r"\bunwahrscheinl" + dot_sfx, "unwahrscheinlich"),
        (r"\bVB" + dot_sfx, "Verbraucher"),
        (r"\bversch" + dot_sfx, "verschieden"),
        (r"\bverw" + dot_sfx, "verwenden"),
        (r"\bvl(l?t)?" + dot_sfx, "vielleicht"),
        (r"\bwissenschaftl" + dot_sfx, "wissenschaftlich"),
        (r"\bz\.?\s?[Bb](spl?|eispiel)?" + dot_sfx, "zum Beispiel"),
        (r"\bzw" + dot_sfx, "zwischen"),
        (r"\b[Kk]omp" + dot_sfx, "Kompetenz"),
        (r"\bkompl" + dot_sfx, "kompliziert"),
        (r"\bL" + dot_sfx, "Lehrer"),
        (r"\bL[Kk]" + dot_sfx, "Lehrkraft"),
        (r"\bL[Pp]" + dot_sfx, "Lehrperson"),
        (r"\blin" + dot_sfx, "linear"),
        (r"\blt" + dot_sfx, "laut"),
        (r"\bmax" + dot_sfx, "maximal"),
        (r"\bn" + dot_sfx, "nicht"),
        (r"\bo\.?\s?[Ää]" + dot_sfx, "oder Ähnliches"),
        (r"\bu\.?\s?[Ää]" + dot_sfx, "und Ähnliches"),
        (r"\bposi?" + dot_sfx, "positiv"),
        (r"\bS\.?\s?A" + dot_sfx, "Schüler A"),
        (r"\bS\.?\s?B" + dot_sfx, "Schüler B"),
        (r"\b[Ss]t" + dot_sfx, "Stunde"),
        (r"\b[Ss]\.?\s?[Vv]" + dot_sfx, "Schülervorstellung"),
        (r"\bSch(üler)?vorst" + dot_sfx, "Schülervorstellung"),
        (r"\bunbel" + dot_sfx, "unbelastbar"),
        (r"\busw" + dot_sfx, "und so weiter"),
        (r"\bim\sV" + dot_sfx, "im Vorfeld"),
        (r"\bv\.?\s?[Aa]" + dot_sfx, "vor allem"),
        (r"\bverb" + dot_sfx, "verbessern"),
        (r"\bvs" + dot_sfx, "versus"),
        (r"\b[Ww]d?[Hh]" + dot_sfx, "Wiederholung"),
        (r"\b[Zz]\.?\s?[Pp]" + dot_sfx, "oder Ähnliches"),
        (r"\b[Zz]\.?\s?[Tt]" + dot_sfx, "oder Ähnliches"),
        (r"\b(ZFK|zfk)" + dot_sfx, "Zentrifugalkraft"),
        (r"\b(ZPK|zpk)" + dot_sfx, "Zentripetalkraft"),
        (r"\b[Zz]sm\.?\s?h(an)?g" + dot_sfx, "Zusammenhang"),
        (r"\bzusammen\.?\s?h(an)?g" + dot_sfx, "Zusammenhang"),
        (r"\bzs?m" + dot_sfx, "zusammen"),
    ]


def replace_abbreviations(s: str) -> str:
    """Replaces typically found abbreviations in text strings.

    Parameters
    ----------
    s : str

    Returns
    -------
    str
    """
    repl_tpls = get_abbreviation_replacement_tuples()
    for abbr, expr in repl_tpls:
        s = re.sub(abbr, expr, s, flags=re.IGNORECASE)
    return s


def cleanup_whitespaces(s: str) -> str:
    """Reduces multiple consecutive whitespaces to a single one

    Parameters
    ----------
    s : str

    Returns
    -------
    str
    """
    s = s.strip()
    s = re.sub(r"\s{2,}", " ", s)
    return s


def remove_empty_aliases(s: str) -> str:
    """Reduces multiple consecutive whitespaces to a single one

    Parameters
    ----------
    s : str

    Returns
    -------
    str
    """
    empty_aliases = ["", "-", "--", "---", "_", "__", "___"]
    if s in empty_aliases:
        s = ""
    return s


whitespace_remover = np.vectorize(cleanup_whitespaces)
abbreviations_replacer = np.vectorize(replace_abbreviations)
empty_aliases_remover = np.vectorize(remove_empty_aliases)



# Text Processing
# ------------------------------------------------------------------------------

def pivot_text_item_df(df_text: pd.DataFrame) -> pd.DataFrame:
    """Pivots text-items DataFrame to wide format. Formats the item colnames and
    automatically fills missings with "" (empty string).

    Parameters
    ----------
    df_text : pd.DataFrame
        Dataframe containing the single item responses (True vs. False) as rows
        in the "item"-column.

    Returns
    -------
    pd.DataFrame
        DataFrame containing the responses as a single row with the columns
        being the properly formatted item-names.
    """

    df_text = df_text.set_index("item").T
    missing_items = np.setdiff1d(text_items, df_text.columns.to_list())
    if len(missing_items) > 0:
        df_text[missing_items] = ""
    df_text = df_text[text_items]
    return df_text


def unite_str_columns(
    df: pd.DataFrame,
    cols: list[str]=None,
    new_name: str="united",
    drop: bool=False,
    sep: str=" "
) -> pd.DataFrame:
    """Wrapper function to unite string type columns to a single column like the
    R-dplyr "unite" function. Replacing NAs with "" beforehand is strongly
    recommended.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with columns to unite.
    cols : list[str]=None
        List with the column names of the columns to unite. If `None` all are
        united.
    new_name : str="united"
        Name of the united column.
    drop : bool=False
        Whether to drop the single columns.
    sep : str=" "
        Separation characters.

    Returns
    -------
    pd.DataFrame
    """
    if cols is None:
        cols = df.columns.to_list()

    df_new = df.copy()
    df_new[new_name] = ""

    for col in cols:
        apdx = df_new[col].astype(str) if col in df_new.columns else ""
        if col != cols[0]:
            apdx = sep + apdx
        df_new[new_name] = df_new[new_name] + apdx

    df_new[new_name] = df_new[new_name].str.strip()

    df_new = reorder_column(df_new, new_name, cols[0])

    if drop:
        df_new = df_new.drop(columns=cols)

    return df_new


def concat_taskwise(df: pd.DataFrame) -> pd.DataFrame:
    """Concats the text-dataframe columns such that each resulting column can
    be matched to a columns in the scores-data.

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe to extract ID-variables from

    Returns
    -------
    pd.DataFrame
        Text dataframes with tasks (codable units) concatted in single columns.
    """

    text_cols = ["A18." if col=="A18b." else col for col in text_items]
    df = df.rename(columns={"A18b.": "A18."})

    for task_name in tasks:
        task_cols = [col for col in text_cols if col.startswith(task_name)]
        if len(task_cols) == 0: # not all items are text-items
            continue
        if len(task_cols) > 1:
            df = unite_str_columns(df, task_cols, task_name, drop=True)

    # id_vars = get_id_vars(df)
    # assert all([col in tasks for col in df.drop(columns=id_vars).columns])
    assert all([col in tasks for col in df.columns])

    return df


def melt_tasks(df: pd.DataFrame) -> pd.DataFrame:
    """Melts a text-dataframe.

    Parameters
    ----------
    df : pd.DataFrame

    Returns
    -------
    pd.DataFrame
    """
    df = df.melt(var_name="item", value_name="text")
    return df


def drop_empty(df: pd.DataFrame) -> pd.DataFrame:
    mask = df["text"] != ""
    df = df.loc[mask, :]
    return df


def _add_item_name(item_name: str, text: str) -> str:
    """Prepends "Aufgabe xy:" to a text, i.e., a text-column entry. Only if
    the text is not empty.
    """
    if "Aufgabe" not in item_name:
        item_name = re.sub("A", "Aufgabe ", item_name)
    return item_name + ": " + text


def add_item_names(
    df_text: pd.DataFrame,
    item_col: str="item",
    text_col: str="text",
) -> pd.DataFrame:
    """Prepends the text column with the item name in the format "Aufgabe xy:".

    Parameters
    ----------
    df_text : pd.DataFrame
    item_col : str="item"
        Column containing the item name.
    text_col : str="text"
        Column containing the response text.

    Returns
    -------
    pd.DataFrame
    """
    df_text = df_text.copy()

    item_names = df_text[item_col]
    item_names = np.array([re.sub("A", "Aufgabe ", i) for i in item_names])

    concatter = np.vectorize(_add_item_name)

    texts = df_text[text_col].values
    texts = concatter(item_names, texts)
    df_text[text_col] = texts

    return df_text



# Text-Scores (Re-)Processing
# ------------------------------------------------------------------------------

def pivot_to_wide(
    df: pd.DataFrame,
    value_cols: str="predicted_scores",
    index_cols: list[str]=["ID"],
    column_names: str="item",
) -> pd.DataFrame:
    """Pivots a DataFrame with responses in rows to wide format with a row
    for each questionnaire edit.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with item-responses in rows.
    index_cols : list[str]=["ID"]
        Columns that should be used as index for pivoting. Defaults to the
        ID-column.
    column_names : str="item":
        Column name of the column whichs entries should be used as the columns
        of the pivoted DataFrame.

    Returns
    -------
    pd.DataFrame
    """
    df = df.pivot(index=index_cols, columns=column_names, values=value_cols)
    try:
        df.columns = df.columns.get_level_values(1)
    except IndexError:
        pass
    df = df.reset_index()
    return df


def combinde_text_mc_cols(
    df_tscores: pd.DataFrame,
    df_mcscores: pd.DataFrame,
    merge_on: str="ID",
    fillna: float=0,
) -> pd.DataFrame:
    """Appends additional score-columns to DataFrame `df`. Used for the multiple
    choice (mc) columns. Keeps only the id-, and scores columns in the result.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame to which the columns should be appended
    df_scores : pd.DataFrame
        Dataframe containing the additional columns.
    merge_on : str="ID"
        Column for the merge
    mc_cols : list[str]=load_pck_aux_data()["mc_items"]
        Names of the multiple choice columns
    task_prefixes : list[str]=load_pck_aux_data()["item_names"]
        Names of all item columns. Used for reshaping.

    Returns
    -------
    pd.DataFrame
    """
    missing_text_cols = np.setdiff1d(tasks, df_tscores.columns.to_list() + mc_tasks)
    df_tscores[missing_text_cols] = fillna

    df_tscores = pd.merge(
        left=df_tscores,
        right=df_mcscores[[merge_on] + mc_tasks],
        on=merge_on,
        validate="1:1",
    )
    assert len(np.setdiff1d(tasks, df_tscores.drop(columns=merge_on).columns.to_list())) == 0, (
        "Not all task-columns are present in the merged dataframe."
    )

    df_tscores = df_tscores[[merge_on] + tasks]
    return df_tscores


def append_dimscore_infos(
    df: pd.DataFrame,
    max_scores_dims: dict[str, int]=max_scores_dims,
) -> pd.DataFrame:
    """Appends an additional row containing the scores relative to the maximum
    possible scores in the dimensions

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame to which the columns should be appended
    max_scores_dims : dict[str, int]
        Max possible scores in the dimensions.

    Returns
    -------
    pd.DataFrame
    """
    df.index = ["sum"]

    df_max = pd.DataFrame(max_scores_dims, index=["max"])
    df_max = df_max[df.columns.to_list()]

    df_uncert = pd.DataFrame(uncert_dims, index=["uncertainty"])
    df_uncert = df_uncert[df.columns.to_list()]

    df_uncert_normed = df_uncert.reset_index(drop=True) / df_max.reset_index(drop=True)
    df_uncert_normed.index = ["uncertainty_normed"]

    df_normed = df.reset_index(drop=True) / df_max.reset_index(drop=True)
    df_normed.index = ["normed"]

    df_ret = pd.concat([
        df_max, df_uncert, df_uncert_normed, df, df_normed,
    ])

    return df_ret
