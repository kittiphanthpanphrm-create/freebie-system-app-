import datetime
import pandas as pd
import streamlit as st

st.set_page_config(page_title="สต็อกของแถม", page_icon="🎁", layout="wide")

st.title("🎁 สต็อกของแถม")

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 สต็อกคงเหลือ",
    "📥 รับเข้าของแถม (IN)",
    "📤 ตัดจ่ายตามบิล (OUT)",
    "⚙️ จัดการสินค้า/ลบ SKU",
])

# Initialize Session State
if "df_freebie" not in st.session_state:
  st.session_state.df_freebie = pd.DataFrame(
      columns=["sku", "name", "qty", "min_qty", "location"], data=[]
  )
  if st.session_state.df_freebie.empty:
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

if "df_out_logs" not in st.session_state:
  st.session_state.df_out_logs = pd.DataFrame(
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

if "log_id_seq" not in st.session_state:
  st.session_state.log_id_seq = 1

df = st.session_state.df_freebie

with tab1:
  st.subheader("📦 สต็อกคงเหลือและรูปภาพล่าสุดของสินค้า")
  if not df.empty:
    low_stock = df[df["qty"] <= df["min_qty"]]
    if not low_stock.empty:
      st.warning(
          f"⚠️ มีของแถมใกล้หมด {len(low_stock)} รายการ กรุณาเติมสต็อก!"
      )

    logs_df = st.session_state.df_freebie_logs

    for idx, row in df.iterrows():
      with st.container(border=True):
        c_img, c_info = st.columns([1, 3])
        with c_img:
          img_displayed = False
          if not logs_df.empty:
            sub_l = logs_df[logs_df["SKU"] == row["sku"]]
            for _, l_row in sub_l.iloc[::-1].iterrows():
              if (
                  "file_obj" in l_row
                  and l_row["file_obj"] is not None
                  and hasattr(l_row["file_obj"], "name")
              ):
                st.image(
                    l_row["file_obj"], width=120, caption="ภาพรับเข้าล่าสุด"
                )
                img_displayed = True
                break
          if not img_displayed:
            st.info("ไม่มีรูปถ่าย")

        with c_info:
          st.markdown(f"### 🏷️ {row['name']} (`{row['sku']}`)")
          col_i1, col_i2, col_i3, col_i4 = st.columns(4)
          col_i1.metric("สต็อกคงเหลือ", f"{row['qty']} ชิ้น")
          col_i2.metric("จุดแจ้งเตือนขั้นต่ำ", f"{row['min_qty']} ชิ้น")
          col_i3.metric("พิกัดล็อก", row["location"])

          if not logs_df.empty and row["sku"] in logs_df["SKU"].values:
            last_log = logs_df[logs_df["SKU"] == row["sku"]].iloc[-1]
            col_i4.metric(
                "รับเข้าล่าสุด",
                f"+{last_log['จำนวนที่รับเข้า']}",
                delta=f"วันที่ {last_log['วันที่']}",
            )
          else:
            col_i4.metric("รับเข้าล่าสุด", "ยังไม่มีข้อมูล")
  else:
    st.info("ยังไม่มีข้อมูลสินค้า กรุณาเพิ่มที่ Tab จัดการสินค้า")

with tab2:
  st.subheader("📥 บันทึกรับเข้าของแถมเข้าคลัง")
  if df.empty:
    st.warning("⚠️ ยังไม่มีสินค้าในระบบ กรุณาเพิ่ม SKU ก่อน")
  else:
    display_list = (df["sku"] + " | " + df["name"]).tolist()
    with st.form("form_in", clear_on_submit=True):
      selected_item = st.selectbox("เลือก SKU / ชื่อของแถม", display_list)
      if selected_item:
        target_sku = selected_item.split(" | ")[0]
        target_name = selected_item.split(" | ")[1]
        default_loc = df[df["sku"] == target_sku]["location"].values[0]
      else:
        target_sku, target_name, default_loc = "", "", ""

      date_in = st.date_input("วันที่รับเข้า", value=datetime.date.today())
      location_in = st.text_input("ชื่อล็อกที่จัดเก็บของแถม", value=default_loc)
      qty_in = st.number_input("จำนวนที่รับเข้า", min_value=1, value=10)

      uploaded_file = st.file_uploader(
          "📸 รูปถ่ายสินค้า (อัปโหลดจากคอม หรือ ถ่ายจากมือถือ)",
          type=["jpg", "jpeg", "png"],
      )

      submit_in = st.form_submit_button("บันทึกรับเข้าของแถม")
      if submit_in and target_sku:
        idx = df[df["sku"] == target_sku].index[0]
        st.session_state.df_freebie.loc[idx, "qty"] += qty_in
        st.session_state.df_freebie.loc[idx, "location"] = location_in

        file_name = (
            uploaded_file.name if uploaded_file is not None else "ไม่มีรูป"
        )

        current_lid = st.session_state.log_id_seq
        st.session_state.log_id_seq += 1

        new_log = pd.DataFrame([{
            "log_id": current_lid,
            "วันที่": str(date_in),
            "SKU": target_sku,
            "ชื่อของแถม": target_name,
            "ชื่อล็อก": location_in,
            "จำนวนที่รับเข้า": qty_in,
            "file_obj": uploaded_file,
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
  st.subheader("📜 ประวัติการรับเข้าของแถม (แก้ไข/ลบได้)")
  in_logs = st.session_state.df_freebie_logs
  if not in_logs.empty and not df.empty:
    for i, lrow in in_logs.iterrows():
      with st.expander(
          f"Log ID: {lrow['log_id']} | วันที่: {lrow['วันที่']} | SKU:"
          f" {lrow['SKU']} | รับเข้า: +{lrow['จำนวนที่รับเข้า']}"
      ):
        c_ed1, c_ed2, c_del = st.columns([2, 2, 2])
        with c_ed1:
          edit_qty_val = st.number_input(
              f"แก้จำนวน (ID {lrow['log_id']})",
              min_value=1,
              value=int(lrow["จำนวนที่รับเข้า"]),
              key=f"in_qty_{lrow['log_id']}",
          )
        with c_ed2:
          st.write(" ")
          st.write(" ")
          if st.button("💾 บันทึกแก้รับเข้า", key=f"save_in_{lrow['log_id']}"):
            old_qty = int(lrow["จำนวนที่รับเข้า"])
            diff = edit_qty_val - old_qty
            if lrow["SKU"] in df["sku"].values:
              idx_s = df[df["sku"] == lrow["SKU"]].index[0]
              st.session_state.df_freebie.loc[idx_s, "qty"] += diff
            st.session_state.df_freebie_logs.loc[i, "จำนวนที่รับเข้า"] = (
                edit_qty_val
            )
            st.success("อัปเดตรับเข้าเรียบร้อย!")
            st.rerun()
        with c_del:
          st.write(" ")
          st.write(" ")
          if st.button("🗑️ ลบรายการรับเข้า", key=f"del_in_{lrow['log_id']}"):
            st.session_state[f"confirm_del_in_{lrow['log_id']}"] = True

        if st.session_state.get(f"confirm_del_in_{lrow['log_id']}", False):
          st.warning(
              f"⚠️ ยืนยันลบ Log รับเข้า ID {lrow['log_id']}?"
              f" (จะหักสต็อกคืน -{lrow['จำนวนที่รับเข้า']})"
          )
          cy, cn = st.columns(2)
          with cy:
            if st.button(
                "✅ ยืนยันลบรับเข้า", key=f"yes_del_in_{lrow['log_id']}"
            ):
              old_qty = int(lrow["จำนวนที่รับเข้า"])
              if lrow["SKU"] in df["sku"].values:
                idx_s = df[df["sku"] == lrow["SKU"]].index[0]
                st.session_state.df_freebie.loc[idx_s, "qty"] -= old_qty
              st.session_state.df_freebie_logs = (
                  st.session_state.df_freebie_logs.drop(i).reset_index(
                      drop=True
                  )
              )
              del st.session_state[f"confirm_del_in_{lrow['log_id']}"]
              st.success("ลบรายการรับเข้าเรียบร้อย!")
              st.rerun()
          with cn:
            if st.button(
                "❌ ยกเลิก", key=f"no_del_in_{lrow['log_id']}"
            ):
              del st.session_state[f"confirm_del_in_{lrow['log_id']}"]
              st.rerun()
  else:
    st.info("ยังไม่มีประวัติการรับเข้าในรอบนี้")

with tab3:
  st.subheader("📤 ตัดจ่ายตามบิล (OUT)")
  if df.empty:
    st.warning("⚠️ ยังไม่มีสินค้าในระบบ กรุณาเพิ่ม SKU ก่อน")
  else:
    with st.form("form_out", clear_on_submit=True):
      order_ref = st.text_input(
          "เลขที่ออเดอร์ / Order Ref", placeholder="POS-20260901-001"
      )
      display_list_out = (df["sku"] + " | " + df["name"]).tolist()
      selected_item_out = st.selectbox(
          "เลือก SKU / ชื่อของแถม", display_list_out
      )
      if selected_item_out:
        target_sku_out = selected_item_out.split(" | ")[0]
        target_name_out = selected_item_out.split(" | ")[1]
        default_loc_out = df[df["sku"] == target_sku_out]["location"].values[0]
      else:
        target_sku_out, target_name_out, default_loc_out = "", "", ""

      date_out = st.date_input("วันที่ตัดจ่าย", value=datetime.date.today())
      location_out = st.text_input(
          "ชื่อล็อกที่จัดของแถม", value=default_loc_out
      )
      qty_out = st.number_input("จำนวนที่แถมไป", min_value=1, value=1)

      submit_out = st.form_submit_button("ยืนยันตัดสต็อกของแถม")
      if submit_out and target_sku_out:
        current_q = df[df["sku"] == target_sku_out]["qty"].values[0]
        if current_q >= qty_out:
          idx = df[df["sku"] == target_sku_out].index[0]
          st.session_state.df_freebie.loc[idx, "qty"] -= qty_out
          st.session_state.df_freebie.loc[idx, "location"] = location_out

          current_lid = st.session_state.log_id_seq
          st.session_state.log_id_seq += 1

          new_out_log = pd.DataFrame([{
              "log_id": current_lid,
              "วันที่": str(date_out),
              "เลขที่ออเดอร์": order_ref,
              "SKU": target_sku_out,
              "ชื่อของแถม": target_name_out,
              "ชื่อล็อก": location_out,
              "จำนวนที่แถมไป": qty_out,
          }])
          st.session_state.df_out_logs = pd.concat(
              [st.session_state.df_out_logs, new_out_log], ignore_index=True
          )

          st.success(
              f"✅ ตัดจ่าย '{target_name_out}' จำนวน -{qty_out} ชิ้น (ออเดอร์"
              f" {order_ref}, ล็อก {location_out}) เรียบร้อย!"
          )
          st.rerun()
        else:
          st.error("❌ สต็อกของแถมไม่พอแจก!")

  st.divider()
  st.subheader("📜 ประวัติการตัดจ่ายตามบิล (OUT) (แก้ไข/ลบได้)")
  out_logs = st.session_state.df_out_logs
  if not out_logs.empty and not df.empty:
    for i, orow in out_logs.iterrows():
      with st.expander(
          f"Log ID: {orow['log_id']} | วันที่: {orow['วันที่']} | ออเดอร์:"
          f" {orow['เลขที่ออเดอร์']} | SKU: {orow['SKU']} | แจก:"
          f" -{orow['จำนวนที่แถมไป']}"
      ):
        c_ed1, c_ed2, c_del = st.columns([2, 2, 2])
        with c_ed1:
          edit_q_out = st.number_input(
              f"แก้จำนวนแจก (ID {orow['log_id']})",
              min_value=1,
              value=int(orow["จำนวนที่แถมไป"]),
              key=f"out_qty_{orow['log_id']}",
          )
        with c_ed2:
          st.write(" ")
          st.write(" ")
          if st.button("💾 บันทึกแก้ตัดจ่าย", key=f"save_out_{orow['log_id']}"):
            old_qty = int(orow["จำนวนที่แถมไป"])
            diff = edit_q_out - old_qty
            if orow["SKU"] in df["sku"].values:
              idx_s = df[df["sku"] == orow["SKU"]].index[0]
              current_q_real = df.loc[idx_s, "qty"]
              if current_q_real - diff < 0:
                st.error("สต็อกคงเหลือไม่พอสำหรับการแก้ไขยอดนี้!")
              else:
                st.session_state.df_freebie.loc[idx_s, "qty"] -= diff
                st.session_state.df_out_logs.loc[i, "จำนวนที่แถมไป"] = (
                    edit_q_out
                )
                st.success("อัปเดตตัดจ่ายเรียบร้อย!")
                st.rerun()
        with c_del:
          st.write(" ")
          st.write(" ")
          if st.button(
              "🗑️ ลบรายการตัดจ่าย", key=f"del_out_{orow['log_id']}"
          ):
            st.session_state[f"confirm_del_out_{orow['log_id']}"] = True

        if st.session_state.get(f"confirm_del_out_{orow['log_id']}", False):
          st.warning(
              f"⚠️ ยืนยันลบ Log ตัดจ่าย ID {orow['log_id']}? (จะคืนสต็อกกลับ"
              f" +{orow['จำนวนที่แถมไป']})"
          )
          cy, cn = st.columns(2)
          with cy:
            if st.button(
                "✅ ยืนยันลบตัดจ่าย", key=f"yes_del_out_{orow['log_id']}"
            ):
              old_qty = int(orow["จำนวนที่แถมไป"])
              if orow["SKU"] in df["sku"].values:
                idx_s = df[df["sku"] == orow["SKU"]].index[0]
                st.session_state.df_freebie.loc[idx_s, "qty"] += old_qty
              st.session_state.df_out_logs = (
                  st.session_state.df_out_logs.drop(i).reset_index(drop=True)
              )
              del st.session_state[f"confirm_del_out_{orow['log_id']}"]
              st.success("ลบรายการตัดจ่ายเรียบร้อย!")
              st.rerun()
          with cn:
            if st.button(
                "❌ ยกเลิก", key=f"no_del_out_{orow['log_id']}"
            ):
              del st.session_state[f"confirm_del_out_{orow['log_id']}"]
              st.rerun()
  else:
    st.info("ยังไม่มีประวัติการตัดจ่ายในรอบนี้")

with tab4:
  st.subheader("⚙️ จัดการ SKU สินค้า / ลบ SKU / เพิ่มสินค้าใหม่")

  # เพิ่มฟอร์มสร้าง SKU ใหม่เผื่อเผลอลบหมด
  with st.expander("➕ เพิ่ม SKU สินค้าใหม่", expanded=df.empty):
    with st.form("form_add_sku"):
      new_s_sku = st.text_input("รหัส SKU", placeholder="FB-NEW-01")
      new_s_name = st.text_input("ชื่อสินค้า/ของแถม", placeholder="ชามข้าวแมว")
      new_s_qty = st.number_input("จำนวนตั้งต้น", min_value=0, value=10)
      new_s_min = st.number_input("จุดแจ้งเตือนขั้นต่ำ", min_value=0, value=5)
      new_s_loc = st.text_input("ชื่อล็อกจัดเก็บ", value="ล็อก A1")
      if st.form_submit_button("➕ เพิ่ม SKU ลงระบบ"):
        if new_s_sku:
          new_row = pd.DataFrame([{
              "sku": new_s_sku,
              "name": new_s_name,
              "qty": new_s_qty,
              "min_qty": new_s_min,
              "location": new_s_loc,
          }])
          st.session_state.df_freebie = pd.concat(
              [st.session_state.df_freebie, new_row], ignore_index=True
          )
          st.success(f"เพิ่ม SKU {new_s_sku} สำเร็จ!")
          st.rerun()

  if not df.empty:
    target_sku_mgmt = st.selectbox(
        "เลือก SKU ของแถมที่ต้องการจัดการ", df["sku"].tolist()
    )

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
      if st.button("✏️ แก้ไขข้อมูล SKU หลัก"):
        st.session_state["edit_target"] = target_sku_mgmt
    with col_btn2:
      if st.button("🗑️ ลบ SKU นี้ออกจากระบบ"):
        st.session_state["confirm_del_target"] = target_sku_mgmt

    if st.session_state.get("confirm_del_target") == target_sku_mgmt:
      st.warning(
          f"⚠️ คุณแน่ใจหรือไม่ที่จะลบ SKU: {target_sku_mgmt}?"
      )
      c_yes, c_no = st.columns(2)
      with c_yes:
        if st.button("✅ ยืนยันลบจริง"):
          st.session_state.df_freebie = st.session_state.df_freebie[
              st.session_state.df_freebie["sku"] != target_sku_mgmt
          ].reset_index(drop=True)
          del st.session_state["confirm_del_target"]
          st.success("ลบ SKU เรียบร้อย!")
          st.rerun()
      with c_no:
        if st.button("❌ ยกเลิกการลบ"):
          del st.session_state["confirm_del_target"]
          st.rerun()

    if st.session_state.get("edit_target") == target_sku_mgmt and not df[
        df["sku"] == target_sku_mgmt
    ].empty:
      row_idx = df[df["sku"] == target_sku_mgmt].index[0]
      c_name = df.loc[row_idx, "name"]
      c_qty = int(df.loc[row_idx, "qty"])
      c_min = int(df.loc[row_idx, "min_qty"])
      c_loc = df.loc[row_idx, "location"]

      st.markdown(f"--- \n **กำลังแก้ไข SKU: {target_sku_mgmt}**")
      with st.form("edit_form_mgmt"):
        new_n = st.text_input("ชื่อของแถม", value=c_name)
        new_q = st.number_input("จำนวนคงเหลือตั้งต้น", value=c_qty, min_value=0)
        new_m = st.number_input(
            "จุดแจ้งเตือนขั้นต่ำ", value=c_min, min_value=0
        )
        new_l = st.text_input("ชื่อล็อกจัดเก็บ", value=c_loc)

        if st.form_submit_button("💾 บันทึกการแก้ไข"):
          st.session_state.df_freebie.loc[row_idx, "name"] = new_n
          st.session_state.df_freebie.loc[row_idx, "qty"] = new_q
          st.session_state.df_freebie.loc[row_idx, "min_qty"] = new_m
          st.session_state.df_freebie.loc[row_idx, "location"] = new_l
          del st.session_state["edit_target"]
          st.success("บันทึกการแก้ไขเรียบร้อย!")
          st.rerun()
