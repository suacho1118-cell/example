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
    layout="wide",
    initial_sidebar_state="collapsed"
)

DATA_FILE = "fridge_data.json"
MAX_FOODS = 20

KST = ZoneInfo("Asia/Seoul")


# =========================================================
# 데이터 저장 / 불러오기
# =========================================================

def load_foods():
    if not os.path.exists(DATA_FILE):
        return []

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []


def save_foods(foods):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(foods, f, ensure_ascii=False, indent=2)


# =========================================================
# 세션 상태
# =========================================================

if "page" not in st.session_state:
    st.session_state.page = "home"

if "selected_food" not in st.session_state:
    st.session_state.selected_food = None

if "foods" not in st.session_state:
    st.session_state.foods = load_foods()

if "selected_storage" not in st.session_state:
    st.session_state.selected_storage = None


# =========================================================
# CSS
# =========================================================

st.markdown(
    """
    <style>

    /* 전체 배경 */
    .stApp {
        background:
            linear-gradient(
                rgba(245, 240, 228, 0.88),
                rgba(245, 240, 228, 0.92)
            );
    }

    /* 기본 여백 */
    .block-container {
        max-width: 1100px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    /* 제목 */
    .main-title {
        text-align: center;
        font-size: 4rem;
        font-weight: 900;
        color: #3f4d35;
        letter-spacing: -3px;
        margin-top: 80px;
        margin-bottom: 15px;
        text-shadow: 3px 3px 0px #ffffff;
    }

    .subtitle {
        text-align: center;
        font-size: 1.2rem;
        color: #66705f;
        margin-bottom: 50px;
    }

    /* 주방 배경 느낌 */
    .kitchen-bg {
        padding: 50px 30px;
        border-radius: 35px;
        background:
            linear-gradient(
                135deg,
                rgba(255,255,255,0.9),
                rgba(229,220,198,0.85)
            );
        box-shadow: 0 10px 35px rgba(80,70,50,0.15);
        min-height: 500px;
    }

    /* 카드 */
    .food-card {
        background: rgba(255,255,255,0.92);
        border-radius: 25px;
        padding: 25px;
        margin-bottom: 20px;
        box-shadow: 0 7px 20px rgba(80,70,50,0.13);
        border: 2px solid rgba(120,120,100,0.12);
    }

    .food-emoji {
        font-size: 4rem;
        text-align: center;
    }

    .food-name {
        text-align: center;
        font-size: 1.35rem;
        font-weight: 800;
        color: #40483b;
    }

    /* 결과 숫자 */
    .index-number {
        text-align: center;
        font-size: 4rem;
        font-weight: 900;
        margin: 15px;
    }

    .warning {
        background: #ffe1e1;
        border: 2px solid #d84a4a;
        color: #9b2424;
        padding: 15px;
        border-radius: 15px;
        text-align: center;
        font-weight: 700;
        margin: 20px 0;
    }

    .notice {
        background: #fff7d6;
        border: 1px solid #e5c75f;
        color: #6f5c20;
        padding: 15px;
        border-radius: 15px;
        margin-top: 25px;
        font-size: 0.9rem;
    }

    /* 버튼 */
    div.stButton > button {
        border-radius: 18px;
        min-height: 50px;
        font-weight: 700;
    }

    /* 접시 */
    .plate-wrapper {
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 30px 0;
    }

    .plate {
        width: 330px;
        height: 330px;
        border-radius: 50%;
        background: #eeeeee;
        border: 15px solid #d1d1d1;
        box-shadow:
            inset 0 0 0 15px #fafafa,
            0 12px 25px rgba(0,0,0,0.18);
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
        transition: height 0.5s ease;
    }

    .plate-inner {
        width: 230px;
        height: 230px;
        border-radius: 50%;
        background: rgba(255,255,255,0.72);
        position: relative;
        z-index: 2;
        display: flex;
        justify-content: center;
        align-items: center;
        text-align: center;
    }

    .plate-text {
        font-size: 2rem;
        font-weight: 900;
        color: #444;
        z-index: 3;
    }

    /* 보관환경 선택 */
    .storage-box {
        background: rgba(255,255,255,0.92);
        border-radius: 25px;
        padding: 25px;
        text-align: center;
        box-shadow: 0 7px 20px rgba(80,70,50,0.12);
        min-height: 170px;
    }

    .storage-icon {
        font-size: 4rem;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# 식품별 기본 미생물 증식 특성
# =========================================================

FOOD_TYPES = {
    "🍚 밥": {
        "base": 30,
        "optimal_temp": 25,
        "description": "전분이 풍부하여 보관 환경에 따라 미생물 증식이 일어날 수 있습니다."
    },
    "🥩 고기": {
        "base": 45,
        "optimal_temp": 25,
        "description": "단백질과 수분이 풍부하여 적절한 저온 보관이 중요합니다."
    },
    "🐟 생선": {
        "base": 50,
        "optimal_temp": 20,
        "description": "수분 함량이 높아 온도와 보관 기간의 영향을 크게 받을 수 있습니다."
    },
    "🥚 달걀": {
        "base": 25,
        "optimal_temp": 20,
        "description": "보관 조건과 표면 오염 등에 따라 미생물 증식 정도가 달라질 수 있습니다."
    },
    "🥛 유제품": {
        "base": 40,
        "optimal_temp": 15,
        "description": "저온에서 보관하는 것이 일반적으로 중요합니다."
    },
    "🥗 채소": {
        "base": 20,
        "optimal_temp": 15,
        "description": "종류와 수분 함량에 따라 저장 중 미생물 변화가 달라질 수 있습니다."
    },
    "🍓 과일": {
        "base": 15,
        "optimal_temp": 20,
        "description": "과일 종류와 숙성 상태에 따라 변화 속도가 달라질 수 있습니다."
    },
    "🍲 국/찌개": {
        "base": 35,
        "optimal_temp": 20,
        "description": "조리 후에는 빠르게 식혀 적절한 온도에서 보관하는 것이 중요합니다."
    },
    "🍞 빵": {
        "base": 15,
        "optimal_temp": 25,
        "description": "수분 함량과 보관 환경에 따라 곰팡이 등의 변화가 나타날 수 있습니다."
    },
    "🍱 기타": {
        "base": 30,
        "optimal_temp": 20,
        "description": "식품의 종류와 특성에 따라 미생물 증식 양상이 달라질 수 있습니다."
    }
}


# =========================================================
# 증식 지수 계산
# =========================================================

def calculate_index(
    food_type,
    storage,
    temperature,
    days,
    opened,
    cooked
):
    """
    교육용 미생물 증식 위험 지수 모델.

    실제 미생물 수를 측정하는 모델이 아니며,
    식품 안전성을 판단하는 절대적인 기준이 아님.
    """

    food = FOOD_TYPES[food_type]

    score = food["base"]

    # -----------------------------------------------------
    # 보관 환경 보정
    # -----------------------------------------------------

    storage_factor = {
        "냉장": -20,
        "냉동": -40,
        "상온": 15
    }

    score += storage_factor[storage]

    # -----------------------------------------------------
    # 온도 영향
    # 온도가 높을수록 일반적으로 증식 가능성이 커지는
    # 방향으로 단순화
    # -----------------------------------------------------

    if storage == "냉동":
        if temperature <= -18:
            score -= 30
        elif temperature <= -10:
            score -= 20
        else:
            score -= 5

    elif storage == "냉장":
        if temperature <= 4:
            score -= 15
        elif temperature <= 8:
            score -= 5
        elif temperature <= 12:
            score += 10
        else:
            score += 25

    else:
        # 상온
        if temperature <= 10:
            score -= 5
        elif temperature <= 20:
            score += 5
        elif temperature <= 30:
            score += 20
        else:
            score += 35

    # -----------------------------------------------------
    # 보관 기간 영향
    # 시간이 길어질수록 증가
    # -----------------------------------------------------

    if days > 0:
        time_effect = min(45, math.log1p(days) * 13)
        score += time_effect

    # -----------------------------------------------------
    # 개봉 여부
    # -----------------------------------------------------

    if opened:
        score += 12

    # -----------------------------------------------------
    # 조리 여부
    # -----------------------------------------------------

    if cooked:
        score += 8

    # -----------------------------------------------------
    # 최종 범위 0~100
    # -----------------------------------------------------

    score = max(0, min(100, round(score)))

    return score


# =========================================================
# 색상 / 상태
# =========================================================

def get_index_info(index):

    if index <= 20:
        return {
            "color": "#4caf50",
            "name": "낮음",
            "message": "현재 입력된 조건에서는 상대적으로 낮은 수준으로 추정됩니다."
        }

    elif index <= 40:
        return {
            "color": "#f0c419",
            "name": "주의",
            "message": "보관 환경과 기간을 계속 확인하는 것이 좋습니다."
        }

    elif index <= 60:
        return {
            "color": "#f28c28",
            "name": "관찰 필요",
            "message": "보관 조건에 따라 미생물 증식 가능성이 커질 수 있습니다."
        }

    elif index <= 80:
        return {
            "color": "#e53935",
            "name": "높음",
            "message": "보관 상태를 주의 깊게 확인하세요."
        }

    else:
        return {
            "color": "#9b111e",
            "name": "매우 높음",
            "message": "보관 상태를 반드시 확인하세요."
        }


# =========================================================
# 날짜 / 경과일
# =========================================================

def get_days(start_date):
    today = datetime.now(KST).date()

    days = (today - start_date).days

    return max(0, days)


# =========================================================
# 권장 섭취 기간
# 교육용 표시
# =========================================================

def recommended_days(storage, food_type):

    if storage == "냉동":
        return 30

    if storage == "냉장":

        if food_type in ["🥩 고기", "🐟 생선"]:
            return 3

        if food_type in ["🍚 밥", "🍲 국/찌개"]:
            return 3

        if food_type == "🥛 유제품":
            return 5

        return 7

    # 상온
    if food_type in ["🍚 밥", "🍲 국/찌개"]:
        return 1

    if food_type == "🥩 고기":
        return 0

    return 3


# =========================================================
# 접시 UI
# =========================================================

def plate_html(index):

    info = get_index_info(index)

    height = max(3, index)

    return f"""
    <div class="plate-wrapper">
        <div class="plate">
            <div
                class="plate-fill"
                style="
                    height:{height}%;
                    background:{info['color']};
                    opacity:0.82;
                ">
            </div>

            <div class="plate-inner">
                <div class="plate-text">
                    🦠<br>
                    {index}%
                </div>
            </div>
        </div>
    </div>
    """


# =========================================================
# 홈 화면
# =========================================================

def home_page():

    st.markdown(
        """
        <div class="kitchen-bg">

            <div style="text-align:center;font-size:5rem;">
                🧊 🍎 🥛 🍚 🥬
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
        ⚠️ 이 앱에서 제공하는 미생물 증식 지수는
        식품의 보관 환경과 기간 등을 바탕으로 만든
        <b>교육용 추정값</b>입니다.<br><br>

        실제 미생물의 수를 측정하거나 실제 식품의 상태와
        안전성을 보장하지 않습니다.
        따라서 증식 지수를 실제 섭취 가능 여부를 판단하는
        절대적인 기준으로 사용하지 마세요.
        </div>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# 식품 입력 화면
# =========================================================

def input_page():

    if st.button("← 내 냉장고로 돌아가기"):
        st.session_state.page = "home"
        st.rerun()

    st.title("🥕 새 식품 추가하기")

    # -----------------------------------------------------
    # 보관 환경
    # -----------------------------------------------------

    st.subheader("1. 보관 환경을 선택하세요")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button(
            "🧊\n\n냉장",
            use_container_width=True
        ):
            st.session_state.selected_storage = "냉장"

    with col2:
        if st.button(
            "❄️\n\n냉동",
            use_container_width=True
        ):
            st.session_state.selected_storage = "냉동"

    with col3:
        if st.button(
            "🧺\n\n상온",
            use_container_width=True
        ):
            st.session_state.selected_storage = "상온"

    storage = st.session_state.selected_storage

    if storage is None:
        st.info("보관 환경을 먼저 선택해주세요.")
        return

    st.success(f"선택한 보관 환경: {storage}")

    st.divider()

    # -----------------------------------------------------
    # 식품 정보
    # -----------------------------------------------------

    st.subheader("2. 식품 정보를 입력하세요")

    food_type = st.selectbox(
        "식품 종류",
        list(FOOD_TYPES.keys())
    )

    start_date = st.date_input(
        "보관 시작 날짜",
        value=datetime.now(KST).date(),
        max_value=datetime.now(KST).date()
    )

    # 온도 범위
    if storage == "냉장":
        default_temp = 4
        min_temp = -5
        max_temp = 20

    elif storage == "냉동":
        default_temp = -18
        min_temp = -30
        max_temp = 5

    else:
        default_temp = 20
        min_temp = -5
        max_temp = 40

    temperature = st.number_input(
        "현재 보관 온도 (℃)",
        min_value=float(min_temp),
        max_value=float(max_temp),
        value=float(default_temp),
        step=0.5
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

    # -----------------------------------------------------
    # 미래 날짜 방지
    # -----------------------------------------------------

    today = datetime.now(KST).date()

    if start_date > today:
        st.error("보관 시작일은 현재보다 미래로 설정할 수 없습니다.")
        return

    # -----------------------------------------------------
    # 결과 계산
    # -----------------------------------------------------

    days = get_days(start_date)

    index = calculate_index(
        food_type=food_type,
        storage=storage,
        temperature=temperature,
        days=days,
        opened=opened == "개봉함",
        cooked=cooked == "조리함"
    )

    st.divider()

    if st.button(
        "🦠 내 식품 속 미생물 확인하기",
        use_container_width=True
    ):

        if len(st.session_state.foods) >= MAX_FOODS:
            st.error(
                f"식품은 최대 {MAX_FOODS}개까지만 등록할 수 있습니다."
            )
            return

        food = {
            "id": datetime.now(KST).strftime("%Y%m%d%H%M%S%f"),
            "food_type": food_type,
            "storage": storage,
            "start_date": start_date.isoformat(),
            "temperature": temperature,
            "opened": opened == "개봉함",
            "cooked": cooked == "조리함"
        }

        st.session_state.foods.append(food)

        save_foods(st.session_state.foods)

        st.session_state.selected_food = food["id"]
        st.session_state.page = "result"

        st.rerun()


# =========================================================
# 저장된 식품의 현재 증식지수 계산
# =========================================================

def calculate_food_current_index(food):

    today = datetime.now(KST).date()

    start_date = date.fromisoformat(food["start_date"])

    days = max(0, (today - start_date).days)

    return calculate_index(
        food_type=food["food_type"],
        storage=food["storage"],
        temperature=food["temperature"],
        days=days,
        opened=food["opened"],
        cooked=food["cooked"]
    )


# =========================================================
# 결과 화면
# =========================================================

def result_page():

    food = None

    for item in st.session_state.foods:
        if item["id"] == st.session_state.selected_food:
            food = item
            break

    if food is None:
        st.session_state.page = "home"
        st.rerun()

    if st.button("← 내 냉장고로 돌아가기"):
        st.session_state.page = "home"
        st.rerun()

    index = calculate_food_current_index(food)

    info = get_index_info(index)

    start_date = date.fromisoformat(food["start_date"])

    days = get_days(start_date)

    recommended = recommended_days(
        food["storage"],
        food["food_type"]
    )

    st.title(f"{food['food_type']} 미생물 결과")

    # 접시
    st.markdown(
        plate_html(index),
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div class="index-number"
             style="color:{info['color']}">
            미생물 증식 지수 {index}%
        </div>

        <div style="text-align:center;font-size:1.3rem;">
            현재 상태: <b>{info['name']}</b>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.write("")

    # 정보
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

    st.info(info["message"])

    if recommended > 0:

        if days >= recommended:
            st.warning(
                f"가능하면 {recommended}일 이내 섭취하는 것을 "
                f"권장하는 교육용 기준을 초과했습니다. "
                f"실제 식품 상태를 함께 확인하세요."
            )

        else:
            remaining = recommended - days

            st.success(
                f"교육용 참고 기준으로는 가능하면 "
                f"{remaining}일 이내에 섭취하세요."
            )

    else:
        st.warning(
            "이 식품은 보관 조건에 따라 상태가 빠르게 변할 수 있으므로 "
            "일반적인 기간만으로 안전성을 판단하지 마세요."
        )

    # 상세 정보
    with st.expander("🔍 입력한 식품 정보 보기"):

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
            f"**개봉 여부:** "
            f"{'개봉함' if food['opened'] else '미개봉'}"
        )

        st.write(
            f"**조리 여부:** "
            f"{'조리함' if food['cooked'] else '조리하지 않음'}"
        )

    st.markdown(
        """
        <div class="notice">
        ⚠️ <b>주의</b><br>
        이 미생물 증식 지수는 실제 미생물의 수를 측정한 값이 아닙니다.
        식품 종류, 온도, 보관 기간 등의 조건을 단순화하여 계산한
        교육용 지표입니다.<br><br>

        실제 식품의 상태와 안전성을 보장하지 않으며,
        이 지수만으로 식품의 섭취 가능 여부를 판단해서는 안 됩니다.
        </div>
        """,
        unsafe_allow_html=True
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
            "아직 등록된 식품이 없습니다.\n\n"
            "새 식품을 추가해보세요!"
        )

        if st.button("🥕 새 식품 추가하기"):
            st.session_state.page = "input"
            st.rerun()

        return

    st.write(
        f"현재 {len(foods)}개의 식품이 등록되어 있습니다. "
        f"(최대 {MAX_FOODS}개)"
    )

    # -----------------------------------------------------
    # 카드
    # -----------------------------------------------------

    cols = st.columns(3)

    for i, food in enumerate(foods):

        index = calculate_food_current_index(food)

        info = get_index_info(index)

        with cols[i % 3]:

            st.markdown(
                f"""
                <div class="food-card">

                    <div class="food-emoji">
                        {food['food_type'].split()[0]}
                    </div>

                    <div class="food-name">
                        {food['food_type']}
                    </div>

                    <div style="
                        text-align:center;
                        font-size:2rem;
                        font-weight:900;
                        color:{info['color']};
                        margin-top:10px;
                    ">
                        {index}%
                    </div>

                    <div style="
                        text-align:center;
                        color:#777;
                        margin-top:5px;
                    ">
                        {food['storage']} ·
                        {get_days(date.fromisoformat(food['start_date']))}일째
                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )

            if index >= 80:
                st.warning("⚠️ 보관 상태를 확인하세요!")

            if st.button(
                "상세 결과 보기",
                key=f"detail_{food['id']}",
                use_container_width=True
            ):
                st.session_state.selected_food = food["id"]
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

                save_foods(st.session_state.foods)

                st.rerun()


# =========================================================
# 페이지 실행
# =========================================================

if st.session_state.page == "home":
    home_page()

elif st.session_state.page == "input":
    input_page()

elif st.session_state.page == "result":
    result_page()

elif st.session_state.page == "fridge":
    fridge_page()
