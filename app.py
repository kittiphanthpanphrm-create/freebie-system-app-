import datetime
import os
import gspread
import pandas as pd
import streamlit as st
from google.oauth2.service_account import Credentials

st.set_page_config(
    page_title="Freebie & Stock Management (GSheets)", page_icon="🎁", layout="wide"
)

# --- CONFIG GOOGLE SHEETS ---
# แนะนำให้ผูกกับ st.secrets["gcp_service_account"] บน Streamlit Cloud
SHEET_NAME = "kathi_stock_db"  # เปลี่ยนชื่อ Google Sheet ให้ตรงกัน


@st.cache_resource
def get_gsheet_client():
  try:
    # อ่านจาก Streamlit Secrets
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds_dict = dict(st.secrets["gcp_service_account"])
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    client = gspread.authorize(creds)
    return client
  except Exception as e:
    st.error(
        f"❌ เชื่อมต่อ Google Sheets ไม่สำเร็จ (กรุณาตั้งค่า Secrets): {e}"
    )
    return None


def load_data_gsheets():
  client = get_gsheet_client()
  if client is None:
    return (
        pd.DataFrame(
            columns=["sku", "name", "qty", "min_qty", "location"]
        ),
        pd.DataFrame(
            columns=[
                "log_id",
                "วันที่",
                "SKU",
                "ชื่อสินค้า",
                "ชื่อล็อก",
                "จำนวนที่รับเข้า",
                "ไฟล์รูป",
            ]
        ),
        pd.DataFrame(
            columns=[
                "log_id",
                "วันที่",
                "เลขที่ออเดอร์",
                "SKU",
                "ชื่อสินค้า",
                "ชื่อล็อก",
                "จำนวนที่จ่ายออก",
            ]
        ),
    )

  sheet = client.open(SHEET_NAME)

  # Load Stock
  ws_stock = sheet.worksheet("stock")
  data_stock = ws_stock.get_all_records()
  df_stock = pd.DataFrame(data_stock)
  if df_stock.empty:
    df_stock = pd.DataFrame(columns=["sku", "name", "qty", "min_qty", "location"])
  else:
    df_stock["sku"] = df_stock["sku"].astype(str)
    df_stock["qty"] = pd.to_numeric(df_stock["qty"], errors="coerce").fillna(0)
    df_stock["min_qty"] = (
        pd.to_numeric(df_stock["min_qty"], errors="coerce").fillna(5)
    )

  # Load Log In
  ws_in = sheet.worksheet("log_in")
  data_in = ws_in.get_all_records()
  df_in = pd.DataFrame(data_in)
  if df_in.empty:
    df_in = pd.DataFrame(
        columns=[
            "log_id",
            "วันที่",
            "SKU",
            "ชื่อสินค้า",
            "ชื่อล็อก",
            "จำนวนที่รับเข้า",
            "ไฟล์รูป",
        ]
    )
  else:
    df_in["log_id"] = (
        pd.to_numeric(df_in["log_id"], errors="coerce").fillna(0)
    )
    df_in["จำนวนที่รับเข้า"] = (
        pd.to_numeric(df_in["จำนวนที่รับเข้า"], errors="coerce").fillna(0)
    )
    df_in["SKU"] = df_in["SKU"].astype(str)

  # Load Log Out
  ws_out = sheet.worksheet("log_out")
  data_out = ws_out.get_all_records()
  df_out = pd.DataFrame(data_out)
  if df_out.empty:
    df_out = pd.DataFrame(
        columns=[
            "log_id",
            "วันที่",
            "เลขที่ออเดอร์",
            "SKU",
            "ชื่อสินค้า",
            "ชื่อล็อก",
            "จำนวนที่จ่ายออก",
        ]
    )
  else:
    df_out["log_id"] = (
        pd.to_numeric(df_out["log_id"], errors="coerce").fillna(0)
    )
    df_out["จำนวนที่จ่ายออก"] = (
        pd.to_numeric(df_out["จำนวนที่จ่ายออก"], errors="coerce").fillna(0)
    )
    df_out["SKU"] = df_out["SKU"].astype(str)

  return df_stock, df_in, df_out


def save_to_gsheets(df_stock, df_in, df_out):
  client = get_gsheet_client()
  if client is None:
    return
  sheet = client.open(SHEET_NAME)

  def save_ws(ws_name, df):
    ws = sheet.worksheet(ws_name)
    ws.clear()
    if not df.empty:
      ws.update([df.columns.values.tolist()] + df.values.tolist())
    else:
      ws.update([df.columns.values.tolist()])

  save_ws("stock", df_stock)
  save_ws("log_in", df_in)
  save_ws("log_out", df_out)


df_stock, df_freebie_logs, df_out_logs = load_data_gsheets()

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; background-color: #F8FAFC; }
    h1 { font-weight: 800 !important; color: #0F172A; }
    h2, h3 { font-weight: 700 !important; color: #1E293B; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; background-color: transparent; padding-bottom: 10px; }
    .stTabs [data-baseweb="tab"] { height: 52px; border-radius: 14px; background-color: #FFFFFF; border: 1px solid #E2E8F0; padding: 0 24px; font-weight: 700 !important; color: #475569; }
    .stTabs [aria-selected="true"] { background-color: #4F46E5 !important; color: white !important; }
    div[data-testid="stVerticalBlock"] > div[style*="border: 1px solid"] { border-radius: 16px !important; border: 1px solid #E2E8F0 !important; background-color: #FFFFFF !important; padding: 16px; }
</style>
""", unsafe_allow_html=True)

st.title("🎁 ระบบจัดการสต็อกและของแถม (เชื่อมต่อ Google Sheets)")

tab1, tab2, tab3, tab4 = st.tabs(
    ["📊 สต็อกคงเหลือ", "📥 รับเข้า (IN)", "📤 จ่ายออก/แถม (OUT)", "📈 รายงาน"]
)

with tab1:
  st.subheader("📦 สต็อกคงเหลือ")
  if not df_stock.empty:
    st.dataframe(df_stock, use_container_width=True)
  else:
    st.info("ยังไม่มีข้อมูลสินค้า")

with tab2:
  st.subheader("📥 บันทึกรับเข้า / เพิ่ม SKU ใหม่")
  with st.form("form_in", clear_on_submit=True):
    target_sku = st.text_input("รหัส SKU", placeholder="SKU-001")
    target_name = st.text_input("ชื่อสินค้า", placeholder="ชื่อสินค้า")
    location_in = st.text_input("ชื่อล็อกจัดเก็บ", value="ล็อก A1")
    qty_in = st.number_input("จำนวนที่รับเข้า", min_value=1, value=10)

    if st.form_submit_button("💾 บันทึกรับเข้า", type="primary"):
      if target_sku and target_name:
        if target_sku not in df_stock["sku"].values:
          new_row = pd.DataFrame([{
              "sku": target_sku,
              "name": target_name,
              "qty": int(qty_in),
              "min_qty": 5,
              "location": location_in,
          }])
          df_stock = pd.concat([df_stock, new_row], ignore_index=True)
        else:
          idx = df_stock[df_stock["sku"] == target_sku].index[0]
          df_stock.loc[idx, "qty"] = int(df_stock.loc[idx, "qty"]) + int(
              qty_in
          )
          df_stock.loc[idx, "location"] = location_in

        current_lid = (
            int(
                pd.to_numeric(
                    df_freebie_logs["log_id"], errors="coerce"
                ).max()
            )
            + 1
            if not df_freebie_logs.empty
            and pd.notna(df_freebie_logs["log_id"].max())
            else 1
        )
        new_log = pd.DataFrame([{
            "log_id": current_lid,
            "วันที่": str(datetime.date.today()),
            "SKU": target_sku,
            "ชื่อสินค้า": target_name,
            "ชื่อล็อก": location_in,
            "จำนวนที่รับเข้า": int(qty_in),
            "ไฟล์รูป": "ไม่มีรูป",
        }])
        df_freebie_logs = pd.concat(
            [df_freebie_logs, new_log], ignore_index=True
        )

        save_to_gsheets(df_stock, df_freebie_logs, df_out_logs)
        st.success("✅ บันทึกและซิงค์ลง Google Sheets สำเร็จ!")
        st.rerun()

with tab3:
  st.subheader("📤 จ่ายออก / แจกตามบิล (OUT)")
  if not df_stock.empty:
    with st.form("form_out", clear_on_submit=True):
      order_ref = st.text_input("เลขที่ออเดอร์", value="POS-001")
      selected_item_out = st.selectbox(
          "เลือกสินค้า", (df_stock["sku"] + " | " + df_stock["name"]).tolist()
      )
      qty_out = st.number_input("จำนวนจ่ายออก", min_value=1, value=1)
      if st.form_submit_button("ยืนยันจ่ายออก", type="primary"):
        target_sku_out = selected_item_out.split(" | ")[0]
        idx = df_stock[df_stock["sku"] == target_sku_out].index[0]
        current_q = int(df_stock.loc[idx, "qty"])
        if current_q >= qty_out:
          df_stock.loc[idx, "qty"] = current_q - int(qty_out)
          current_lid = (
              int(
                  pd.to_numeric(df_out_logs["log_id"], errors="coerce").max()
              )
              + 1
              if not df_out_logs.empty
              and pd.notna(df_out_logs["log_id"].max())
              else 1
          )
          new_out_log = pd.DataFrame([{
              "log_id": current_lid,
              "วันที่": str(datetime.date.today()),
              "เลขที่ออเดอร์": order_ref,
              "SKU": target_sku_out,
              "ชื่อสินค้า": df_stock.loc[idx, "name"],
              "ชื่อล็อก": df_stock.loc[idx, "location"],
              "จำนวนที่จ่ายออก": int(qty_out),
          }])
          df_out_logs = pd.concat([df_out_logs, new_out_log], ignore_index=True)
          save_to_gsheets(df_stock, df_freebie_logs, df_out_logs)
          st.success("✅ ตัดสต็อกและซิงค์ Google Sheets สำเร็จ!")
          st.rerun()
        else:
          st.error("❌ สต็อกไม่พอ!")
  else:
    st.warning("ยังไม่มีสินค้า")

with tab4:
  st.subheader("📈 รายงาน")
  st.markdown("### 📥 รับเข้า")
  st.dataframe(df_freebie_logs, use_container_width=True)
  st.markdown("### 📤 จ่ายออก")
  st.dataframe(df_out_logs, use_container_width=True)
