# %% 
import lasio
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
# %% ──────────────────── Загрузка и очистка ────────────────────────────────────
def analyze_well(well):
    las = lasio.read(well)
    df = las.df()
    df = df.replace(-999.25, np.nan)
    print("Количество пустых строк:")
    print(df.isnull().sum())
    
#───────────────────────── Заполнение пустых строк ───────────────────────── 
    clean = df.ffill().bfill()
    print("\nКоличество пустых строк после заполнения:")
    print (clean.isnull().sum())
    print(clean.describe())
    
#───────────────────────── Проверка на выбросы ───────────────────────── 
    for col in ['GAMMA', 'RESISTIVITY', 'POROSITY']:
        mean = clean[col].mean()
        std = clean[col].std()
        
        outliers = clean [
            (clean[col] > mean + 3*std) |
            (clean[col] < mean - 3*std)
        ]
        print(f"\n{col}:")
        print(f"Среднее: {mean:.1f}, Стд: {std:.1f}")
        print(f"Выбросов: {len(outliers)}")
        
#───────────────────────── Планшет скважины ───────────────────────── 

    collector = (
        (clean['GAMMA'] < 60) & 
        (clean['RESISTIVITY'] > 10) &
        (clean['POROSITY'] > 0.0019) 
    )
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, sharey = True, figsize = (12, 10))

    ax1.plot(clean['GAMMA'], clean.index, color = 'red', label = 'Гамма каротаж')
    ax1.fill_betweenx(clean.index, 0, clean['GAMMA'].max(),
                    where = (clean['GAMMA'] < 60),
                    color = 'green', alpha = 0.3)
    ax2.plot(clean['RESISTIVITY'], clean.index, color = 'yellow', label = 'Сопротивление')
    ax2.fill_betweenx(clean.index, 0, clean['RESISTIVITY'].max(),
                    where = (clean['RESISTIVITY'] > 10),
                    color = 'green', alpha = 0.3)
    ax3.plot(clean['POROSITY'], clean.index, color = 'black', label = 'Пористость')
    ax3.fill_betweenx(clean.index, 0, clean['POROSITY'].max(),
                    where = (clean['POROSITY'] > 0.0019),
                    color = 'green', alpha = 0.3)
    ax1.invert_yaxis()
    fig.suptitle(f'Планшет скважины {well}')
    
    ax1.set(xlabel = 'Гамма каротаж, gAPI', ylabel = 'Глубина, м')
    ax1.grid()
    ax1.legend()
    ax2.set(xlabel = 'Сопротивление, ohm.m')
    ax2.grid()
    ax2.legend()
    ax3.set(xlabel = 'Пористость, m3/m3')
    ax3.grid()
    ax3.legend()
    
    plt.draw() 
    
    for ax in [ax1, ax2, ax3]:
        ax.fill_betweenx(clean.index, 
                    ax.get_xlim()[0], ax.get_xlim()[1],
                    where=collector,
                    color='purple', alpha=0.4,
                    label='Коллектор')
        
    plt.tight_layout()
    plt.show()
#───────────────────────── Корреляционные матрицы ───────────────────────── 

    correlation_matrix = clean.corr()
    sns.heatmap (data = correlation_matrix, annot = True, cmap = 'coolwarm', fmt = '.2f')
    plt.show()
    
    print(clean[collector])
    collectors = clean[collector]
    print(f"\nПотенциальные коллекторы: {len(collectors)} замеров")
    print(collectors[['GAMMA', 'RESISTIVITY', 'POROSITY']])
    
    return clean

for well in ['A15', 'A16', 'A10']:
    print(f"\n{'='*50}")
    print(f"АНАЛИЗ СКВАЖИНЫ {well}")
    print(f"{'='*50}")
    analyze_well(well)

# %%
