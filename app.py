from flask import Flask, render_template, request
import numpy as np
import matplotlib.pyplot as plt
import io
import base64
import matplotlib
from flask_talisman import Talisman

# Matplotlib'in etkileşimli olmayan arka plan modunu kullan
matplotlib.use('Agg')

app = Flask(__name__)
# Flask-Talisman'ı ekleyerek güvenlik başlıklarını ve HTTPS'yi zorunlu hale getirin
talisman = Talisman(app, content_security_policy=None, force_https=True, strict_transport_security=True, strict_transport_security_max_age=31536000)

def convert_to_int(value):
    try:
        return int(value.replace('.', ''))
    except ValueError:
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    predicted_rank_2024 = None
    error_message = None
    graph_url = None
    if request.method == 'POST':
        try:
            rank_2023 = convert_to_int(request.form['rank_2023'])
            rank_2022 = convert_to_int(request.form['rank_2022'])
            rank_2021 = convert_to_int(request.form['rank_2021'])
            
            if None in (rank_2023, rank_2022, rank_2021):
                raise ValueError("Geçersiz giriş")

            max_value = 1500000
            if rank_2023 > max_value or rank_2022 > max_value or rank_2021 > max_value:
                raise ValueError(f"Sıralama değeri {max_value} değerinden büyük olamaz")
            
            # Ortalama değişim yüzdesini hesapla
            change_2022_to_2023 = ((rank_2023 - rank_2022) / rank_2022) * 100
            change_2021_to_2022 = ((rank_2022 - rank_2021) / rank_2021) * 100
            
            average_change = (change_2022_to_2023 + change_2021_to_2022) / 2
            
            # 2024 tahmini
            predicted_rank_2024 = int(rank_2023 * (1 + (average_change / 100)))

            # Grafik oluşturma
            years = np.array([2021, 2022, 2023, 2024])
            ranks = np.array([rank_2021, rank_2022, rank_2023, predicted_rank_2024])
            graph_url = create_graph(years, ranks)
        
        except ValueError as e:
            error_message = str(e)
    
    return render_template('index.html', predicted_rank_2024=predicted_rank_2024, error_message=error_message, graph_url=graph_url)

def create_graph(years, ranks):
    plt.figure()
    plt.plot(years, ranks, marker='o', linestyle='-', color='b')
    plt.xlabel('Yıl')
    plt.ylabel('Sıralama')
    plt.title('Yıllara Göre Sıralama Tahmini')
    plt.grid(True)
    
    # Yılların tam sayılar olarak görünmesi için x eksenini ayarla
    plt.xticks(years)
    plt.yticks(ranks)

    # Grafik verilerini bellek tamponuna kaydetme
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    graph_url = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()
    plt.close()
    return f"data:image/png;base64,{graph_url}"

if __name__ == '__main__':
    app.run(ssl_context=('cert.pem', 'key.pem'), debug=True)
