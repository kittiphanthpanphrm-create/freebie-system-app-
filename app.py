import streamlit as st
import pandas as pd
import datetime
import os

st.set_page_config(
    page_title="Freebie & Stock Management",
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
        df_in = pd.DataFrame(columns=["log_id", "วันที่", "SKU", "ชื่อสินค้า", "ชื่อล็อก", "จำนวนที่รับเข้า", "file_obj", "ไฟล์รูป"])
        
    if os.path.exists(LOG_OUT_FILE):
        df_out = pd.read_csv(LOG_OUT_FILE, dtype=str)
        df_out["log_id"] = pd.to_numeric(df_out["log_id"], errors="coerce").fillna(0)
        df_out["จำนวนที่จ่ายออก"] = pd.to_numeric(df_out["จำนวนที่จ่ายออก"], errors="coerce").fillna(0)
    else:
        df_out = pd.DataFrame(columns=["log_id", "วันที่", "เลขที่ออเดอร์", "SKU", "ชื่อสินค้า", "ชื่อล็อก", "จำนวนที่จ่ายออก"])
        
    return df_stock, df_in, df_out

df_stock, df_freebie_logs, df_out_logs = load_data()

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
        background-color: #F8FAFC;
    }
    h1 { font-weight: 800 !important; color: #0F172A; }
    h2, h3 { font-weight: 700 !important; color: #1E293B; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; background-color: transparent; padding-bottom: 10px; }
    .stTabs [data-baseweb="tab"] {
        height: 52px; border-radius: 14px; background-color: #FFFFFF;
        border: 1px solid #E2E8F0; padding: 0 24px; font-size: 1rem !important;
        font-weight: 700 !important; color: #475569; box-shadow: 0 1px 3px rgba(0,0,0,0.02);
    }
    .stTabs [aria-selected="true"] {
        background-color: #4F46E5 !important; color: white !important; border-color: #4F46E5 !important;
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.25);
    }
    div[data-testid="stVerticalBlock"] > div[style*="border: 1px solid"] {
        border-radius: 16px !important; border: 1px solid #E2E8F0 !important;
        background-color: #FFFFFF !important; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.03);
        padding: 16px;
    }
    div[data-testid="stMetricValue"] { font-size: 1.8rem !important; font-weight: 800 !important; color: #0F172A; }
    div[data-testid="stMetricLabel"] { font-size: 0.85rem !important; font-weight: 600 !important; color: #64748B; }
    .stButton button { border-radius: 12px !important; font-weight: 700 !important; padding: 0.5rem 1rem; }
    .stButton button[kind="primary"] { background-color: #4F46E5 !important; border: none; }
</style>
""", unsafe_allow_html=True)

st.title("🎁 ระบบจัดการสต็อกและของแถม")

with st.sidebar:
    st.markdown("### ⚙️ ตั้งค่าระบบ")
    with st.expander("🔐 ตั้งค่ารีเซ็ตข้อมูล"):
        reset_pin = st.text_input("กรอกรหัสผ่าน", type="password", key="sidebar_reset_pin", placeholder="••••")
        if st.button("🗑️ รีเซ็ต/ล้างข้อมูลทั้งหมด", use_container_width=True):
            if reset_pin == "1234":
                if os.path.exists(STOCK_FILE): os.remove(STOCK_FILE)
                if os.path.exists(LOG_IN_FILE): os.remove(LOG_IN_FILE)
                if os.path.exists(LOG_OUT_FILE): os.remove(LOG_OUT_FILE)
                st.sidebar.success("✅ รีเซ็ตระบบสำเร็จ")
                st.rerun()
            else:
                st.sidebar.error("❌ รหัสผ่านไม่ถูกต้อง (กรุณากรอก 1234)")
                
    with st.expander("💾 สำรอง / กู้คืนข้อมูล (Backup)"):
        if os.path.exists(STOCK_FILE):
            with open(STOCK_FILE, "rb") as f:
                st.download_button("⬇️ โหลด Stock.csv", f, file_name="stock_data.csv", use_container_width=True)
        if os.path.exists(LOG_IN_FILE):
            with open(LOG_IN_FILE, "rb") as f:
                st.download_button("⬇️ โหลด Log_IN.csv", f, file_name="log_in_data.csv", use_container_width=True)
        if os.path.exists(LOG_OUT_FILE):
            with open(LOG_OUT_FILE, "rb") as f:
                st.download_button("⬇️ โหลด Log_OUT.csv", f, file_name="log_out_data.csv", use_container_width=True)
        
        st.divider()
        up_stock = st.file_uploader("⬆️ กู้คืน Stock.csv", type=["csv"], key="restore_stock")
        if up_stock is not None:
            with open(STOCK_FILE, "wb") as f: f.write(up_stock.getbuffer())
            st.success("✅ กู้คืน Stock สำเร็จ รีเฟรชหน้าเว็บ 1 ครั้ง")
            
        up_in = st.file_uploader("⬆️ กู้คืน Log_IN.csv", type=["csv"], key="restore_in")
        if up_in is not None:
            with open(LOG_IN_FILE, "wb") as f: f.write(up_in.getbuffer())
            st.success("✅ กู้คืน Log_IN สำเร็จ รีเฟรชหน้าเว็บ 1 ครั้ง")

tab1, tab2, tab3, tab4 = st.tabs(["📊 สต็อกคงเหลือ", "📥 รับเข้า (IN)", "📤 จ่ายออก/แถม (OUT)", "📈 รายงานเคลื่อนไหว"])

with tab1:
    st.subheader("📦 สต็อกคงเหลือและรูปภาพล่าสุด")
    if not df_stock.empty:
        low_stock = df_stock[pd.to_numeric(df_stock["qty"], errors="coerce") <= pd.to_numeric(df_stock["min_qty"], errors="coerce")]
        if not low_stock.empty:
            st.warning(f"⚠️ มีสินค้าใกล้หมด {len(low_stock)} รายการ กรุณาเติมสต็อก!")
        
        for idx, row in df_stock.iterrows():
            with st.container(border=True):
                c_img, c_info = st.columns([1.5, 3.5], gap="medium")
                with c_img:
                    img_displayed = False
                    if not df_freebie_logs.empty:
                        sub_l = df_freebie_logs[df_freebie_logs["SKU"] == str(row["sku"])]
                        for _, l_row in sub_l.iloc[::-1].iterrows():
                            if "file_obj" in l_row and pd.notna(l_row["file_obj"]) and str(l_row["file_obj"]) != "None" and os.path.exists(str(l_row["file_obj"])):
                                st.image(str(l_row["file_obj"]), width=130, caption="ภาพรับเข้าล่าสุด")
                                img_displayed = True
                                break
                    if not img_displayed:
                        st.info("ไม่มีรูปถ่าย")
                        
                with c_info:
                    st.markdown(f"### 🏷️ {row['name']} `[{row['sku']}]`")
                    col_i1, col_i2, col_i3, col_i4 = st.columns(4)
                    col_i1.metric("คงเหลือ", f"{row['qty']} ชิ้น")
                    col_i2.metric("จุดแจ้งเตือน", f"{row['min_qty']} ชิ้น")
                    col_i3.metric("พิกัดล็อก", row["location"])
                    
                    if not df_freebie_logs.empty and str(row["sku"]) in df_freebie_logs["SKU"].values:
                        last_log = df_freebie_logs[df_freebie_logs["SKU"] == str(row["sku"])].iloc[-1]
                        col_i4.metric("รับล่าสุด", f"+{last_log['จำนวนที่รับเข้า']}", delta=f"วันที่ {last_log['วันที่']}")
                    else:
                        col_i4.metric("รับล่าสุด", "ยังไม่มีข้อมูล")
    else:
        st.info("✨ ยังไม่มีข้อมูลสินค้า เพิ่มได้ที่แท็บรับเข้า")

with tab2:
    st.subheader("📥 บันทึกรับเข้า / เพิ่ม SKU ใหม่")
    is_new_sku = st.checkbox("➕ เพิ่มเป็น SKU ใหม่", value=df_stock.empty)
    
    target_sku = ""
    target_name = ""
    default_loc = "ล็อก A1"
    
    if is_new_sku or df_stock.empty:
        target_sku = st.text_input("รหัส SKU ใหม่*", placeholder="SKU-001")
        target_name = st.text_input("ชื่อสินค้า/ของแถม*", placeholder="ชื่อสินค้า")
        default_loc = st.text_input("ชื่อล็อกจัดเก็บ", value="ล็อก A1")
    else:
        display_list = (df_stock["sku"].astype(str) + " | " + df_stock["name"].astype(str)).tolist()
        selected_item = st.selectbox("เลือก SKU / ชื่อสินค้า", display_list)
        if selected_item:
            parts = selected_item.split(" | ")
            target_sku = parts[0]
            target_name = parts if len(parts) > 1 else ""
            default_loc = df_stock[df_stock["sku"] == target_sku]["location"].values[0]
            
    with st.form("form_in", clear_on_submit=False):
        date_in = st.date_input("วันที่รับเข้า", value=datetime.date.today())
        location_in = st.text_input("ชื่อล็อกที่จัดเก็บ", value=default_loc)
        qty_in = st.number_input("จำนวนที่รับเข้า", min_value=1, value=10)
        uploaded_file = st.file_uploader("📸 รูปถ่ายสินค้า (คอม / มือถือ)", type=["jpg", "jpeg", "png"])
        
        submit_in = st.form_submit_button("💾 บันทึกรับเข้า", type="primary", use_container_width=True)
        
        if submit_in:
            if not target_sku or not target_name:
                st.error("❌ กรุณากรอกรหัส SKU และชื่อสินค้าให้ครบถ้วน")
            else:
                target_sku = str(target_sku)
                if target_sku not in df_stock["sku"].astype(str).values:
                    new_row = pd.DataFrame([{
                        "sku": target_sku, "name": target_name, "qty": int(qty_in), "min_qty": 5, "location": location_in
                    }])
                    df_stock = pd.concat([df_stock, new_row], ignore_index=True)
                else:
                    idx = df_stock[df_stock["sku"].astype(str) == target_sku].index[0]
                    df_stock.loc[idx, "qty"] = int(df_stock.loc[idx, "qty"]) + int(qty_in)
                    df_stock.loc[idx, "location"] = location_in
                
                file_name = uploaded_file.name if uploaded_file is not None else "ไม่มีรูป"
                file_path_save = None
                if uploaded_file is not None:
                    os.makedirs("uploads", exist_ok=True)
                    file_path_save = os.path.join("uploads", f"{int(datetime.datetime.now().timestamp())}_{uploaded_file.name}")
                    with open(file_path_save, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                
                current_lid = int(pd.to_numeric(df_freebie_logs["log_id"], errors="coerce").max()) + 1 if not df_freebie_logs.empty and pd.notna(df_freebie_logs["log_id"].max()) else 1
                new_log = pd.DataFrame([{
                    "log_id": current_lid,
                    "วันที่": str(date_in),
                    "SKU": target_sku,
                    "ชื่อสินค้า": target_name,
                    "ชื่อล็อก": location_in,
                    "จำนวนที่รับเข้า": int(qty_in),
                    "file_obj": file_path_save,
                    "ไฟล์รูป": file_name
                }])
                df_freebie_logs = pd.concat([df_freebie_logs, new_log], ignore_index=True)
                
                df_stock.to_csv(STOCK_FILE, index=False)
                df_freebie_logs.to_csv(LOG_IN_FILE, index=False)
                
                st.success(f"✅ บันทึกรับเข้า '{target_name}' จำนวน +{qty_in} ชิ้นเรียบร้อย!")
                st.rerun()

with tab3:
    st.subheader("📤 จ่ายออก / แจกตามบิล (OUT)")
    if df_stock.empty:
        st.warning("⚠️ ยังไม่มีสินค้าในระบบ")
    else:
        with st.form("form_out", clear_on_submit=True):
            order_ref = st.text_input("เลขที่ออเดอร์ / Order Ref", placeholder="POS-2026-001")
            display_list_out = (df_stock["sku"].astype(str) + " | " + df_stock["name"].astype(str)).tolist()
            selected_item_out = st.selectbox("เลือกสินค้าจ่ายออก", display_list_out)
            if selected_item_out:
                parts_out = selected_item_out.split(" | ")
                target_sku_out = parts_out[0]
                target_name_out = parts_out if len(parts_out) > 1 else ""
                default_loc_out = df_stock[df_stock["sku"].astype(str) == target_sku_out]["location"].values[0]
            else:
                target_sku_out, target_name_out, default_loc_out = "", "", ""
                
            date_out = st.date_input("วันที่จ่ายออก", value=datetime.date.today())
            location_out = st.text_input("ชื่อล็อก", value=default_loc_out)
            qty_out = st.number_input("จำนวนที่จ่ายออก", min_value=1, value=1)
            
            submit_out = st.form_submit_button("ยืนยันตัดสต็อก", type="primary", use_container_width=True)
            if submit_out and target_sku_out:
                idx = df_stock[df_stock["sku"].astype(str) == target_sku_out].index[0]
                current_q = int(df_stock.loc[idx, "qty"])
                if current_q >= qty_out:
                    df_stock.loc[idx, "qty"] = current_q - int(qty_out)
                    df_stock.loc[idx, "location"] = location_out
                    
                    current_lid = int(pd.to_numeric(df_out_logs["log_id"], errors="coerce").max()) + 1 if not df_out_logs.empty and pd.notna(df_out_logs["log_id"].max()) else 1
                    new_out_log = pd.DataFrame([{
                        "log_id": current_lid,
                        "วันที่": str(date_out),
                        "เลขที่ออเดอร์": order_ref,
                        "SKU": target_sku_out,
                        "ชื่อสินค้า": target_name_out,
                        "ชื่อล็อก": location_out,
                        "จำนวนที่จ่ายออก": int(qty_out)
                    }])
                    df_out_logs = pd.concat([df_out_logs, new_out_log], ignore_index=True)
                    
                    df_stock.to_csv(STOCK_FILE, index=False)
                    df_out_logs.to_csv(LOG_OUT_FILE, index=False)
                    
                    st.success(f"✅ จ่ายออก '{target_name_out}' เรียบร้อย!")
                    st.rerun()
                else:
                    st.error("❌ สต็อกไม่พอจ่ายออก!")

with tab4:
    st.subheader("📈 รายงานสรุปการเคลื่อนไหว")
    c_f1, c_f2 = st.columns(2)
    with c_f1: rep_start_date = st.date_input("ตั้งแต่วันที่", value=datetime.date.today() - datetime.timedelta(days=30))
    with c_f2: rep_end_date = st.date_input("ถึงวันที่", value=datetime.date.today())
    
    st.markdown("---")
    r_col1, r_col2 = st.columns(2)
    with r_col1:
        st.markdown("### 📥 รายการรับเข้า (IN)")
        if not df_freebie_logs.empty:
            df_freebie_logs["dt_parsed"] = pd.to_datetime(df_freebie_logs["วันที่"], errors="coerce").dt.date
            filt_in = df_freebie_logs[(df_freebie_logs["dt_parsed"] >= rep_start_date) & (df_freebie_logs["dt_parsed"] <= rep_end_date)]
            st.metric("รวมรับเข้า", f"+{filt_in['จำนวนที่รับเข้า'].sum() if not filt_in.empty else 0} ชิ้น")
            st.dataframe(filt_in, use_container_width=True, hide_index=True)
    with r_col2:
        st.markdown("### 📤 รายการจ่ายออก (OUT)")
        if not df_out_logs.empty:
            df_out_logs["dt_parsed"] = pd.to_datetime(df_out_logs["วันที่"], errors="coerce").dt.date
            filt_out = df_out_logs[(df_out_logs["dt_parsed"] >= rep_start_date) & (df_out_logs["dt_parsed"] <= rep_end_date)]
            st.metric("รวมจ่ายออก", f"-{filt_out['จำนวนที่จ่ายออก'].sum() if not filt_out.empty else 0} ชิ้น")
            st.dataframe(filt_out, use_container_width=True, hide_index=True)
