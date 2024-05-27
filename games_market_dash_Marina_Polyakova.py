import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px


df_games = pd.read_csv('games.csv')
df_games['User_Score'] = pd.to_numeric(df_games['User_Score'], errors='coerce')
df_games['Critic_Score'] = pd.to_numeric(df_games['Critic_Score'], errors='coerce')
df_games['Critic_Score'] = df_games['Critic_Score'].apply(lambda x: x / 10 if x > 10 else x)
df_games = df_games[(df_games['Year_of_Release'] >= 2000) & (df_games['Year_of_Release'] <= 2022)]
df_games = df_games.dropna()

rating_map = {'E': 1, 'E10+': 2, 'T': 3, 'M': 4,  'AO': 5, 'RP': 0}
df_games['Numeric_rating'] = df_games['Rating'].map(rating_map)

app = dash.Dash(__name__)


app.layout = html.Div([
    html.H1(children='Игровая индустрия', style={'text-align': 'center'}),
    html.P('Дашборд "Игровая индустрия" разработан для анализа данных в сфере видеоигр.'
           ' Он предоставляет пользователю возможность исследовать различные аспекты игровой индустрии,'
           ' такие как платформы, жанры, оценки пользователей и критиков, а также возрастные рейтинги.'),

    html.Div([
        dcc.Dropdown(
            id='platform_filter',
            options=[{'label': platform, 'value': platform} for platform in df_games['Platform'].unique()],
            multi=True,
            placeholder='Выберите платформу',
            style={'width': '90%'}
        ),
        dcc.Dropdown(
            id='genre_filter',
            options=[{'label': genre, 'value': genre} for genre in df_games['Genre'].unique()],
            multi=True,
            placeholder='Выберите жанр',
            style={'width': '90%'}
        ),
        html.Div(
            dcc.RangeSlider(
                id='year_filter',
                min=2000,
                max=2022,
                step=1,
                marks={year: str(year) for year in range(2000, 2023)},
                value=[2000, 2022]
            ),
            style={'width': '220%','fontWeight': 'bold'}
        )
    ], style={'display': 'flex', 'justify-content': 'space-between', 'align-items': 'center', 'margin-bottom': '20px'}),


    html.Div([
        html.Div([
            html.P('Количество игр:', style={'fontSize': 16, 'margin': '0'}),
            html.Div(id='total_games', style={'fontSize': 32, 'fontWeight': 'bold', 'margin': '0'})
        ], style={'border': '1px solid black', 'padding': '10px', 'margin': '5px','text-align': 'center'}),

        html.Div([
            html.P('Средняя оценка игроков:', style={'fontSize': 16, 'margin': '0'}),
            html.Div(id='average_user_score', style={'fontSize': 32, 'fontWeight': 'bold', 'margin': '0'})
        ], style={'border': '1px solid black', 'padding': '10px', 'margin': '5px','text-align': 'center'}),

        html.Div([
            html.P('Средняя оценка критиков:', style={'fontSize': 16, 'margin': '0'}),
            html.Div(id='average_critic_score', style={'fontSize': 32, 'fontWeight': 'bold', 'margin': '0'})
        ], style={'border': '1px solid black', 'padding': '10px', 'margin': '5px'}),
    ], style={'display': 'grid', 'grid-template-columns': '1fr 1fr 1fr', 'margin-bottom': '20px','text-align': 'center'}),

    html.Div([
        dcc.Graph(id='games_by_year_and_platform', style={'flex': '1', 'margin': '10px'}),
        dcc.Graph(id='user_vs_critic_score', style={'flex': '1', 'margin': '10px'}),
        dcc.Graph(id='average_rating_by_genre', style={'flex': '1', 'margin': '10px'})
    ], style={'display': 'flex', 'justify-content': 'space-around'})

])
@app.callback(
    [
        Output('total_games', 'children'),
        Output('average_user_score', 'children'),
        Output('average_critic_score', 'children'),
        Output('games_by_year_and_platform', 'figure'),
        Output('user_vs_critic_score', 'figure'),
        Output('average_rating_by_genre', 'figure')
    ],
    [
        Input('platform_filter', 'value'),
        Input('genre_filter', 'value'),
        Input('year_filter', 'value')
    ]
)

def update_dashboard(selected_platform, selected_genre, selected_year):

    filtered_df = df_games.copy()

    if selected_platform:
        filtered_df = filtered_df[filtered_df['Platform'].isin(selected_platform)]

    if selected_genre:
        filtered_df = filtered_df[filtered_df['Genre'].isin(selected_genre)]

    if selected_year:
        filtered_df = filtered_df[
            (filtered_df['Year_of_Release'] >= selected_year[0]) & (filtered_df['Year_of_Release'] <= selected_year[1])]

    total_games = filtered_df.shape[0]
    average_user_score = round(filtered_df['User_Score'].mean(), 1)
    average_critic_score = round(filtered_df['Critic_Score'].mean(), 1)

    games_by_year_and_platform = px.area(
        filtered_df,
        x='Year_of_Release',
        y='Name',
        color='Platform',
        title='Выпуск игр по годам и платформам',
        labels={'Name': 'Количество игр'}
    )

    user_vs_critic_score = px.scatter(
        filtered_df,
        x='User_Score',
        y='Critic_Score',
        color='Genre',
        title='Оценки игроков vs Оценки критиков',
        labels={'User_Score': 'Оценки игроков', 'Critic_Score': 'Оценки критиков'}
    )

    average_rating_by_genre = filtered_df.groupby('Genre')['Numeric_rating'].mean().reset_index()

    average_rating_by_genre_graph = px.bar(
        average_rating_by_genre,
        x='Genre',
        y='Numeric_rating',
        title='Средний возрастной рейтинг по жанрам',
        labels={'Numeric_rating': 'Средний возрастной рейтинг',
                'Genre': 'Жанр'}
    )

    return total_games, average_user_score, average_critic_score, games_by_year_and_platform, user_vs_critic_score, average_rating_by_genre_graph

if __name__ == '__main__':
    app.run_server(debug=True)

