import streamlit as st

# Настройка страницы сайта
st.set_page_config(page_title="Марс-Симулятор 2026", page_icon="🚀", layout="wide")

st.title("👨‍🚀 Симулятор автономной марсианской станции")
st.markdown("---")

# ================= БОКОВОЕ МЕНЮ (ВВОД ДАННЫХ) =================
st.sidebar.header("🛸 Параметры миссии")

# Экипаж и время
crew_size = st.sidebar.number_input("Численность экипажа (чел):", min_value=1, max_value=20, value=4)
mission_days = st.sidebar.slider("Длительность симуляции (дней):", min_value=10, max_value=365, value=30)

st.sidebar.markdown("---")
st.sidebar.header("🌱 Параметры фермы")
farm_area = st.sidebar.number_input("Площадь теплицы (кв. метры):", min_value=0, max_value=500, value=50)

# Выбор метода очистки грунта (Влияет на энергию)
soil_method = st.sidebar.selectbox(
    "Метод очистки реголита от перхлоратов:",
    ["Биологический (Бактерии)", "Термический (Запекание)", "Химический (Промывка)"]
)

# Выбор защиты от радиации
radiation_shield = st.sidebar.selectbox(
    "Тип радиационной защиты:",
    ["Пассивный (Водяные экраны)", "Активный (Магнитный щит)", "Без защиты"]
)

# ================= МАТЕМАТИЧЕСКАЯ МОДЕЛЬ (РАСЧЕТЫ) =================

# Константы потребления на 1 человека в сутки
DRINK_WATER_PER_MAN = 2.0  # Питьевая вода, л
HYGIENE_WATER_PER_MAN = 2.5 # Вода на помыться/гигиену, л
OXYGEN_PER_MAN = 0.84       # Кислород, кг
CALORIES_PER_MAN = 2700     # Калории, ккал

# Константы теплицы
WATER_PER_REGOLET_M2 = 5.0  # Полив на 1 кв.м грунта в сутки, л
POTATO_YIELD_PER_M2_DAY = 0.1 # Сколько кг картошки растет с 1 кв.м в день
CALORIES_PER_KG_POTATO = 800  # Калорий в 1 кг картошки

# Расчет затрат энергии в зависимости от выбора пользователя
energy_consumption = 50.0 # Базовое потребление станции, кВт*ч в сутки

if soil_method == "Термический (Запекание)":
    energy_consumption += farm_area * 15.0 # Запекание требует много энергии
elif soil_method == "Химический (Промывка)":
    energy_consumption += farm_area * 5.0
else:
    energy_consumption += farm_area * 1.2 # Бактерии требуют минимум энергии

if radiation_shield == "Активный (Магнитный щит)":
    energy_consumption += 120.0 # Магнитный щит постоянно жрет энергию

# Эффективность СЖО (Регенерация воды)
# Если защита пассивная водяная, часть технической воды циркулирует в щитах, регенерация чуть выше
regen_rate = 0.85
if radiation_shield == "Пассивный (Водяные экраны)":
    regen_rate = 0.90

# ГЛОБАЛЬНЫЙ СУММАРНЫЙ РАСЧЕТ ЗА ВСЮ МИССИЮ
total_drink_water = crew_size * DRINK_WATER_PER_MAN * mission_days
total_hygiene_water = crew_size * HYGIENE_WATER_PER_MAN * mission_days

# Сколько воды вернет система фильтрации обратно
regenerated_water = (total_drink_water + total_hygiene_water) * regen_rate
# Безвозвратные потери человеческой воды
human_water_loss = (total_drink_water + total_hygiene_water) - regenerated_water

# Вода на полив (уходит безвозвратно в растения)
total_farm_water = farm_area * WATER_PER_REGOLET_M2 * mission_days

# Итоговый чистый расход чистой воды, которую нужно привезти с собой
total_net_water_needed = total_drink_water + total_hygiene_water + total_farm_water - regenerated_water

# Кислород и калории
total_oxygen = crew_size * OXYGEN_PER_MAN * mission_days
total_calories_needed = crew_size * CALORIES_PER_MAN * mission_days

# Производство еды фермой
total_potato_produced = farm_area * POTATO_YIELD_PER_M2_DAY * mission_days
total_calories_produced = total_potato_produced * CALORIES_PER_KG_POTATO

# Общая необходимая энергия
total_energy_needed = energy_consumption * mission_days

# ================= ВЫВОД РЕЗУЛЬТАТОВ НА ЭКРАН (ИНТЕРФЕЙС) =================

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="💧 Всего чистой воды требуется (с учетом потерь)", value=f"{total_net_water_needed:.1f} л")
    st.caption(f"Из них: питье — {total_drink_water:.0f}л, гигиена — {total_hygiene_water:.0f}л, полив — {total_farm_water:.0f}л. СЖО вернула: {regenerated_water:.1f}л.")

with col2:
    st.metric(label="💨 Необходимый запас Кислорода", value=f"{total_oxygen:.1f} кг")

with col3:
    st.metric(label="⚡ Энергопотребление базы", value=f"{total_energy_needed:.1f} кВт*ч")
    st.caption(f"Суточный расход: {energy_consumption:.1f} кВт*ч (Защита: {radiation_shield}, Очистка: {soil_method})")

st.markdown("---")
st.subheader("📊 Баланс продовольствия (Картофель)")

col_f1, col_f2 = st.columns(2)

with col_f1:
    st.info(f"🧬 Потребность экипажа в энергии: **{total_calories_needed:,} ккал**")
    st.success(f"🥔 Произведено фермой за миссию: **{total_potato_produced:.1f} кг** ({total_calories_produced:,} ккал)")

with col_f2:
    balance = total_calories_produced - total_calories_needed
    if balance >= 0:
        st.success(f"✅ Ферма полностью обеспечивает экипаж! Избыток калорий: {balance:,} ккал")
    else:
        st.error(f"🚨 Внимание! Дефицит продовольствия! Не хватает {-balance:,} ккал. Нужно увеличить площадь теплицы!")

# Информационный блок для защиты проекта
st.markdown("---")
with st.expander("ℹ️ Посмотреть физико-биологическое обоснование модели"):
    st.write(f"""
    * **Водный баланс:** Расчет учитывает строгое разделение на питьевую воду и воду для санитарных нужд. Коэффициент регенерации СЖО равен **{regen_rate*100}%**. Вода для полива грунта ({WATER_PER_REGOLET_M2} л/м²) поглощается реголитом и не подлежит повторной быстрой фильтрации.
    * **Радиационный щит:** Выбор режима '{radiation_shield}' напрямую влияет на энергосистему марсианского комплекса.
    * **Детоксикация:** Очистка реголита от перхлоратов методом '{soil_method}' заложена в алгоритм как переменный коэффициент энергетических затрат на квадратный метр полезной площади фермы.
    """)
