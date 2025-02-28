import os
import streamlit as st
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")

client = MongoClient(MONGO_URI, server_api=ServerApi("1"))
db = client[DB_NAME]
todos = db[COLLECTION_NAME]

st.set_page_config(page_title="TodoShare", layout="wide")

# 화면 선택
page = st.sidebar.radio("메뉴", ["할 일 입력", "완료된 할 일"])

if page == "할 일 입력":
    st.title("Todo 입력")

    # 큰 텍스트 입력 필드
    content = st.text_area("할 일 입력", height=200)
    if st.button("등록"):
        if content.strip():
            todos.insert_one({"content": content, "date": "", "completed": False})
            st.success("등록 완료!")
            st.rerun()
        else:
            st.warning("내용을 입력하세요.")

    st.subheader("📌 현재 진행 중인 Todo")
    items = list(todos.find({"completed": False}).sort("_id", 1))

    for item in items:
        with st.expander(item["content"][:50] + "..." if len(item["content"]) > 50 else item["content"]):
            new_content = st.text_area(
                "내용 수정", item["content"], key=str(item["_id"])
            )
            res = todos.update_one({"_id": item["_id"]}, {"$set": {"content": new_content}})
            if res.modified_count > 0:
                st.success("수정 완료!")
                st.rerun()
            # if st.button("수정", key=f"edit_{item['_id']}"):
            #     todos.update_one(
            #         {"_id": item["_id"]}, {"$set": {"content": new_content}}
            #     )
            #     st.success("수정 완료!")
            #     st.rerun()
            if st.button("삭제", key=f"delete_{item['_id']}"):
                todos.delete_one({"_id": item["_id"]})
                st.warning("삭제 완료!")
                st.rerun()

            completion_date = st.date_input("완료 날짜 입력", key=f"date_{item['_id']}")
            if st.button("완료 처리", key=f"done_{item['_id']}"):
                todos.update_one(
                    {"_id": item["_id"]},
                    {"$set": {"date": completion_date.isoformat(), "completed": True}},
                )
                st.success("완료 처리됨!")
                st.rerun()

elif page == "완료된 할 일":
    st.title("완료된 Todo 목록")
    done_items = list(todos.find({"completed": True}).sort("date", -1))

    for item in done_items:
        with st.expander(f"✅ {item['content']} (완료: {item['date']})"):
            new_content = st.text_area(
                "내용 수정", item["content"], key=f"done_edit_{item['_id']}"
            )
            res = todos.update_one({"_id": item["_id"]}, {"$set": {"content": new_content}})
            if res.modified_count > 0:
                st.success("수정 완료!")
                st.rerun()
            # if st.button("수정", key=f"done_edit_btn_{item['_id']}"):
            #     todos.update_one(
            #         {"_id": item["_id"]}, {"$set": {"content": new_content}}
            #     )
            #     st.success("수정 완료!")
            #     st.rerun()
            if st.button("삭제", key=f"done_delete_{item['_id']}"):
                todos.delete_one({"_id": item["_id"]})
                st.warning("삭제 완료!")
                st.rerun()

            if st.button("미완료 처리", key=f"undone_{item['_id']}"):
                todos.update_one(
                    {"_id": item["_id"]},
                    {"$set": {"date": "", "completed": False}},
                )
                st.success("미완료 처리됨!")
                st.rerun()
