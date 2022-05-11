import numpy as np
import pandas as pd

class Functions:

    @staticmethod
    def kelvin(temperature):
        return round(temperature + 273.15, 8)

    @staticmethod
    def celsius(temperature):
        return round(temperature - 273.15, 8)

    @staticmethod
    def interpolate(p1, p2, x):
        return p1[1] + (x-p1[0])*(p2[1]-p1[1])/(p2[0]-p1[0])

    @staticmethod
    def getValues(table, variable, value):
        if value in table[variable].values:
            return table.loc[table[variable] == value] 
        else:
            previousIndex = table[table[variable] < value].index[-1]
            out = []
            for col in table.columns:
                if col != variable:
                    p1 = [table[table.index == previousIndex][variable].values[0],
                          table[table.index == previousIndex][col].values[0]]
                    p2 = [table[table.index == previousIndex + 1][variable].values[0],
                          table[table.index == previousIndex + 1][col].values[0]]
                    out.append(Functions.interpolate(p1, p2, value))
                else:
                    out.append(value)
            return pd.DataFrame(np.array([out]), columns=table.columns)