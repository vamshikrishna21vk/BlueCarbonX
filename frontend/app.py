# app.py - BlueCarbonX Streamlit Frontend (with Marketplace Buy/Sell/Retire)
import io
import datetime
from PIL import Image, ImageDraw, ImageFont
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import pydeck as pdk

API_BASE = "http://localhost:3001/api"


# --- Helper for certificate generation ---
def generate_certificate_image(title, tokenId, owner, before_img=None, after_img=None):
    W, H = 1200, 800
    bg = Image.new("RGB", (W, H), color=(255, 255, 255))
    draw = ImageDraw.Draw(bg)

    try:
        font_title = ImageFont.truetype("arial.ttf", 40)
        font_sub = ImageFont.truetype("arial.ttf", 20)
    except:
        font_title = ImageFont.load_default()
        font_sub = ImageFont.load_default()

    # Header
    draw.rectangle([(0, 0), (W, 120)], fill=(2, 85, 120))
    draw.text((30, 30), "BlueCarbonX Restoration Certificate",
              fill=(255, 255, 255), font=font_title)

    # Project info
    draw.text((50, 160), f"Project: {title}", fill=(0, 0, 0), font=font_sub)
    draw.text((50, 200), f"Certificate ID: {tokenId}", fill=(
        0, 0, 0), font=font_sub)
    draw.text((50, 240), f"Owner: {owner}", fill=(0, 0, 0), font=font_sub)

    # Optional thumbnails
    thumb_y = 320
    if before_img:
        b = Image.open(before_img).resize((350, 250))
        bg.paste(b, (50, thumb_y))
        draw.text((50, thumb_y+255), "Before", fill=(0, 0, 0), font=font_sub)
    if after_img:
        a = Image.open(after_img).resize((350, 250))
        bg.paste(a, (450, thumb_y))
        draw.text((450, thumb_y+255), "After", fill=(0, 0, 0), font=font_sub)

    # Footer
    draw.text((50, H-80), f"Issued: {datetime.date.today().isoformat()}",
              fill=(80, 80, 80), font=font_sub)

    buf = io.BytesIO()
    bg.save(buf, format="PNG")
    buf.seek(0)
    return buf


# --- Page Config ---
st.set_page_config(page_title="BlueCarbonX", layout="wide")

# --- Sidebar Navigation ---
st.sidebar.title("🌊 BlueCarbonX")
page = st.sidebar.radio("Navigation", [
    "Upload", "Dashboard", "Projects", "Marketplace", "Map", "Analyze", "Wallet"
])

# --- Upload Page ---
if page == "Upload":
    st.title("📤 Upload New Project")

    with st.form("upload_form"):
        title = st.text_input("Project Title")
        carbon = st.number_input(
            "Estimated Carbon Restored (tCO₂)", min_value=1)
        lat = st.number_input("Latitude", value=12.97, format="%.6f")
        lng = st.number_input("Longitude", value=77.59, format="%.6f")
        before_img = st.file_uploader("Before Image", type=["jpg", "png"])
        after_img = st.file_uploader("After Image", type=["jpg", "png"])

        submitted = st.form_submit_button("Upload Project")
        if submitted:
            try:
                payload = {"title": title, "carbon": carbon,
                           "lat": lat, "lng": lng}
                r = requests.post(f"{API_BASE}/projects", json=payload)
                st.success(f"✅ Project created: {r.json()['id']}")
            except Exception as e:
                st.error(f"Upload failed: {e}")


# --- Dashboard Page ---
elif page == "Dashboard":
    st.title("📊 Dashboard Overview")
    try:
        stats = requests.get(f"{API_BASE}/stats").json()

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Projects", stats["totalProjects"])
        col2.metric("Total Carbon", f"{stats['totalCarbon']} tCO₂")
        col3.metric("Tokens Issued", stats["totalTokens"])
        col4.metric("Tokens Retired", stats["totalRetired"])

        st.subheader("📈 Token Distribution")
        df = pd.DataFrame(stats["tokenDistribution"])
        if not df.empty:
            fig = px.bar(df, x="title", y=["tokens", "retired"], barmode="group",
                         title="Tokens vs Retired Tokens")
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("🟢 Project Status Breakdown")
        fig2 = px.pie(names=list(stats["byStatus"].keys()),
                      values=list(stats["byStatus"].values()),
                      title="Uploaded vs Minted")
        st.plotly_chart(fig2, use_container_width=True)

    except Exception as e:
        st.error(f"Error loading stats: {e}")


# --- Projects Page ---
elif page == "Projects":
    st.title("🌱 Projects")
    try:
        projects = requests.get(f"{API_BASE}/projects").json()
        if projects:
            for p in projects:
                with st.expander(f"{p['title']} ({p['status']})"):
                    st.write(f"Carbon: {p['carbon']} tCO₂")
                    st.write(f"Wallet: {p['wallet']}")

                    if p["status"] != "minted":
                        if st.button(f"Mint {p['title']}", key=p["id"]):
                            r = requests.post(f"{API_BASE}/mint/{p['id']}")
                            res = r.json()
                            st.success(res)

                            # Generate & show certificate
                            cert_buf = generate_certificate_image(
                                title=p["title"],
                                tokenId=res.get("certificateId", "N/A"),
                                owner=p.get("wallet", "0xDemoWallet")
                            )
                            st.image(cert_buf, caption="🎉 Restoration Certificate",
                                     use_column_width=True)
                            st.download_button(
                                "⬇️ Download Certificate",
                                data=cert_buf.getvalue(),
                                file_name=f"certificate_{p['id']}.png",
                                mime="image/png",
                            )
        else:
            st.info("No projects yet.")
    except Exception as e:
        st.error(f"Error: {e}")


# --- Marketplace Page ---
elif page == "Marketplace":
    st.title("🛒 Marketplace")
    try:
        projects = requests.get(f"{API_BASE}/projects").json()
        for p in projects:
            if p["status"] == "minted":
                with st.expander(f"{p['title']} - {p['tokens']} tokens available"):
                    st.write(f"Retired: {p.get('tokens_retired', 0)}")

                    amount = st.number_input(
                        f"Amount for {p['title']}", min_value=1, key=f"amt_{p['id']}"
                    )
                    col1, col2, col3 = st.columns(3)

                    # Buy button
                    if col1.button("Buy", key=f"buy_{p['id']}"):
                        r = requests.post(
                            f"{API_BASE}/marketplace/buy/{p['id']}",
                            json={"amount": int(amount)},
                        )
                        st.success(r.json())

                    # Sell button (NEW)
                    if col2.button("Sell", key=f"sell_{p['id']}"):
                        r = requests.post(
                            f"{API_BASE}/marketplace/sell/{p['id']}",
                            json={"amount": int(amount)},
                        )
                        st.success(r.json())

                    # Retire button
                    if col3.button("Retire", key=f"retire_{p['id']}"):
                        r = requests.post(
                            f"{API_BASE}/marketplace/retire/{p['id']}",
                            json={"amount": int(amount)},
                        )
                        st.success(r.json())
    except Exception as e:
        st.error(f"Error: {e}")


# --- Map Page ---
elif page == "Map":
    st.title("🗺 Project Map")
    try:
        geojson = requests.get(f"{API_BASE}/map").json()
        features = geojson.get("features", [])
        if features:
            df = pd.json_normalize(features)
            df["lat"] = df["geometry.coordinates"].apply(lambda x: x[1])
            df["lng"] = df["geometry.coordinates"].apply(lambda x: x[0])

            st.pydeck_chart(
                pdk.Deck(
                    map_style="mapbox://styles/mapbox/dark-v10",
                    initial_view_state=pdk.ViewState(
                        latitude=df["lat"].mean(),
                        longitude=df["lng"].mean(),
                        zoom=3,
                        pitch=0,
                    ),
                    layers=[
                        pdk.Layer(
                            "ScatterplotLayer",
                            data=df,
                            get_position="[lng, lat]",
                            get_fill_color="[0, 180, 200, 200]",
                            get_radius=50000,
                            pickable=True,
                        )
                    ],
                    tooltip={
                        "text": "{properties.title}\nCarbon: {properties.carbon} tCO₂"},
                )
            )
        else:
            st.info("No projects with coordinates yet.")
    except Exception as e:
        st.error(f"Error loading map: {e}")


# --- Analyze Page ---
elif page == "Analyze":
    st.title("🤖 AI Simulation - Before/After Analysis")

    before = st.file_uploader("Upload Before Image", type=[
                              "jpg", "png"], key="before_ai")
    after = st.file_uploader("Upload After Image", type=[
                             "jpg", "png"], key="after_ai")

    if before and after:
        col1, col2 = st.columns(2)
        with col1:
            st.image(Image.open(before), caption="Before")
        with col2:
            st.image(Image.open(after), caption="After")

        st.success(
            "✅ AI simulation overlay complete (static demo). Carbon restored: ~12 tCO₂")


# --- Wallet Page ---
elif page == "Wallet":
    st.title("🔐 Wallet Viewer")
    addr = st.text_input("Enter wallet address (0x...)", value="")
    if st.button("Check Wallet"):
        if not addr:
            st.error("Enter address first")
        else:
            try:
                r = requests.get(f"{API_BASE}/balance/{addr}")
                data = r.json()

                st.subheader("ERC20 Balance")
                st.write(f"{int(data['tokens']):,} BCT (raw units)")

                st.subheader("Certificates owned")
                if data.get("certificates"):
                    for c in data["certificates"]:
                        st.markdown(
                            f"**{c['title']}** — tokenId: `{c['tokenId']}` — project: `{c['projectId']}`"
                        )
                        if st.button(f"View Certificate #{c['tokenId']}", key=f"cert_{c['tokenId']}"):
                            cert_img = generate_certificate_image(
                                title=c['title'], tokenId=c['tokenId'], owner=addr
                            )
                            st.image(
                                cert_img, caption=f"Certificate #{c['tokenId']}", use_column_width=True)
                else:
                    st.info("No certificates found for this wallet.")
            except Exception as e:
                st.error(f"Error: {e}")


# --- Marketplace Page ---
elif page == "Marketplace":
    st.title("🛒 Marketplace")

    try:
        projects = requests.get(f"{API_BASE}/projects").json()

        if not projects:
            st.info("No projects yet.")
        else:
            for p in projects:
                if p["status"] == "minted":
                    with st.expander(f"{p['title']} - {p['tokens']} tokens available"):
                        st.write(f"Retired: {p.get('tokens_retired', 0)}")
                        amount = st.number_input(
                            f"Amount for {p['title']}",
                            min_value=1,
                            key=f"amt_{p['id']}"
                        )
                        col1, col2, col3 = st.columns(3)

                        # --- Buy Tokens ---
                        if col1.button("Buy", key=f"buy_{p['id']}"):
                            r = requests.post(
                                f"{API_BASE}/marketplace/buy/{p['id']}",
                                json={"amount": int(amount)},
                            )
                            st.success(r.json())

                        # --- Retire Tokens ---
                        if col2.button("Retire", key=f"retire_{p['id']}"):
                            r = requests.post(
                                f"{API_BASE}/marketplace/retire/{p['id']}",
                                json={"amount": int(amount)},
                            )
                            st.success(r.json())

                        # --- Sell Tokens (new) ---
                        if col3.button("Sell", key=f"sell_{p['id']}"):
                            r = requests.post(
                                f"{API_BASE}/marketplace/sell/{p['id']}",
                                json={"amount": int(amount)},
                            )
                            st.success(r.json())
    except Exception as e:
        st.error(f"Error: {e}")
