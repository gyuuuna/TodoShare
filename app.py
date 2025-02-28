import os
import random
import streamlit as st
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import datetime
import pytz

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")

client = MongoClient(MONGO_URI, server_api=ServerApi("1"))
db = client[DB_NAME]
todos = db[COLLECTION_NAME]

kst = pytz.timezone("Asia/Seoul")

st.set_page_config(page_title="도장깨기", layout="wide")

# 화면 선택
page = st.sidebar.radio("메뉴", ["Todo 입력", "랜덤 뽑기", "Todo", "완료된 Todo"])

if page == "Todo 입력":
    st.title("Todo 입력")

    # 큰 텍스트 입력 필드
    content = st.text_area("Todo 입력", height=200)
    if st.button("등록"):
        if content.strip():
            created_at = datetime.datetime.now(pytz.utc).astimezone(kst)
            todos.insert_one(
                {
                    "content": content,
                    "date": "",
                    "completed": False,
                    "createdAt": created_at.isoformat(),
                }
            )
            st.success("등록 완료!")
            content = ""
            st.rerun()
        else:
            st.warning("내용을 입력하세요.")

    st.subheader("최근 추가된 Todo")
    items = list(todos.find({"completed": False}).sort("_id", -1))[:5]

    for item in items:
        created_at = datetime.datetime.fromisoformat(
            item.get("createdAt", datetime.datetime.utcnow().isoformat())
        ).astimezone(kst)
        with st.expander(
            f"{item['content']}"
        ):
            new_content = st.text_area(
                "내용 수정", item["content"], key=str(item["_id"])
            )
            res = todos.update_one(
                {"_id": item["_id"]}, {"$set": {"content": new_content}}
            )
            if res.modified_count > 0:
                st.success("수정 완료!")
                st.rerun()
            if st.button("삭제", key=f"delete_{item['_id']}"):
                todos.delete_one({"_id": item["_id"]})
                st.warning("삭제 완료!")
                st.rerun()

            created_at_date = st.date_input(
                "추가한 날짜 수정",
                created_at.date(),
                key=f"done_created_date_{item['_id']}",
            )
            if st.button(
                "추가한 날짜 변경", key=f"change_done_created_date_{item['_id']}"
            ):
                updated_created_at = datetime.datetime.combine(
                    created_at_date, created_at.time()
                ).astimezone(kst)
                todos.update_one(
                    {"_id": item["_id"]},
                    {"$set": {"createdAt": updated_created_at.isoformat()}},
                )
                st.success("추가한 날짜 변경됨!")
                st.rerun()

            completion_date = st.date_input("완료 날짜 입력", key=f"date_{item['_id']}")
            if st.button("완료 처리", key=f"done_{item['_id']}"):
                todos.update_one(
                    {"_id": item["_id"]},
                    {"$set": {"date": completion_date.isoformat(), "completed": True}},
                )
                st.success("완료 처리됨!")
                st.rerun()

elif page == "랜덤 뽑기":
    # choose random item
    st.title("랜덤 뽑기")
    items = list(todos.find({"completed": False}))
    button = st.button("랜덤 뽑기")
    if button:
        if items:
            random_item = random.choice(items)
            # Show random item
            st.success(f"🎉 {random_item['content']}")
        else:
            st.warning("Todo이 없습니다.")

elif page == "Todo":
    st.title("Todo")
    items = list(todos.find({"completed": False}).sort("_id", -1))

    for item in items:
        created_at = datetime.datetime.fromisoformat(
            item.get("createdAt", datetime.datetime.utcnow().isoformat())
        ).astimezone(kst)
        with st.expander(
            f"{item['content']}"
        ):
            new_content = st.text_area(
                "내용 수정", item["content"], key=str(item["_id"])
            )
            res = todos.update_one(
                {"_id": item["_id"]}, {"$set": {"content": new_content}}
            )
            if res.modified_count > 0:
                st.success("수정 완료!")
                st.rerun()
            if st.button("삭제", key=f"delete_{item['_id']}"):
                todos.delete_one({"_id": item["_id"]})
                st.warning("삭제 완료!")
                st.rerun()

            created_at_date = st.date_input(
                "추가한 날짜 수정",
                created_at.date(),
                key=f"done_created_date_{item['_id']}",
            )
            if st.button(
                "추가한 날짜 변경", key=f"change_done_created_date_{item['_id']}"
            ):
                updated_created_at = datetime.datetime.combine(
                    created_at_date, created_at.time()
                ).astimezone(kst)
                todos.update_one(
                    {"_id": item["_id"]},
                    {"$set": {"createdAt": updated_created_at.isoformat()}},
                )
                st.success("추가한 날짜 변경됨!")
                st.rerun()

            completion_date = st.date_input("완료 날짜 입력", key=f"date_{item['_id']}")
            if st.button("완료 처리", key=f"done_{item['_id']}"):
                todos.update_one(
                    {"_id": item["_id"]},
                    {"$set": {"date": completion_date.isoformat(), "completed": True}},
                )
                st.success("완료 처리됨!")
                st.rerun()

elif page == "완료된 Todo":
    st.title("완료된 Todo")
    done_items = list(todos.find({"completed": True}).sort("date", -1))

    for item in done_items:
        created_at = datetime.datetime.fromisoformat(
            item.get("createdAt", datetime.datetime.utcnow().isoformat())
        ).astimezone(kst)
        with st.expander(
            f"✅ {item['content']} (완료: {item['date']})"
        ):
            new_content = st.text_area(
                "내용 수정", item["content"], key=f"done_edit_{item['_id']}"
            )
            res = todos.update_one(
                {"_id": item["_id"]}, {"$set": {"content": new_content}}
            )
            if res.modified_count > 0:
                st.success("수정 완료!")
                st.rerun()
            if st.button("삭제", key=f"done_delete_{item['_id']}"):
                todos.delete_one({"_id": item["_id"]})
                st.warning("삭제 완료!")
                st.rerun()

            created_at_date = st.date_input(
                "추가한 날짜 수정",
                created_at.date(),
                key=f"done_created_date_{item['_id']}",
            )
            if st.button(
                "추가한 날짜 변경", key=f"change_done_created_date_{item['_id']}"
            ):
                updated_created_at = datetime.datetime.combine(
                    created_at_date, created_at.time()
                ).astimezone(kst)
                todos.update_one(
                    {"_id": item["_id"]},
                    {"$set": {"createdAt": updated_created_at.isoformat()}},
                )
                st.success("추가한 날짜 변경됨!")
                st.rerun()

            completion_date = st.date_input(
                "완료 날짜 수정", key=f"done_date_{item['_id']}"
            )
            if st.button("완료 날짜 변경", key=f"change_date_{item['_id']}"):
                todos.update_one(
                    {"_id": item["_id"]},
                    {"$set": {"date": completion_date.isoformat()}},
                )
                st.success("완료 날짜 변경됨!")
                st.rerun()

            if st.button("미완료 처리", key=f"undone_{item['_id']}"):
                todos.update_one(
                    {"_id": item["_id"]},
                    {"$set": {"date": "", "completed": False}},
                )
                st.success("미완료 처리됨!")
                st.rerun()
