import datetime
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Kathi Freebie POS", page_icon="🎁", layout="wide")

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

st.title("🎁 ระบบจัดการสต็อกของแถม (Google Sheets Persistent)")


# โหลดข้อมูลจาก Google Sheets
@st.cache_data(ttl=2)
def load_gsheets():
  try:
    conn = st.connection("gsheets", type="gsheets")
    df_stock = conn.read(worksheet="stock", ttl=1)
    df_in = conn.read(worksheet="log_in", ttl=1)
    df_out = conn.read(worksheet="log_out", ttl=1)

    # Clean DataFrame format
    if df_stock.empty or "sku" not in df_stock.columns:
      df_stock = pd.DataFrame(
          columns=["sku", "name", "qty", "min_qty", "location"]
      )
    else:
      df_stock["qty"] = pd.to_numeric(df_stock["qty"], errors="coerce").fillna(
          0
      )
      df_stock["min_qty"] = pd.to_numeric(
          df_stock["min_qty"], errors="coerce"
      ).fillna(5)

    if df_in.empty or "log_id" not in df_in.columns:
      df_in = pd.DataFrame(
          columns=[
              "log_id",
              "วันที่",
              "SKU",
              "ชื่อของแถม",
              "ชื่อล็อก",
              "จำนวนที่รับเข้า",
              "ไฟล์รูป",
          ]
      )
    else:
      df_in["log_id"] = pd.to_numeric(
          df_in["log_id"], errors="coerce"
      ).fillna(0)
      df_in["จำนวนที่รับเข้า"] = pd.to_numeric(
          df_in["จำนวนที่รับเข้า"], errors="coerce"
      ).fillna(0)
      if "file_obj" not in df_in.columns:
        df_in["file_obj"] = None

    if df_out.empty or "log_id" not in df_out.columns:
      df_out = pd.DataFrame(
          columns=[
              "log_id",
              "วันที่",
              "เลขที่ออเดอร์",
              "SKU",
              "ชื่อของแถม",
              "ชื่อล็อก",
              "จำนวนที่แถมไป",
          ]
      )
    else:
      df_out["log_id"] = pd.to_numeric(
          df_out["log_id"], errors="coerce"
      ).fillna(0)
      df_out["จำนวนที่แถมไป"] = pd.to_numeric(
          df_out["จำนวนที่แถมไป"], errors="coerce"
      ).fillna(0)

    return df_stock, df_in, df_out
  except Exception as e:
    st.error(
        f"⚠️ กรุณาตั้งค่า Google Sheets Secrets ใน Streamlit Cloud ก่อนใช้งาน:"
        f" {e}"
    )
    return (
        pd.DataFrame(columns=["sku", "name", "qty", "min_qty", "location"]),
        pd.DataFrame(
            columns=[
                "log_id",
                "วันที่",
                "SKU",
                "ชื่อของแถม",
                "ชื่อล็อก",
                "จำนวนที่รับเข้า",
                "file_obj",
                "ไฟล์รูป",
            ]
        ),
        pd.DataFrame(
            columns=[
                "log_id",
                "วันที่",
                "เลขที่ออเดอร์",
                "SKU",
                "ชื่อของแถม",
                "ชื่อล็อก",
                "จำนวนที่แถมไป",
            ]
        ),
    )


def save_gsheets(worksheet_name, df):
  try:
    conn = st.connection("gsheets", type="gsheets")
    conn.update(worksheet=worksheet_name, data=df)
    st.cache_data.clear()
  except Exception as e:
    st.error(f"❌ บันทึก Google Sheets ไม่สำเร็จ: {e}")


df_stock, df_freebie_logs, df_out_logs = load_gsheets()

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 สต็อกคงเหลือ",
    "📥 รับเข้าของแถม (IN)",
    "📤 ตัดจ่ายตามบิล (OUT)",
    "📈 รายงานเคลื่อนไหว (Report)",
])

with tab1:
  st.subheader("📦 สต็อกคงเหลือ")
  if not df_stock.empty and len(df_stock) > 0:
    for idx, row in df_stock.iterrows():
      with st.container(border=True):
        st.markdown(f"### 🏷️ {row.get('name', '')} `[{row.get('sku', '')}]`")
        col_i1, col_i2, col_i3 = st.columns(3)
        col_i1.metric("สต็อกคงเหลือ", f"{row.get('qty', 0)} ชิ้น")
        col_i2.metric("จุดแจ้งเตือนต่ำ", f"{row.get('min_qty', 5)} ชิ้น")
        col_i3.metric("พิกัดล็อก", row.get("location", "-"))
  else:
    st.info("✨ ยังไม่มีข้อมูลสินค้าใน Google Sheets")

with tab2:
  st.subheader("📥 บันทึกรับเข้าของแถม / เพิ่ม SKU ใหม่")
  is_new_sku = st.checkbox(
      "➕ เพิ่มเป็น SKU ใหม่ / สินค้าใหม่",
      value=True if df_stock.empty else False,
  )

  target_sku = ""
  target_name = ""
  default_loc = "ล็อก A1"

  if is_new_sku or df_stock.empty:
    target_sku = st.text_input("รหัส SKU ใหม่*", placeholder="FB-NEW-01")
    target_name = st.text_input("ชื่อสินค้า/ของแถม*", placeholder="ชามข้าวแมว")
    default_loc = st.text_input("ชื่อล็อกจัดเก็บ", value="ล็อก A1")
  else:
    display_list = (
        df_stock["sku"].astype(str) + " | " + df_stock["name"].astype(str)
    ).tolist()
    selected_item = st.selectbox("เลือก SKU / ชื่อของแถม", display_list)
    if selected_item:
      target_sku = selected_item.split(" | ")[0]
      target_name = selected_item.split(" | ")[1]
      default_loc = df_stock[df_stock["sku"] == target_sku][
          "location"
      ].values[0]

  with st.form("form_in", clear_on_submit=False):
    date_in = st.date_input("วันที่รับเข้า", value=datetime.date.today())
    location_in = st.text_input("ชื่อล็อกที่จัดเก็บของแถม", value=default_loc)
    qty_in = st.number_input("จำนวนที่รับเข้า", min_value=1, value=10)
    uploaded_file = st.file_uploader(
        "📸 รูปถ่ายสินค้า (คอม / มือถือ)", type=["jpg", "jpeg", "png"]
    )
    submit_in = st.form_submit_button(
        "💾 บันทึกรับเข้าลง Google Sheets", type="primary", use_container_width=True
    )

    if submit_in:
      if not target_sku or not target_name:
        st.error("❌ กรุณากรอกรหัส SKU และชื่อสินค้าให้ครบถ้วน")
      else:
        target_sku = str(target_sku)
        file_name = (
            uploaded_file.name if uploaded_file is not None else "ไม่มีรูป"
        )

        if target_sku not in df_stock["sku"].astype(str).values:
          new_row = pd.DataFrame([{
              "sku": target_sku,
              "name": target_name,
              "qty": int(qty_in),
              "min_qty": 5,
              "location": location_in,
          }])
          df_stock = pd.concat([df_stock, new_row], ignore_index=True)
        else:
          idx = df_stock[df_stock["sku"].astype(str) == target_sku].index[0]
          df_stock.loc[idx, "qty"] = int(df_stock.loc[idx, "qty"]) + int(qty_in)
          df_stock.loc[idx, "location"] = location_in

        current_lid = (
            int(
                pd.to_numeric(df_freebie_logs["log_id"], errors="coerce").max()
            )
            + 1
            if not df_freebie_logs.empty
            and pd.notna(df_freebie_logs["log_id"].max())
            else 1
        )
        new_log = pd.DataFrame([{
            "log_id": current_lid,
            "วันที่": str(date_in),
            "SKU": target_sku,
            "ชื่อของแถม": target_name,
            "ชื่อล็อก": location_in,
            "จำนวนที่รับเข้า": int(qty_in),
            "file_obj": None,
            "ไฟล์รูป": file_name,
        }])
        df_freebie_logs = pd.concat(
            [df_freebie_logs, new_log], ignore_index=True
        )

        save_gsheets("stock", df_stock)
        save_gsheets("log_in", df_freebie_logs)
        st.success("✅ บันทึกข้อมูลลง Google Sheets เรียบร้อยถาวร!")
        st.rerun()

with tab3:
  st.subheader("📤 ตัดจ่ายตามบิล (OUT)")
  if df_stock.empty:
    st.warning("⚠️ ยังไม่มีสินค้าในระบบ")
  else:
    with st.form("form_out", clear_on_submit=True):
      order_ref = st.text_input(
          "เลขที่ออเดอร์ / Order Ref", placeholder="POS-20260901-001"
      )
      display_list_out = (
          df_stock["sku"].astype(str) + " | " + df_stock["name"].astype(str)
      ).tolist()
      selected_item_out = st.selectbox(
          "เลือก SKU / ชื่อของแถม", display_list_out
      )
      target_sku_out, target_name_out, default_loc_out = "", "", ""
      if selected_item_out:
        target_sku_out = selected_item_out.split(" | ")[0]
        target_name_out = selected_item_out.split(" | ")[1]
        default_loc_out = df_stock[
            df_stock["sku"].astype(str) == target_sku_out
        ]["location"].values[0]

      date_out = st.date_input("วันที่ตัดจ่าย", value=datetime.date.today())
      location_out = st.text_input(
          "ชื่อล็อกที่จัดของแถม", value=default_loc_out
      )
      qty_out = st.number_input("จำนวนที่แถมไป", min_value=1, value=1)
      submit_out = st.form_submit_button(
          "ยืนยันตัดสต็อกลง Google Sheets",
          type="primary",
          use_container_width=True,
      )

      if submit_out and target_sku_out:
        idx = df_stock[df_stock["sku"].astype(str) == target_sku_out].index[0]
        current_q = int(df_stock.loc[idx, "qty"])
        if current_q >= qty_out:
          df_stock.loc[idx, "qty"] = current_q - int(qty_out)
          df_stock.loc[idx, "location"] = location_out

          current_lid = (
              int(pd.to_numeric(df_out_logs["log_id"], errors="coerce").max())
              + 1
              if not df_out_logs.empty
              and pd.notna(df_out_logs["log_id"].max())
              else 1
          )
          new_out_log = pd.DataFrame([{
              "log_id": current_lid,
              "วันที่": str(date_out),
              "เลขที่ออเดอร์": order_ref,
              "SKU": target_sku_out,
              "ชื่อของแถม": target_name_out,
              "ชื่อล็อก": location_out,
              "จำนวนที่แถมไป": int(qty_out),
          }])
          df_out_logs = pd.concat([df_out_logs, new_out_log], ignore_index=True)

          save_gsheets("stock", df_stock)
          save_gsheets("log_out", df_out_logs)
          st.success("✅ ตัดจ่ายบันทึกทับใน Google Sheets เรียบร้อย!")
          st.rerun()
        else:
          st.error("❌ สต็อกไม่พอแจก!")

with tab4:
  st.subheader("📈 รายงานสรุปการเคลื่อนไหว")
  r_col1, r_col2 = st.columns(2)
  with r_col1:
    st.markdown("### 📥 รายการรับเข้า (IN)")
    if not df_freebie_logs.empty:
      st.dataframe(df_freebie_logs, use_container_width=True, hide_index=True)
  with r_col2:
    st.markdown("### 📤 รายการแถมออก (OUT)")
    if not df_out_logs.empty:
      st.dataframe(df_out_logs, use_container_width=True, hide_index=True)
