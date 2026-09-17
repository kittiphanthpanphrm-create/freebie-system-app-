import datetime
import pandas as pd
import streamlit as st

st.set_page_config(page_title="สต็อกของแถม", page_icon="🎁", layout="wide")

st.title("🎁 สต็อกของแถม")

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 สต็อกคงเหลือ",
    "📥 รับเข้าของแถม (IN)",
    "📤 ตัดจ่ายตามบิล (OUT)",
    "⚙️ จัดการ/แก้ไข/ลบ",
])

# Initialize Session State
if "df_freebie" not in st.session_state:
  st.session_state.df_freebie = pd.DataFrame({
      "sku": ["FB-CAT-01", "FB-DOG-02", "FB-TOY-03"],
      "name": [
          "ขนมแมวเลียซองทดลอง",
          "แชมพูสุนัขขวดเล็ก",
          "พวงกุญแจห้อยกระเป๋า",
      ],
      "qty": [50, 25, 15],
      "min_qty": [10, 5, 5],
      "location": ["ล็อก A1", "ล็อก A2", "ล็อก B1"],
  })

if "df_freebie_logs" not in st.session_state:
  st.session_state.df_freebie_logs = pd.DataFrame(
      columns=[
          "วันที่",
          "SKU",
          "ชื่อของแถม",
          "ชื่อล็อก",
          "จำนวนที่รับเข้า",
          "ไฟล์รูป",
      ]
  )

df = st.session_state.df_freebie

with tab1:
  st.subheader("รายการของแถมทั้งหมด")
  low_stock = df[df["qty"] <= df["min_qty"]]
  if not low_stock.empty:
    st.warning(f"⚠️ มีของแถมใกล้หมด {len(low_stock)} รายการ กรุณาเติมสต็อก!")
  st.dataframe(df, use_container_width=True)

with tab2:
  st.subheader("📥 บันทึกรับเข้าของแถมเข้าคลัง")
  with st.form("form_in", clear_on_submit=True):
    display_list = (df["sku"] + " | " + df["name"]).tolist()
    selected_item = st.selectbox("เลือก SKU / ชื่อของแถม", display_list)

    target_sku = selected_item.split(" | ")[0]
    target_name = selected_item.split(" | ")[1]

    default_loc = df[df["sku"] == target_sku]["location"].values[0]

    date_in = st.date_input("วันที่รับเข้า", value=datetime.date.today())
    location_in = st.text_input("ชื่อล็อกที่จัดเก็บของแถม", value=default_loc)
    qty_in = st.number_input("จำนวนที่รับเข้า", min_value=1, value=10)

    # เพิ่มช่องอัปโหลดรูป / ถ่ายจากมือถือ
    uploaded_file = st.file_uploader(
        "📸 รูปถ่ายสินค้า (อัปโหลดจากคอม หรือ ถ่ายจากมือถือ)",
        type=["jpg", "jpeg", "png"],
    )

    submit_in = st.form_submit_button("บันทึกรับเข้าของแถม")
    if submit_in:
      idx = df[df["sku"] == target_sku].index[0]
      st.session_state.df_freebie.loc[idx, "qty"] += qty_in
      st.session_state.df_freebie.loc[idx, "location"] = location_in

      file_name = (
          uploaded_file.name if uploaded_file is not None else "ไม่มีรูป"
      )

      new_log = pd.DataFrame([{
          "วันที่": str(date_in),
          "SKU": target_sku,
          "ชื่อของแถม": target_name,
          "ชื่อล็อก": location_in,
          "จำนวนที่รับเข้า": qty_in,
          "ไฟล์รูป": file_name,
      }])
      st.session_state.df_freebie_logs = pd.concat(
          [st.session_state.df_freebie_logs, new_log], ignore_index=True
      )

      st.success(
          f"✅ บันทึกรับเข้า '{target_name}' จำนวน +{qty_in} ชิ้น ที่"
          f" '{location_in}' เรียบร้อย!"
      )
      st.rerun()

  st.divider()
  st.subheader("📜 ประวัติการรับเข้าของแถม")
  if not st.session_state.df_freebie_logs.empty:
    st.dataframe(st.session_state.df_freebie_logs, use_container_width=True)
  else:
    st.info("ยังไม่มีประวัติการรับเข้าในรอบนี้")

with tab3:
  st.subheader("ตัดสต็อกของแถมผูกกับบิลขายหลัก")
  with st.form("form_out"):
    order_ref = st.text_input(
        "เลขที่ออเดอร์ / Order Ref", placeholder="POS-20260901-001"
    )
    sku_out = st.selectbox("เลือกของแถมแถมท้ายบิล", df["sku"].tolist())
    qty_out = st.number_input("จำนวนที่แจก", min_value=1, value=1)
    submit_out = st.form_submit_button("ยืนยันตัดสต็อกของแถม")
    if submit_out:
      current_q = df[df["sku"] == sku_out]["qty"].values[0]
      if current_q >= qty_out:
        idx = df[df["sku"] == sku_out].index[0]
        st.session_state.df_freebie.loc[idx, "qty"] -= qty_out
        st.success(
            f"ตัดของแถม {sku_out} จำนวน {qty_out} สำเร็จ (ผูกบิล"
            f" {order_ref})"
        )
        st.rerun()
      else:
        st.error("❌ สต็อกของแถมไม่พอแจก!")

with tab4:
  st.subheader("⚙️ แก้ไขหรือลบรายการของแถม")
  target_sku_mgmt = st.selectbox(
      "เลือก SKU ของแถมที่ต้องการจัดการ", df["sku"].tolist()
  )

  col_btn1, col_btn2 = st.columns(2)
  with col_btn1:
    if st.button("✏️ แก้ไขข้อมูล"):
      st.session_state["edit_target"] = target_sku_mgmt
  with col_btn2:
    if st.button("🗑️ ลบรายการนี้"):
      st.session_state["confirm_del_target"] = target_sku_mgmt

  if st.session_state.get("confirm_del_target") == target_sku_mgmt:
    st.warning(
        f"⚠️ คุณแน่ใจหรือไม่ที่จะลบ SKU: {target_sku_mgmt}"
        f" ({df[df['sku'] == target_sku_mgmt]['name'].values[0]})?"
    )
    c_yes, c_no = st.columns(2)
    with c_yes:
      if st.button("✅ ยืนยันลบจริง"):
        st.session_state.df_freebie = st.session_state.df_freebie[
            st.session_state.df_freebie["sku"] != target_sku_mgmt
        ].reset_index(drop=True)
        del st.session_state["confirm_del_target"]
        st.success("ลบรายการเรียบร้อย!")
        st.rerun()
    with c_no:
      if st.button("❌ ยกเลิกการลบ"):
        del st.session_state["confirm_del_target"]
        st.rerun()

  if st.session_state.get("edit_target") == target_sku_mgmt:
    row_idx = df[df["sku"] == target_sku_mgmt].index[0]
    c_name = df.loc[row_idx, "name"]
    c_qty = int(df.loc[row_idx, "qty"])
    c_min = int(df.loc[row_idx, "min_qty"])
    c_loc = df.loc[row_idx, "location"]

    st.markdown(f"--- \n **กำลังแก้ไข SKU: {target_sku_mgmt}**")
    with st.form("edit_form_mgmt"):
      new_n = st.text_input("ชื่อของแถม", value=c_name)
      new_q = st.number_input("จำนวนคงเหลือ", value=c_qty, min_value=0)
      new_m = st.number_input("จุดแจ้งเตือนขั้นต่ำ", value=c_min, min_value=0)
      new_l = st.text_input("ชื่อล็อกจัดเก็บ", value=c_loc)

      if st.form_submit_button("💾 บันทึกการแก้ไข"):
        st.session_state.df_freebie.loc[row_idx, "name"] = new_n
        st.session_state.df_freebie.loc[row_idx, "qty"] = new_q
        st.session_state.df_freebie.loc[row_idx, "min_qty"] = new_m
        st.session_state.df_freebie.loc[row_idx, "location"] = new_l
        del st.session_state["edit_target"]
        st.success("บันทึกการแก้ไขเรียบร้อย!")
        st.rerun()
