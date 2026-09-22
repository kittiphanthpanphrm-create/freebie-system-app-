import streamlit as st
import pandas as pd
import datetime
import os

st.set_page_config(
    page_title="Kathi Freebie POS",
    page_icon="🎁",
    layout="wide"
)

STOCK_FILE = "stock_data.csv"
LOG_IN_FILE = "log_in_data.csv"
LOG_OUT_FILE = "log_out_data.csv"

def load_data():
    if os.path.exists(STOCK_FILE):
        df_stock = pd.read_csv(STOCK_FILE, dtype=str)
        df_stock["qty"] = pd.to_numeric(df_stock["qty"], errors="coerce").fillna(0)
        df_stock["min_qty"] = pd.to_numeric(df_stock["min_qty"], errors="coerce").fillna(5)
    else:
        df_stock = pd.DataFrame(columns=["sku", "name", "qty", "min_qty", "location"])
        
    if os.path.exists(LOG_IN_FILE):
        df_in = pd.read_csv(LOG_IN_FILE, dtype=str)
        df_in["log_id"] = pd.to_numeric(df_in["log_id"], errors="coerce").fillna(0)
        df_in["จำนวนที่รับเข้า"] = pd.to_numeric(df_in["จำนวนที่รับเข้า"], errors="coerce").fillna(0)
        if "file_obj" not in df_in.columns:
            df_in["file_obj"] = None
    else:
        df_in = pd.DataFrame(columns=["log_id", "วันที่", "SKU", "ชื่อของแถม", "ชื่อล็อก", "จำนวนที่รับเข้า", "file_obj", "ไฟล์รูป"])
        
    if os.path.exists(LOG_OUT_FILE):
        df_out = pd.read_csv(LOG_OUT_FILE, dtype=str)
        df_out["log_id"] = pd.to_numeric(df_out["log_id"], errors="coerce").fillna(0)
        df_out["จำนวนที่แถมไป"] = pd.to_numeric(df_out["จำนวนที่แถมไป"], errors="coerce").fillna(0)
    else:
        df_out = pd.DataFrame(columns=["log_id", "วันที่", "เลขที่ออเดอร์", "SKU", "ชื่อของแถม", "ชื่อล็อก", "จำนวนที่แถมไป"])
        
    return df_stock, df_in, df_out

df_stock, df_freebie_logs, df_out_logs = load_data()

st.title("🎁 ระบบจัดการสต็อกของแถม (Kathi Pet Shop)")

tab1, tab2, tab3 = st.tabs(["📊 สต็อกคงเหลือ", "📥 รับเข้าของแถม (IN)", "📤 ตัดจ่ายตามบิล (OUT)"])

with tab1:
    st.subheader("📦 สต็อกคงเหลือ")
    if not df_stock.empty:
        st.dataframe(df_stock, use_container_width=True)
    else:
        st.info("ยังไม่มีสินค้า")

with tab2:
    st.subheader("📥 บันทึกรับเข้าของแถม")
    with st.form("form_in"):
        sku_in = st.text_input("SKU ของแถม", value="FB-01")
        name_in = st.text_input("ชื่อของแถม", value="ขนมแมวเลีย")
        loc_in = st.text_input("พิกัดล็อก", value="A1")
        qty_in = st.number_input("จำนวน", min_value=1, value=10)
        if st.form_submit_button("บันทึกรับเข้า"):
            new_row = pd.DataFrame([{"sku": sku_in, "name": name_in, "qty": qty_in, "min_qty": 5, "location": loc_in}])
            df_stock = pd.concat([df_stock, new_row], ignore_index=True)
            df_stock.to_csv(STOCK_FILE, index=False)
            st.success("บันทึกสำเร็จ!")
            st.rerun()

with tab3:
    st.subheader("📤 ตัดจ่ายตามบิล")
    if not df_stock.empty:
        with st.form("form_out"):
            ord_ref = st.text_input("เลขที่ออเดอร์", value="POS-001")
            sku_out = st.selectbox("เลือก SKU", df_stock["sku"].tolist())
            qty_out = st.number_input("จำนวนแจก", min_value=1, value=1)
            if st.form_submit_button("ยืนยันตัดสต็อก"):
                idx = df_stock[df_stock["sku"] == sku_out].index[0]
                df_stock.loc[idx, "qty"] = int(df_stock.loc[idx, "qty"]) - qty_out
                df_stock.to_csv(STOCK_FILE, index=False)
                st.success("ตัดสต็อกสำเร็จ!")
                st.rerun()
    else:
        st.warning("ยังไม่มีสินค้า")
