import pandas as pd
import plotly.express as px

# Beispiel-Daten
data = {
    'x': [1, 2, 3, 1, 2, 3],
    'y': [10, 12, 15, 20, 22, 23],
    'group': ['Linie A', 'Linie A', 'Linie A', 'Linie B', 'Linie B', 'Linie B']
}

df = pd.DataFrame(data)

# Plotly Express Zeichnung
fig = px.line(df, x='x', y='y', color='group', title='Mehrere Linien mit Plotly Express')
fig.show()
