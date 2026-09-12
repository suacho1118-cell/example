import streamlit as st
import json
import os
import math
from datetime import datetime, date
from zoneinfo import ZoneInfo


# =========================================================
# 기본 설정
# =========================================================

st.set_page_config(
    page_title="내 냉장고 속 미생물",
    page_icon="🦠",
    layout="wide"
)

DATA_FILE = "fridge_data.json"
MAX_FOODS = 20

KST = ZoneInfo("Asia/Seoul")


# =========================================================
# 데이터 불러오기
# =========================================================

def load_foods():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []

    return []


def save_foods(foods):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(foods, f, ensure_ascii=False, indent=2)


# =========================================================
# 세션 상태
# =========================================================

if "page" not in st.session_state:
    st.session_state.page = "home"

if "foods" not in st.session_state:
    st.session_state.foods = load_foods()

if "selected_food" not in st.session_state:
    st.session_state.selected_food = None

if "storage" not in st.session_state:
    st.session_state.storage = None


# =========================================================
# CSS
# =========================================================

st.markdown("""
<style>

.stApp {
    background-color: #f5f1e8;
}

.block-container {
    max-width: 1100px;
    padding-top: 30px;
}


/* =========================
   시작 화면
   ========================= */

.home-box {
    min-height: 560px;
    border-radius: 35px;

    background:
        linear-gradient(
            rgba(255,255,255,0.62),
            rgba(255,255,255,0.72)
        ),
        linear-gradient(
            135deg,
            #ddd4c3 0%,
            #eee8dc 45%,
            #d7d0c2 100%
        );

    box-shadow:
        0 15px 40px rgba(70,60,45,0.18);

    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;

    position: relative;
    overflow: hidden;
}


/* 주방 느낌을 주는 가구 */

.fridge-shape {
    position: absolute;
    left: 7%;
    top: 13%;
    width: 150px;
    height: 330px;

    background: rgba(220,225,222,0.72);

    border-radius: 18px;

    box-shadow:
        inset 0 0 0 5px rgba(255,255,255,0.55),
        0 10px 25px rgba(0,0,0,0.12);

    filter: blur(1px);
}

.fridge-handle {
    position: absolute;
    right: 20px;
    top: 110px;
    width: 8px;
    height: 100px;
    border-radius: 5px;
    background: rgba(100,100,100,0.3);
}


.shelf {
    position: absolute;
    right: 8%;
    bottom: 15%;
    width: 250px;
    height: 18px;
    background: rgba(120,105,80,0.28);
    border-radius: 10px;
}

.basket {
    position: absolute;
    right: 12%;
    bottom: 18%;
    width: 130px;
    height: 90px;
    border-radius: 15px 15px 25px 25px;
    background: rgba(190,165,115,0.45);
}

.food-decoration {
    position: absolute;
    font-size: 3.2rem;
    opacity: 0.65;
    filter: blur(0.5px);
}

.apple {
    right: 25%;
    bottom: 28%;
}

.milk {
    right: 8%;
    bottom: 31%;
}

.carrot {
    left: 23%;
    bottom: 18%;
}


/* 메인 제목 */

.main-title {
    position: relative;
    z-index: 5;

    font-size: 4.2rem;
    font-weight: 900;

    color: #3f4d35;

    letter-spacing: -4px;

    text-align: center;

    text-shadow:
        3px 3px 0px white;

    margin-bottom: 15px;
}


.subtitle {
    position: relative;
    z-index: 5;

    font-size: 1.2rem;
    color: #5d6655;

    text-align: center;

    line-height: 1.8;

    margin-bottom: 35px;
}


/* =========================
   카드
   ========================= */

.food-card {
    background: rgba(255,255,255,0.9);
    padding: 25px;
    border-radius: 25px;

    box-shadow:
        0 8px 25px rgba(60,50,40,0.12);

    text-align: center;

    margin-bottom: 10px;
}


.food-emoji {
    font-size: 4rem;
}

.food-name {
    font-size: 1.2rem;
    font-weight: 800;
    margin-top: 10px;
}


/* =========================
   결과 접시
   ========================= */

.plate-wrapper {
    display: flex;
    justify-content: center;
    margin: 30px;
}

.plate {
    width: 330px;
    height: 330px;

    border-radius: 50%;

    background: #eeeeee;

    border: 15px solid #cccccc;

    box-shadow:
        inset 0 0 0 15px #ffffff,
        0 15px 30px rgba(0,0,0,0.18);

    position: relative;
    overflow: hidden;

    display: flex;
    justify-content: center;
    align-items: center;
}


.plate-fill {
    position: absolute;
    bottom: 0;
    left: 0;

    width: 100%;

    opacity: 0.82;
}


.plate-inner {
    position: relative;
    z-index: 2;

    width: 220px;
    height: 220px;

    border-radius: 50%;

    background: rgba(255,255,255,0.72);

    display: flex;
    justify-content: center;
    align-items: center;
}


.plate-text {
    text-align: center;

    font-size: 2rem;
    font-weight: 900;

    color: #444;
}


/* =========================
   안내
   ========================= */

.notice {
    background: #fff6d6;

    border: 1px solid #e5c75f;

    border-radius: 15px;

    padding: 18px;

    margin-top: 30px;

    color: #675722;
}


/* =========================
   버튼
   ========================= */

div.stButton > button {
    border-radius: 18px;

    min-height: 52px;

    font-weight: 700;

    font-size: 1rem;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# 식품 종류
# =========================================================

FOOD_TYPES = {
    "🍚 밥": 30,
    "🥩 고기": 45,
    "🐟 생선": 50,
    "🥚 달걀": 25,
    "🥛 유제품": 40,
    "🥗 채소": 20,
    "🍓 과일": 15,
    "🍲 국/찌개": 35,
    "🍞 빵": 15,
    "🍱 기타": 30
}


# =========================================================
# 증식 지수 계산
# =========================================================

def calculate_index(
    food,
    storage,
    temperature,
    days,
    opened,
    cooked
):

    score = FOOD_TYPES[food]

    # 보관 환경
    if storage == "냉장":
        score -= 20

    elif storage == "냉동":
        score -= 40

    elif storage == "상온":
        score += 15


    # 온도
    if storage == "냉장":

        if temperature <= 4:
            score -= 15

        elif temperature <= 8:
            score -= 5

        elif temperature <= 12:
            score += 10

        else:
            score += 25


    elif storage == "냉동":

        if temperature <= -18:
            score -= 30

        elif temperature <= -10:
            score -= 20

        else:
            score -= 5


    else:

        if temperature <= 10:
            score -= 5

        elif temperature <= 20:
            score += 5

        elif temperature <= 30:
            score += 20

        else:
            score += 35


    # 보관 기간
    if days > 0:
        score += min(45, math.log1p(days) * 13)


    # 개봉
    if opened:
        score += 12


    # 조리
    if cooked:
        score += 8


    # 0~100 제한
    score = max(0, min(100, round(score)))

    return score


# =========================================================
# 색상 / 상태
# =========================================================

def get_status(index):

    if index <= 20:
        return "#4CAF50", "낮음"

    elif index <= 40:
        return "#E6C229", "주의"

    elif index <= 60:
        return "#F28C28", "관찰 필요"

    elif index <= 80:
        return "#E53935", "높음"

    else:
        return "#8B0000", "매우 높음"


# =========================================================
# 보관 기간
# =========================================================

def get_days(start_date):

    today = datetime.now(KST).date()

    return max(
        0,
        (today - start_date).days
    )


# =========================================================
# 홈 화면
# =========================================================

def home_page():

    st.markdown(
        """
<div class="home-box">

<div class="fridge-shape">
    <div class="fridge-handle"></div>
</div>

<div class="shelf"></div>

<div class="basket"></div>

<div class="food-decoration apple">
    🍎
</div>

<div class="food-decoration milk">
    🥛
</div>

<div class="food-decoration carrot">
    🥕
</div>

<div class="main-title">
    내 냉장고 속 미생물
</div>

<div class="subtitle">
    내 식품의 보관 환경을 입력하고<br>
    미생물 증식 정도를 알아보세요!
</div>

</div>
        """,
        unsafe_allow_html=True
    )

    st.write("")

    col1, col2 = st.columns(2)

    with col1:
        if st.button(
            "🥕 새 식품 추가하기",
            use_container_width=True
        ):
            st.session_state.page = "input"
            st.rerun()

    with col2:
        if st.button(
            "🧊 내 냉장고 구경하기",
            use_container_width=True
        ):
            st.session_state.page = "fridge"
            st.rerun()

    st.markdown(
        """
<div class="notice">

⚠️ <b>중요한 안내</b>

<br><br>

이 앱의 미생물 증식 지수는
식품 종류, 보관 온도, 보관 기간 등의 조건을
단순화하여 계산한 <b>교육용 추정값</b>입니다.

<br><br>

실제 미생물의 수를 측정하거나
실제 식품의 상태와 안전성을 보장하지 않습니다.

<br><br>

따라서 이 지수만으로 식품의 섭취 가능 여부를
판단해서는 안 됩니다.

</div>
        """,
        unsafe_allow_html=True
    )

# =========================================================
# 입력 화면
# =========================================================

def input_page():

    if st.button("← 시작 화면"):

        st.session_state.page = "home"

        st.rerun()


    st.title("🥕 새 식품 추가하기")


    st.subheader("1. 보관 환경")


    col1, col2, col3 = st.columns(3)


    with col1:

        if st.button(
            "🧊\n냉장",
            use_container_width=True
        ):

            st.session_state.storage = "냉장"


    with col2:

        if st.button(
            "❄️\n냉동",
            use_container_width=True
        ):

            st.session_state.storage = "냉동"


    with col3:

        if st.button(
            "🧺\n상온",
            use_container_width=True
        ):

            st.session_state.storage = "상온"


    storage = st.session_state.storage


    if storage is None:

        st.info("보관 환경을 선택해주세요.")

        return


    st.success(
        f"현재 선택: {storage}"
    )


    st.divider()


    st.subheader("2. 식품 정보")


    food_type = st.selectbox(
    "식품 종류",
    list(FOOD_TYPES.keys())
)

food_name = st.text_input(
    "식품 이름",
    placeholder="예: 김치볶음밥, 딸기잼, 남은 피자 등"
)

if food_name.strip() == "":
    food_name = food_type


    today = datetime.now(KST).date()


    start_date = st.date_input(
        "보관 시작 날짜",
        value=today,
        max_value=today
    )


    if storage == "냉장":

        temperature = st.number_input(
            "현재 보관 온도 (℃)",
            -5.0,
            20.0,
            4.0,
            0.5
        )

    elif storage == "냉동":

        temperature = st.number_input(
            "현재 보관 온도 (℃)",
            -30.0,
            5.0,
            -18.0,
            0.5
        )

    else:

        temperature = st.number_input(
            "현재 보관 온도 (℃)",
            -5.0,
            40.0,
            20.0,
            0.5
        )


    opened = st.radio(
        "개봉 여부",
        ["미개봉", "개봉함"],
        horizontal=True
    )


    cooked = st.radio(
        "조리 여부",
        ["조리하지 않음", "조리함"],
        horizontal=True
    )


    days = get_days(start_date)


    if st.button(
        "🦠 내 식품 속 미생물 확인하기",
        use_container_width=True
    ):

        if len(st.session_state.foods) >= MAX_FOODS:

            st.error(
                f"식품은 최대 {MAX_FOODS}개까지 등록할 수 있습니다."
            )

            return


        food_data = {

    "id": datetime.now(KST).strftime(
        "%Y%m%d%H%M%S%f"
    ),

    "food_type": food_type,

    "food_name": food_name.strip(),

    "storage": storage,

    "start_date": start_date.isoformat(),

    "temperature": temperature,

    "opened": opened == "개봉함",

    "cooked": cooked == "조리함"
}

        st.session_state.foods.append(
            food_data
        )

        save_foods(
            st.session_state.foods
        )


        st.session_state.selected_food = (
            food_data["id"]
        )

        st.session_state.page = "result"

        st.rerun()


# =========================================================
# 현재 식품 지수
# =========================================================

def current_index(food):

    start = date.fromisoformat(
        food["start_date"]
    )

    days = get_days(start)


    return calculate_index(
        food["food_type"],
        food["storage"],
        food["temperature"],
        days,
        food["opened"],
        food["cooked"]
    )


# =========================================================
# 결과 화면
# =========================================================

def result_page():

    food = next(
        (x for x in st.session_state.foods
         if x["id"] == st.session_state.selected_food),
        None
    )

    if food is None:
        st.session_state.page = "home"
        st.rerun()

    if st.button("← 내 냉장고로 돌아가기"):
        st.session_state.page = "home"
        st.rerun()

    index = current_index(food)

    color, status = get_status(index)

    start = date.fromisoformat(food["start_date"])
    days = get_days(start)

    st.title(f"{food['food_name']} 미생물 결과")

    # =========================================
    # 접시
    # =========================================

    st.markdown(
        f"""
<div style="display:flex;justify-content:center;margin:30px;">

<div style="
width:300px;
height:300px;
border-radius:50%;
background:#eeeeee;
border:15px solid #cccccc;
box-shadow:inset 0 0 0 15px white, 0 15px 30px rgba(0,0,0,0.18);
position:relative;
overflow:hidden;
display:flex;
justify-content:center;
align-items:center;
">

<div style="
position:absolute;
bottom:0;
left:0;
width:100%;
height:{max(index, 3)}%;
background:{color};
opacity:0.82;
"></div>

<div style="
position:relative;
z-index:2;
width:200px;
height:200px;
border-radius:50%;
background:rgba(255,255,255,0.75);
display:flex;
justify-content:center;
align-items:center;
text-align:center;
font-size:32px;
font-weight:900;
color:#444444;
">

🦠<br>{index}%

</div>

</div>

</div>
        """,
        unsafe_allow_html=True
    )

    # =========================================
    # 증식 지수
    # =========================================

    st.markdown(
        f"""
<h1 style="text-align:center;color:{color};">
미생물 증식 지수 {index}%
</h1>

<p style="text-align:center;font-size:20px;">
현재 상태: <b>{status}</b>
</p>
        """,
        unsafe_allow_html=True
    )

    # =========================================
    # 기본 정보
    # =========================================

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "보관 환경",
            food["storage"]
        )

    with col2:
        st.metric(
            "보관 기간",
            f"{days}일째"
        )

    with col3:
        st.metric(
            "현재 온도",
            f"{food['temperature']}℃"
        )

    # =========================================
    # 상태 설명
    # =========================================

    if index <= 20:

        st.success(
            "현재 입력된 조건에서는 미생물 증식 지수가 "
            "상대적으로 낮게 계산되었습니다."
        )

    elif index <= 40:

        st.info(
            "보관 환경과 기간을 계속 확인해 주세요."
        )

    elif index <= 60:

        st.warning(
            "보관 환경이나 기간에 따라 "
            "미생물 증식 가능성이 커질 수 있습니다."
        )

    elif index <= 80:

        st.warning(
            "⚠️ 미생물 증식 지수가 높은 편입니다. "
            "보관 상태를 주의 깊게 확인하세요."
        )

    else:

        st.error(
            "⚠️ 보관 상태를 확인하세요!"
        )

    # =========================================
    # 입력 정보
    # =========================================

    with st.expander("🔍 입력한 식품 정보 보기"):

        st.write(
            f"**식품 이름:** {food['food_name']}"
        )

        st.write(
            f"**식품 종류:** {food['food_type']}"
        )

        st.write(
            f"**보관 환경:** {food['storage']}"
        )

        st.write(
            f"**보관 시작일:** {food['start_date']}"
        )

        st.write(
            f"**현재 보관 온도:** {food['temperature']}℃"
        )

        st.write(
            f"**개봉 여부:** "
            f"{'개봉함' if food['opened'] else '미개봉'}"
        )

        st.write(
            f"**조리 여부:** "
            f"{'조리함' if food['cooked'] else '조리하지 않음'}"
        )

    # =========================================
    # 주의사항
    # =========================================

    st.warning(
        "⚠️ 이 앱의 미생물 증식 지수는 실제 미생물의 수를 "
        "측정한 값이 아닌 교육용 추정값입니다. "
        "실제 식품의 상태와 안전성을 보장하지 않으며, "
        "이 지수만으로 식품의 섭취 가능 여부를 판단해서는 안 됩니다."
    )


# =========================================================
# 냉장고 화면
# =========================================================

def fridge_page():

    if st.button("← 시작 화면"):

        st.session_state.page = "home"

        st.rerun()


    st.title("🧊 내 냉장고 구경하기")


    foods = st.session_state.foods


    if not foods:

        st.info(
            "아직 등록된 식품이 없습니다."
        )

        if st.button("🥕 새 식품 추가하기"):

            st.session_state.page = "input"

            st.rerun()

        return


    st.write(
        f"등록된 식품: {len(foods)} / {MAX_FOODS}"
    )


    cols = st.columns(3)


    for i, food in enumerate(foods):

        index = current_index(food)

        color, status = get_status(index)


        with cols[i % 3]:

            emoji = food["food_type"].split()[0]

            st.markdown(
                f"""
                <div class="food-card">

                    <div class="food-emoji">
                        {emoji}
                    </div>

                    <div class="food-name">
                        {food["food_name"]}
                    </div>

                    <div style="
                        font-size:2.2rem;
                        font-weight:900;
                        color:{color};
                        margin:10px;
                    ">
                        {index}%
                    </div>

                    <div>
                        {food["storage"]}
                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )


            if index >= 80:

                st.warning(
                    "⚠️ 보관 상태를 확인하세요!"
                )


            if st.button(
                "상세 결과 보기",
                key=f"detail_{food['id']}",
                use_container_width=True
            ):

                st.session_state.selected_food = (
                    food["id"]
                )

                st.session_state.page = "result"

                st.rerun()


            if st.button(
                "🗑️ 삭제",
                key=f"delete_{food['id']}",
                use_container_width=True
            ):

                st.session_state.foods = [
                    x for x in st.session_state.foods
                    if x["id"] != food["id"]
                ]

                save_foods(
                    st.session_state.foods
                )

                st.rerun()


# =========================================================
# 페이지 표시
# =========================================================

if st.session_state.page == "home":

    home_page()

elif st.session_state.page == "input":

    input_page()

elif st.session_state.page == "result":

    result_page()

elif st.session_state.page == "fridge":

    fridge_page()
