import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Freebie Management System", page_icon="🎁", layout="wide"
)

st.title("🎁 ระบบจัดการสต็อกและแจกของแถม (Freebie Dedicated App)")

if "freebie_db" not in st.session_state:
  st.session_state.freebie_db = pd.DataFrame({
      "freebie_sku": ["FB-CAT-01", "FB-DOG-02", "FB-TOY-03"],
      "item_name": [
          "ขนมแมวเลียสูตรไก่ (ซองทดลอง)",
          "กระดูกยางขัดฟันสุนัข",
          "พวงกุญแจแมวคัธี",
      ],
      "category": ["อาหาร", "อุปกรณ์", "ของพรีเมียม"],
      "qty_left": [120, 45, 80],
      "min_alert": [20, 10, 15],
  })

df_fb = st.session_state.freebie_db

tab1, tab2, tab3 = st.tabs(
    ["📦 คลังของแถมทั้งหมด", "📤 บันทึกแจกของแถมตามบิล", "📥 รับเข้าของแถมเพิ่ม"]
)

with tab1:
  st.subheader("รายการของแถมคงเหลือ")
  st.dataframe(df_fb, use_container_width=True)

  low_stock = df_fb[df_fb["qty_left"] <= df_fb["min_alert"]]
  if not low_stock.empty:
    st.warning("⚠️ มีของแถมต่ำกว่าจุดเตือน:")
    st.write(low_stock[["freebie_sku", "item_name", "qty_left"]])

with tab2:
  st.subheader("ตัดสต็อกแจกของแถม (Checkout / Promo Freebie)")
  with st.form("issue_form"):
    order_ref = st.text_input("เลขที่บิลขายหลัก (Order ID)", "POS-99901")
    sku_target = st.selectbox(
        "เลือก SKU ของแถมที่จะแถม", df_fb["freebie_sku"].tolist()
    )
    give_qty = st.number_input("จำนวนที่แจก", min_value=1, value=1)
    submit_give = st.form_submit_button("ยืนยันจ่ายของแถม")

    if submit_give:
      idx = df_fb[df_fb["freebie_sku"] == sku_target].index[0]
      current_q = df_fb.loc[idx, "qty_left"]
      if current_q >= give_qty:
        st.session_state.freebie_db.loc[idx, "qty_left"] -= give_qty
        st.success(
            f"✅ แจก {sku_target} จำนวน {give_qty} ชิ้น (ผูกบิล"
            f" {order_ref}) สำเร็จ!"
        )
        st.rerun()
      else:
        st.error("❌ ของแถมในคลังไม่พอจ่าย!")

with tab3:
  st.subheader("เพิ่มสต็อกรับเข้า (Stock In)")
  with st.form("in_form"):
    sku_in = st.selectbox(
        "เลือก SKU ของแถมรับเข้า", df_fb["freebie_sku"].tolist()
    )
    add_q = st.number_input("จำนวนรับเข้า", min_value=1, value=50)
    submit_add = st.form_submit_button("บันทึกรับเข้าของแถม")

    if submit_add:
      idx = df_fb[df_fb["freebie_sku"] == sku_in].index[0]
      st.session_state.freebie_db.loc[idx, "qty_left"] += add_q
      st.success(f"➕ เติมสต็อก {sku_in} +{add_q} ชิ้นเรียบร้อย!")
      st.rerun()
