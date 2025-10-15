"""
电影数据分析系统
基于第6章6.5案例电影数据分析的交互式系统
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from flask import Flask, render_template, request, jsonify, send_file
import io
import base64
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import matplotlib
matplotlib.use('Agg')

app = Flask(__name__)

# 加载电影数据
def load_movie_data():
    try:
        # 尝试从源代码目录加载数据
        movies = pd.read_csv("《Python数据分析与应用：从数据获取到可视化（第2版）》/源代码/IMDB-Movie-Data.csv")
    except:
        try:
            # 尝试从当前目录加载数据
            movies = pd.read_csv("IMDB-Movie-Data.csv")
        except:
            # 如果数据文件不存在，创建一个示例数据
            print("警告：未找到IMDB-Movie-Data.csv文件，使用示例数据")
            movies = pd.DataFrame({
                'Rank': [1, 2, 3, 4, 5],
                'Title': ['Guardians of the Galaxy', 'Prometheus', 'Split', 'Sing', 'Suicide Squad'],
                'Genre': ['Action,Adventure,Sci-Fi', 'Adventure,Mystery,Sci-Fi', 'Horror,Thriller', 
                         'Animation,Comedy,Family', 'Action,Adventure,Fantasy'],
                'Director': ['James Gunn', 'Ridley Scott', 'M. Night Shyamalan', 
                           'Christophe Lourdelet', 'David Ayer'],
                'Year': [2014, 2012, 2016, 2016, 2016],
                'Runtime (Minutes)': [121, 124, 117, 108, 123],
                'Rating': [8.1, 7.0, 7.3, 7.2, 6.2],
                'Votes': [757074, 485820, 157606, 60545, 393727],
                'Revenue (Millions)': [333.13, 126.46, 138.12, 270.32, 325.02],
                'Metascore': [76.0, 65.0, 62.0, 59.0, 40.0]
            })
    return movies

# 获取基本统计信息
def get_basic_stats(movies):
    stats = {
        'total_movies': len(movies),
        'avg_rating': round(movies['Rating'].mean(), 1),
        'total_directors': len(movies['Director'].unique()),
        'avg_runtime': round(movies['Runtime (Minutes)'].mean(), 1),
        'total_votes': movies['Votes'].sum(),
        'avg_revenue': round(movies['Revenue (Millions)'].mean(), 1) if 'Revenue (Millions)' in movies.columns else 0
    }
    return stats

# 获取电影类型统计
def get_genre_stats(movies):
    # 获取所有的电影类型
    temp_list = [i.split(",") for i in movies["Genre"]]
    genre_list = np.unique([i for j in temp_list for i in j])
    
    # 创建类型统计
    genre_counts = {}
    for genre in genre_list:
        count = sum([1 for genres in temp_list if genre in genres])
        genre_counts[genre] = count
    
    return genre_counts

# 生成评分分布图
def create_rating_distribution(movies):
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(movies['Rating'], bins=20, alpha=0.7, color='skyblue', edgecolor='black')
    ax.set_xlabel('评分')
    ax.set_ylabel('电影数量')
    ax.set_title('电影评分分布')
    ax.grid(True, alpha=0.3)
    
    # 转换为base64图像
    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    
    return plot_url

# 生成片长分布图
def create_runtime_distribution(movies):
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(movies['Runtime (Minutes)'], bins=20, alpha=0.7, color='lightgreen', edgecolor='black')
    ax.set_xlabel('片长（分钟）')
    ax.set_ylabel('电影数量')
    ax.set_title('电影片长分布')
    ax.grid(True, alpha=0.3)
    
    # 转换为base64图像
    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    
    return plot_url

# 生成类型统计图
def create_genre_distribution(genre_stats):
    fig, ax = plt.subplots(figsize=(12, 8))
    genres = list(genre_stats.keys())
    counts = list(genre_stats.values())
    
    # 按数量排序
    sorted_indices = np.argsort(counts)[::-1]
    genres = [genres[i] for i in sorted_indices]
    counts = [counts[i] for i in sorted_indices]
    
    bars = ax.bar(genres, counts, color=plt.cm.Set3(np.linspace(0, 1, len(genres))))
    ax.set_xlabel('电影类型')
    ax.set_ylabel('电影数量')
    ax.set_title('电影类型统计')
    plt.xticks(rotation=45, ha='right')
    ax.grid(True, alpha=0.3)
    
    # 添加数值标签
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}', ha='center', va='bottom')
    
    # 转换为base64图像
    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    
    return plot_url

# 生成评分与片长关系图
def create_rating_runtime_scatter(movies):
    fig, ax = plt.subplots(figsize=(10, 6))
    scatter = ax.scatter(movies['Runtime (Minutes)'], movies['Rating'], 
                        alpha=0.6, c=movies['Rating'], cmap='viridis')
    ax.set_xlabel('片长（分钟）')
    ax.set_ylabel('评分')
    ax.set_title('评分与片长关系')
    ax.grid(True, alpha=0.3)
    plt.colorbar(scatter, label='评分')
    
    # 转换为base64图像
    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    
    return plot_url

# 生成年度评分趋势图
def create_year_rating_trend(movies):
    year_rating = movies.groupby('Year')['Rating'].mean()
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(year_rating.index, year_rating.values, marker='o', linewidth=2, markersize=6)
    ax.set_xlabel('年份')
    ax.set_ylabel('平均评分')
    ax.set_title('年度平均评分趋势')
    ax.grid(True, alpha=0.3)
    
    # 转换为base64图像
    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    
    return plot_url

@app.route('/')
def index():
    movies = load_movie_data()
    stats = get_basic_stats(movies)
    genre_stats = get_genre_stats(movies)
    
    # 生成所有图表
    rating_plot = create_rating_distribution(movies)
    runtime_plot = create_runtime_distribution(movies)
    genre_plot = create_genre_distribution(genre_stats)
    scatter_plot = create_rating_runtime_scatter(movies)
    trend_plot = create_year_rating_trend(movies)
    
    # 获取前10部高评分电影
    top_movies = movies.nlargest(10, 'Rating')[['Title', 'Rating', 'Director', 'Year']]
    
    return render_template('index.html', 
                         stats=stats, 
                         genre_stats=genre_stats,
                         rating_plot=rating_plot,
                         runtime_plot=runtime_plot,
                         genre_plot=genre_plot,
                         scatter_plot=scatter_plot,
                         trend_plot=trend_plot,
                         top_movies=top_movies.to_dict('records'))

@app.route('/search')
def search():
    query = request.args.get('q', '')
    movies = load_movie_data()
    
    if query:
        # 搜索电影标题、导演、类型
        filtered_movies = movies[
            movies['Title'].str.contains(query, case=False, na=False) |
            movies['Director'].str.contains(query, case=False, na=False) |
            movies['Genre'].str.contains(query, case=False, na=False)
        ]
    else:
        filtered_movies = movies.head(20)  # 默认显示前20部电影
    
    return render_template('search.html', 
                         movies=filtered_movies.to_dict('records'), 
                         query=query)

@app.route('/directors')
def directors():
    movies = load_movie_data()
    
    # 导演统计
    director_stats = movies.groupby('Director').agg({
        'Title': 'count',
        'Rating': 'mean',
        'Runtime (Minutes)': 'mean',
        'Revenue (Millions)': 'mean'
    }).round(2).reset_index()
    director_stats = director_stats.rename(columns={
        'Title': '电影数量',
        'Rating': '平均评分',
        'Runtime (Minutes)': '平均片长',
        'Revenue (Millions)': '平均票房_百万'
    })
    
    # 按电影数量排序
    director_stats = director_stats.sort_values('电影数量', ascending=False)
    
    return render_template('directors.html', 
                         directors=director_stats.to_dict('records'))

@app.route('/genres')
def genres():
    movies = load_movie_data()
    genre_stats = get_genre_stats(movies)
    
    # 计算每个类型的平均评分
    genre_ratings = {}
    for genre in genre_stats.keys():
        genre_movies = movies[movies['Genre'].str.contains(genre, na=False)]
        if len(genre_movies) > 0:
            genre_ratings[genre] = round(genre_movies['Rating'].mean(), 2)
    
    return render_template('genres.html', 
                         genre_stats=genre_stats,
                         genre_ratings=genre_ratings)

@app.route('/api/stats')
def api_stats():
    movies = load_movie_data()
    stats = get_basic_stats(movies)
    return jsonify(stats)

@app.route('/api/movies')
def api_movies():
    movies = load_movie_data()
    return jsonify(movies.to_dict('records'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)