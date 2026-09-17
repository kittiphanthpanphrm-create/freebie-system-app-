import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="สต็อกของแถม", page_icon="🎁", layout="wide"
)

# หัวข้อหลักตามที่ต้องการแก้ไข
st.title("🎁 สต็อกของแถม")

tab1, tab2, tab3 = st.tabs(
    ["📊 สต็อกคงเหลือ", "📥 รับเข้าของแถม (IN)", "📤 ตัดจ่ายตามบิล (OUT)"]
)

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
  })

df = st.session_state.df_freebie

with tab1:
  st.subheader("รายการของแถมทั้งหมด")
  low_stock = df[df["qty"] <= df["min_qty"]]
  if not low_stock.empty:
    st.warning(f"⚠️ มีของแถมใกล้หมด {len(low_stock)} รายการ กรุณาเติมสต็อก!")
  st.dataframe(df, use_container_width=True)

with tab2:
  st.subheader("บันทึกรับเข้าของแถมเข้าคลัง")
  with st.form("form_in"):
    sku_in = st.selectbox("เลือก SKU ของแถมรับเข้า", df["sku"].tolist())
    qty_in = st.number_input("จำนวนรับเข้า", min_value=1, value=20)
    submit_in = st.form_submit_button("บันทึกรับเข้าของแถม")
    if submit_in:
      idx = df[df["sku"] == sku_in].index
      st.session_state.df_freebie.loc[idx, "qty"] += qty_in
      st.success(f"เพิ่มสต็อก {sku_in} เรียบร้อย (+{qty_in})")
      st.rerun()

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
        idx = df[df["sku"] == sku_out].index
        st.session_state.df_freebie.loc[idx, "qty"] -= qty_out
        st.success(
            f"ตัดของแถม {sku_out} จำนวน {qty_out} สำเร็จ (ผูกบิล"
            f" {order_ref})"
        )
        st.rerun()
      else:
        st.error("❌ สต็อกของแถมไม่พอแจก!")
