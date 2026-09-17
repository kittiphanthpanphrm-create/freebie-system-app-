import datetime
import os
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Kathi Freebie POS", page_icon="🎁", layout="wide")

STOCK_FILE = "stock_data.csv"
LOG_IN_FILE = "log_in_data.csv"
LOG_OUT_FILE = "log_out_data.csv"


def load_data():
  if os.path.exists(STOCK_FILE):
    df_stock = pd.read_csv(STOCK_FILE, dtype=str)
    df_stock["qty"] = pd.to_numeric(df_stock["qty"], errors="coerce").fillna(0)
    df_stock["min_qty"] = pd.to_numeric(
        df_stock["min_qty"], errors="coerce"
    ).fillna(5)
  else:
    df_stock = pd.DataFrame(
        columns=["sku", "name", "qty", "min_qty", "location"]
    )

  if os.path.exists(LOG_IN_FILE):
    df_in = pd.read_csv(LOG_IN_FILE, dtype=str)
    df_in["log_id"] = pd.to_numeric(df_in["log_id"], errors="coerce").fillna(0)
    df_in["จำนวนที่รับเข้า"] = pd.to_numeric(
        df_in["จำนวนที่รับเข้า"], errors="coerce"
    ).fillna(0)
    if "file_obj" not in df_in.columns:
      df_in["file_obj"] = None
  else:
    df_in = pd.DataFrame(
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
    )

  if os.path.exists(LOG_OUT_FILE):
    df_out = pd.read_csv(LOG_OUT_FILE, dtype=str)
    df_out["log_id"] = pd.to_numeric(
        df_out["log_id"], errors="coerce"
    ).fillna(0)
    df_out["จำนวนที่แถมไป"] = pd.to_numeric(
        df_out["จำนวนที่แถมไป"], errors="coerce"
    ).fillna(0)
  else:
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

st.title("🎁 ระบบจัดการสต็อกของแถม")

with st.sidebar:
  st.markdown("### ⚙️ ตั้งค่าระบบ")
  with st.expander("🔐 ตั้งค่ารีเซ็ตข้อมูล"):
    reset_pin = st.text_input(
        "กรอกรหัสผ่าน",
        type="password",
        key="sidebar_reset_pin",
        placeholder="••••",
    )
    if st.button("🗑️ รีเซ็ต/ล้างข้อมูลทั้งหมด", use_container_width=True):
      if reset_pin == "1234":
        if os.path.exists(STOCK_FILE):
          os.remove(STOCK_FILE)
        if os.path.exists(LOG_IN_FILE):
          os.remove(LOG_IN_FILE)
        if os.path.exists(LOG_OUT_FILE):
          os.remove(LOG_OUT_FILE)
        st.sidebar.success("✅ รีเซ็ตระบบสำเร็จ")
        st.rerun()
      else:
        st.sidebar.error("❌ รหัสผ่านไม่ถูกต้อง (กรุณากรอก 1234)")

  with st.expander("💾 สำรอง / กู้คืนข้อมูล (Backup)"):
    if os.path.exists(STOCK_FILE):
      with open(STOCK_FILE, "rb") as f:
        st.download_button(
            "⬇️ โหลด Stock.csv",
            f,
            file_name="stock_data.csv",
            use_container_width=True,
        )
    if os.path.exists(LOG_IN_FILE):
      with open(LOG_IN_FILE, "rb") as f:
        st.download_button(
            "⬇️ โหลด Log_IN.csv",
            f,
            file_name="log_in_data.csv",
            use_container_width=True,
        )
    if os.path.exists(LOG_OUT_FILE):
      with open(LOG_OUT_FILE, "rb") as f:
        st.download_button(
            "⬇️ โหลด Log_OUT.csv",
            f,
            file_name="log_out_data.csv",
            use_container_width=True,
        )

    st.divider()
    up_stock = st.file_uploader(
        "⬆️ กู้คืน Stock.csv", type=["csv"], key="restore_stock"
    )
    if up_stock is not None:
      with open(STOCK_FILE, "wb") as f:
        f.write(up_stock.getbuffer())
      st.success("✅ กู้คืน Stock สำเร็จ รีเฟรชหน้าเว็บ 1 ครั้ง")

    up_in = st.file_uploader(
        "⬆️ กู้คืน Log_IN.csv", type=["csv"], key="restore_in"
    )
    if up_in is not None:
      with open(LOG_IN_FILE, "wb") as f:
        f.write(up_in.getbuffer())
      st.success("✅ กู้คืน Log_IN สำเร็จ รีเฟรชหน้าเว็บ 1 ครั้ง")

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 สต็อกคงเหลือ",
    "📥 รับเข้าของแถม (IN)",
    "📤 ตัดจ่ายตามบิล (OUT)",
    "📈 รายงานเคลื่อนไหว (Report)",
])

with tab1:
  st.subheader("📦 สต็อกคงเหลือและรูปภาพล่าสุดของสินค้า")
  if not df_stock.empty:
    low_stock = df_stock[
        pd.to_numeric(df_stock["qty"], errors="coerce")
        <= pd.to_numeric(df_stock["min_qty"], errors="coerce")
    ]
    if not low_stock.empty:
      st.warning(
          f"⚠️ มีของแถมใกล้หมด {len(low_stock)} รายการ กรุณาเติมสต็อก!"
      )

    for idx, row in df_stock.iterrows():
      with st.container(border=True):
        c_img, c_info = st.columns([1, 3], gap="medium")
        with c_img:
          img_displayed = False
          if not df_freebie_logs.empty:
            sub_l = df_freebie_logs[df_freebie_logs["SKU"] == str(row["sku"])]
            for _, l_row in sub_l.iloc[::-1].iterrows():
              if (
                  "file_obj" in l_row
                  and pd.notna(l_row["file_obj"])
                  and str(l_row["file_obj"]) != "None"
              ):
                st.image(
                    str(l_row["file_obj"]), width=130, caption="ภาพรับเข้าล่าสุด"
                )
                img_displayed = True
                break
          if not img_displayed:
            st.info("ไม่มีรูปถ่าย")

        with c_info:
          st.markdown(f"### 🏷️ {row['name']} `[{row['sku']}]`")
          col_i1, col_i2, col_i3, col_i4 = st.columns(4)
          col_i1.metric("สต็อกคงเหลือ", f"{row['qty']} ชิ้น")
          col_i2.metric("จุดแจ้งเตือนต่ำ", f"{row['min_qty']} ชิ้น")
          col_i3.metric("พิกัดล็อก", row["location"])

          if (
              not df_freebie_logs.empty
              and str(row["sku"]) in df_freebie_logs["SKU"].values
          ):
            last_log = df_freebie_logs[
                df_freebie_logs["SKU"] == str(row["sku"])
            ].iloc[-1]
            col_i4.metric(
                "รับเข้าล่าสุด",
                f"+{last_log['จำนวนที่รับเข้า']}",
                delta=f"วันที่ {last_log['วันที่']}",
            )
          else:
            col_i4.metric("รับเข้าล่าสุด", "ยังไม่มีข้อมูล")
  else:
    st.info("✨ ยังไม่มีข้อมูลสินค้า กรุณาเพิ่มที่หน้ารับเข้าด้านบนได้เลยครับ")

with tab2:
  st.subheader("📥 บันทึกรับเข้าของแถม / เพิ่ม SKU ใหม่")
  is_new_sku = st.checkbox(
      "➕ เพิ่มเป็น SKU ใหม่ / สินค้าใหม่", value=df_stock.empty
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
        "💾 บันทึกรับเข้าของแถม", type="primary", use_container_width=True
    )

    if submit_in:
      if not target_sku or not target_name:
        st.error("❌ กรุณากรอกรหัส SKU และชื่อสินค้าให้ครบถ้วน")
      else:
        target_sku = str(target_sku)
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

        file_name = (
            uploaded_file.name if uploaded_file is not None else "ไม่มีรูป"
        )
        file_path_save = None
        if uploaded_file is not None:
          os.makedirs("uploads", exist_ok=True)
          file_path_save = os.path.join(
              "uploads",
              f"{int(datetime.datetime.now().timestamp())}_{uploaded_file.name}",
          )
          with open(file_path_save, "wb") as f:
            f.write(uploaded_file.getbuffer())

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
            "file_obj": file_path_save,
            "ไฟล์รูป": file_name,
        }])
        df_freebie_logs = pd.concat(
            [df_freebie_logs, new_log], ignore_index=True
        )

        df_stock.to_csv(STOCK_FILE, index=False)
        df_freebie_logs.to_csv(LOG_IN_FILE, index=False)

        st.success(
            f"✅ บันทึกรับเข้า/สร้างใหม่ '{target_name}' จำนวน +{qty_in} ชิ้นเรียบร้อย!"
        )
        st.rerun()

  st.divider()
  st.subheader("📜 ประวัติการรับเข้าของแถม (แก้ไขจำนวน / เปลี่ยนรูป)")
  if not df_freebie_logs.empty and not df_stock.empty:
    for i, lrow in df_freebie_logs.iterrows():
      with st.expander(
          f"Log ID: {lrow['log_id']} | วันที่: {lrow['วันที่']} | SKU:"
          f" {lrow['SKU']} | รับเข้า: +{lrow['จำนวนที่รับเข้า']}"
      ):
        c_img_prev, c_ed1, c_del = st.columns([1.5, 2.5, 1.5])
        with c_img_prev:
          if (
              "file_obj" in lrow
              and pd.notna(lrow["file_obj"])
              and str(lrow["file_obj"]) != "None"
              and os.path.exists(str(lrow["file_obj"]))
          ):
            st.image(str(lrow["file_obj"]), width=90, caption="รูปปัจจุบัน")
          else:
            st.caption("ไม่มีรูป")

        with c_ed1:
          edit_qty_val = st.number_input(
              f"แก้จำนวน (ID {lrow['log_id']})",
              min_value=1,
              value=int(lrow["จำนวนที่รับเข้า"]),
              key=f"in_qty_edit_{i}",
          )
          edit_file_val = st.file_uploader(
              "แนบ/เปลี่ยนรูป (คอม/มือถือ)",
              type=["jpg", "jpeg", "png"],
              key=f"in_file_edit_{i}",
          )
          if st.button("💾 บันทึกแก้รับเข้า", key=f"save_in_edit_{i}"):
            old_qty = int(lrow["จำนวนที่รับเข้า"])
            diff = edit_qty_val - old_qty
            target_sku_str = str(lrow["SKU"])
            if target_sku_str in df_stock["sku"].astype(str).values:
              idx_s = df_stock[
                  df_stock["sku"].astype(str) == target_sku_str
              ].index[0]
              df_stock.loc[idx_s, "qty"] = (
                  int(df_stock.loc[idx_s, "qty"]) + diff
              )
            df_freebie_logs.at[i, "จำนวนที่รับเข้า"] = edit_qty_val
            if edit_file_val is not None:
              os.makedirs("uploads", exist_ok=True)
              new_path = os.path.join(
                  "uploads",
                  f"{int(datetime.datetime.now().timestamp())}_{edit_file_val.name}",
              )
              with open(new_path, "wb") as f:
                f.write(edit_file_val.getbuffer())
              df_freebie_logs.at[i, "file_obj"] = new_path
              df_freebie_logs.at[i, "ไฟล์รูป"] = edit_file_val.name

            df_stock.to_csv(STOCK_FILE, index=False)
            df_freebie_logs.to_csv(LOG_IN_FILE, index=False)
            st.success("อัปเดตข้อมูลรับเข้าเรียบร้อย!")
            st.rerun()

        with c_del:
          st.write(" ")
          if st.button("🗑️ ลบรายการรับเข้า", key=f"del_in_{lrow['log_id']}_{i}"):
            old_qty = int(lrow["จำนวนที่รับเข้า"])
            target_sku_str = str(lrow["SKU"])
            if target_sku_str in df_stock["sku"].astype(str).values:
              idx_s = df_stock[
                  df_stock["sku"].astype(str) == target_sku_str
              ].index[0]
              df_stock.loc[idx_s, "qty"] = (
                  int(df_stock.loc[idx_s, "qty"]) - old_qty
              )
            df_freebie_logs = df_freebie_logs.drop(i).reset_index(drop=True)

            df_stock.to_csv(STOCK_FILE, index=False)
            df_freebie_logs.to_csv(LOG_IN_FILE, index=False)
            st.success("ลบรายการเรียบร้อย!")
            st.rerun()
  else:
    st.info("ยังไม่มีประวัติการรับเข้า")

with tab3:
  st.subheader("📤 ตัดจ่ายตามบิล (OUT)")
  if df_stock.empty:
    st.warning("⚠️ ยังไม่มีสินค้าในระบบ กรุณาเพิ่มสินค้าผ่านหน้ารับเข้าก่อน")
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
      if selected_item_out:
        target_sku_out = selected_item_out.split(" | ")[0]
        target_name_out = selected_item_out.split(" | ")[1]
        default_loc_out = df_stock[
            df_stock["sku"].astype(str) == target_sku_out
        ]["location"].values[0]
      else:
        target_sku_out, target_name_out, default_loc_out = "", "", ""

      date_out = st.date_input("วันที่ตัดจ่าย", value=datetime.date.today())
      location_out = st.text_input(
          "ชื่อล็อกที่จัดของแถม", value=default_loc_out
      )
      qty_out = st.number_input("จำนวนที่แถมไป", min_value=1, value=1)

      submit_out = st.form_submit_button(
          "ยืนยันตัดสต็อกของแถม", type="primary", use_container_width=True
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

          df_stock.to_csv(STOCK_FILE, index=False)
          df_out_logs.to_csv(LOG_OUT_FILE, index=False)

          st.success(f"✅ ตัดจ่าย '{target_name_out}' เรียบร้อย!")
          st.rerun()
        else:
          st.error("❌ สต็อกของแถมไม่พอแจก!")

  st.divider()
  st.subheader("📜 ประวัติการตัดจ่ายตามบิล (OUT)")
  if not df_out_logs.empty and not df_stock.empty:
    for i, orow in df_out_logs.iterrows():
      item_name_str = orow.get("ชื่อของแถม", "ไม่ระบุ")
      with st.expander(
          f"Log ID: {orow['log_id']} | วันที่: {orow['วันที่']} | ออเดอร์:"
          f" {orow['เลขที่ออเดอร์']} | สินค้า: {item_name_str} | แจก:"
          f" -{orow['จำนวนที่แถมไป']}"
      ):
        c_ed_out, c_del_out = st.columns([3, 1])
        with c_ed_out:
          edit_q_out = st.number_input(
              f"แก้จำนวนแจก (ID {orow['log_id']})",
              min_value=1,
              value=int(orow["จำนวนที่แถมไป"]),
              key=f"out_qty_edit_{i}",
          )
          edit_order_out = st.text_input(
              f"แก้ออเดอร์ (ID {orow['log_id']})",
              value=str(orow["เลขที่ออเดอร์"]),
              key=f"out_ord_edit_{i}",
          )
          if st.button("💾 บันทึกแก้ตัดจ่าย", key=f"save_out_edit_{i}"):
            old_qty = int(orow["จำนวนที่แถมไป"])
            diff = edit_q_out - old_qty
            target_sku_str = str(orow["SKU"])
            if (
                diff > 0
                and target_sku_str in df_stock["sku"].astype(str).values
            ):
              idx_s = df_stock[
                  df_stock["sku"].astype(str) == target_sku_str
              ].index[0]
              current_stk = int(df_stock.loc[idx_s, "qty"])
              if current_stk < diff:
                st.error("❌ สต็อกไม่พอปรับเพิ่มจำนวนแจก!")
                st.stop()

            if target_sku_str in df_stock["sku"].astype(str).values:
              idx_s = df_stock[
                  df_stock["sku"].astype(str) == target_sku_str
              ].index[0]
              df_stock.loc[idx_s, "qty"] = (
                  int(df_stock.loc[idx_s, "qty"]) - diff
              )

            df_out_logs.at[i, "จำนวนที่แถมไป"] = edit_q_out
            df_out_logs.at[i, "เลขที่ออเดอร์"] = edit_order_out

            df_stock.to_csv(STOCK_FILE, index=False)
            df_out_logs.to_csv(LOG_OUT_FILE, index=False)
            st.success("อัปเดตข้อมูลตัดจ่ายเรียบร้อย!")
            st.rerun()

        with c_del_out:
          st.write(" ")
          if st.button(
              "🗑️ ลบรายการตัดจ่าย", key=f"del_out_{orow['log_id']}_{i}"
          ):
            old_qty = int(orow["จำนวนที่แถมไป"])
            target_sku_str = str(orow["SKU"])
            if target_sku_str in df_stock["sku"].astype(str).values:
              idx_s = df_stock[
                  df_stock["sku"].astype(str) == target_sku_str
              ].index[0]
              df_stock.loc[idx_s, "qty"] = (
                  int(df_stock.loc[idx_s, "qty"]) + old_qty
              )
            df_out_logs = df_out_logs.drop(i).reset_index(drop=True)

            df_stock.to_csv(STOCK_FILE, index=False)
            df_out_logs.to_csv(LOG_OUT_FILE, index=False)
            st.success("คืนสต็อกและลบรายการสำเร็จ!")
            st.rerun()
  else:
    st.info("ยังไม่มีประวัติการตัดจ่าย")

with tab4:
  st.subheader("📈 รายงานสรุปการเคลื่อนไหว (รับเข้า / แถมออก)")
  c_f1, c_f2 = st.columns(2)
  with c_f1:
    rep_start_date = st.date_input(
        "ตั้งแต่วันที่", value=datetime.date.today() - datetime.timedelta(days=30)
    )
  with c_f2:
    rep_end_date = st.date_input("ถึงวันที่", value=datetime.date.today())

  st.markdown("---")
  r_col1, r_col2 = st.columns(2)

  with r_col1:
    st.markdown("### 📥 รายการรับเข้า (IN)")
    if not df_freebie_logs.empty:
      df_freebie_logs["dt_parsed"] = pd.to_datetime(
          df_freebie_logs["วันที่"], errors="coerce"
      ).dt.date
      filt_in = df_freebie_logs[
          (df_freebie_logs["dt_parsed"] >= rep_start_date)
          & (df_freebie_logs["dt_parsed"] <= rep_end_date)
      ]
      tot_in = (
          filt_in["จำนวนที่รับเข้า"].sum() if not filt_in.empty else 0
      )
      st.metric("รวมรับเข้าช่วงนี้", f"+{tot_in} ชิ้น")
      st.dataframe(
          filt_in[[
              "log_id",
              "วันที่",
              "SKU",
              "ชื่อของแถม",
              "ชื่อล็อก",
              "จำนวนที่รับเข้า",
          ]],
          use_container_width=True,
          hide_index=True,
      )
      if not filt_in.empty:
        st.download_button(
            "📥 โหลดรายงานรับเข้า (CSV)",
            filt_in.to_csv(index=False).encode("utf-8-sig"),
            "report_in.csv",
            mime="text/csv",
        )
    else:
      st.info("ไม่มีข้อมูลรับเข้า")

  with r_col2:
    st.markdown("### 📤 รายการแถมออก (OUT)")
    if not df_out_logs.empty:
      df_out_logs["dt_parsed"] = pd.to_datetime(
          df_out_logs["วันที่"], errors="coerce"
      ).dt.date
      filt_out = df_out_logs[
          (df_out_logs["dt_parsed"] >= rep_start_date)
          & (df_out_logs["dt_parsed"] <= rep_end_date)
      ]
      tot_out = (
          filt_out["จำนวนที่แถมไป"].sum() if not filt_out.empty else 0
      )
      st.metric("รวมแถมออกช่วงนี้", f"-{tot_out} ชิ้น")
      st.dataframe(
          filt_out[[
              "log_id",
              "วันที่",
              "เลขที่ออเดอร์",
              "SKU",
              "ชื่อของแถม",
              "ชื่อล็อก",
              "จำนวนที่แถมไป",
          ]],
          use_container_width=True,
          hide_index=True,
      )
      if not filt_out.empty:
        st.download_button(
            "📤 โหลดรายงานแถมออก (CSV)",
            filt_out.to_csv(index=False).encode("utf-8-sig"),
            "report_out.csv",
            mime="text/csv",
        )
    else:
      st.info("ไม่มีข้อมูลแถมออก")
