import json
import pandas as pd
import numpy as np

class DatasetProfiler:
    def __init__(self, df):
        self.df = df
        self.profile = {}

    def schema(self):
        return pd.DataFrame({
            "Column": self.df.columns,
            "Data Type": [str(x) for x in self.df.dtypes],
            "Non-Null Count": [int(self.df[c].notna().sum()) for c in self.df.columns]
        })

    def missing_values(self):
        return pd.DataFrame({
            "Column": self.df.columns,
            "Missing Values": self.df.isna().sum().values,
            "Missing Percentage": (self.df.isna().sum().values / len(self.df) * 100).round(2)
        })

    def duplicates(self):
        n = int(self.df.duplicated().sum())
        return {"Total Rows": len(self.df), "Duplicate Rows": n, "Unique Rows": len(self.df)-n}

    def unique_values(self):
        return pd.DataFrame({
            "Column": self.df.columns,
            "Unique Values": [int(self.df[c].nunique(dropna=True)) for c in self.df.columns]
        })

    def numeric_statistics(self):
        d = self.df.select_dtypes(include=[np.number])
        if d.empty: return pd.DataFrame()
        x = d.describe().T.reset_index().rename(columns={"index":"Column"})
        return x.round(3)

    def categorical_summary(self):
        rows=[]
        for c in self.df.select_dtypes(include=["object","category","bool"]).columns:
            vc=self.df[c].value_counts(dropna=True)
            rows.append({"Column":c,"Unique Values":int(self.df[c].nunique(dropna=True)),
                         "Most Frequent":str(vc.index[0]) if not vc.empty else "N/A",
                         "Frequency":int(vc.iloc[0]) if not vc.empty else 0})
        return pd.DataFrame(rows)

    def generate_profile(self):
        self.profile={
            "basic_information":{"Rows":len(self.df),"Columns":len(self.df.columns),"Column Names":list(map(str,self.df.columns))},
            "duplicate_information":self.duplicates(),
            "schema":self.schema().to_dict("records"),
            "missing_values":self.missing_values().to_dict("records"),
            "unique_values":self.unique_values().to_dict("records"),
            "numeric_statistics":self.numeric_statistics().replace({np.nan:None}).to_dict("records"),
            "categorical_summary":self.categorical_summary().to_dict("records")
        }
        return self.profile

    def json_report(self):
        if not self.profile: self.generate_profile()
        return json.dumps(self.profile, indent=4, default=str)
