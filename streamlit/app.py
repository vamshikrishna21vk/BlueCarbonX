# app.py - BlueCarbonX demo (Streamlit)
import streamlit as st
import pandas as pd
import os, hashlib, uuid, time
from PIL import Image
from io import BytesIO

# -----------------------
# Helpers
# -----------------------
def ensure_state():
    if 'projects' not in st.session_state:
        st.session_state['projects'] = []         # list of project dicts
    if 'wallets' not in st.session_state:
        st.session_state['wallets'] = {}         # address -> balance
    if 'next_id' not in st.session_state:
        st.session_state['next_id'] = 1

def generate_cid(title):
    s = f"{title}-{time.time()}"
    return hashlib.sha256(s.encode()).hexdigest()[:20]

def generate_nft_id():
    return uuid.uuid4().hex[:8]

def save_uploaded_file(uploaded_file, save_path):
    with open(save_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return save_path

# -----------------------
# App UI
# -----------------------
st.set_page_config(page_title="BlueCarbonX Demo", layout="wide")
st.title("BlueCarbonX — Local Demo (Streamlit)")

ensure_state()

menu = st.sidebar.selectbox("🔎 Choose page", ["Upload", "Analyze", "Mint", "Marketplace", "Dashboard", "Reset Demo"])

# ---- Reset demo
if menu == "Reset Demo":
    if st.button("Clear all demo data (session)"):
        st.session_state['projects'] = []
        st.session_state['wallets'] = {}
        st.success("Cleared demo session data.")
    st.stop()

# ---- Upload Page
if menu == "Upload":
    st.header("1) Upload project (local demo)")
    with st.form("upload_form"):
        title = st.text_input("Project title", value="Mangrove Site A")
        before = st.file_uploader("Before image (required)", type=['png','jpg','jpeg'])
        after = st.file_uploader("After image (optional)", type=['png','jpg','jpeg'])
        col1, col2 = st.columns(2)
        with col1:
            lat = st.number_input("Latitude", value=12.97, format="%.6f")
            lng = st.number_input("Longitude", value=77.59, format="%.6f")
        with col2:
            carbon = st.number_input("Carbon estimate (tCO2e)", value=12.5, step=0.1)
            wallet = st.text_input("Community wallet (optional)", placeholder="0xabc... (simulated)")
        submitted = st.form_submit_button("Save project")
    if submitted:
        if not before:
            st.error("Please upload a 'before' image.")
        else:
            pid = f"p{st.session_state['next_id']}"
            st.session_state['next_id'] += 1
            os.makedirs("uploads", exist_ok=True)
            before_path = f"uploads/{pid}_before_{before.name}"
            save_uploaded_file(before, before_path)
            after_path = ""
            if after:
                after_path = f"uploads/{pid}_after_{after.name}"
                save_uploaded_file(after, after_path)
            project = {
                "id": pid,
                "title": title,
                "before": before_path,
                "after": after_path,
                "lat": float(lat),
                "lng": float(lng),
                "carbon": float(carbon),
                "wallet": wallet if wallet else f"0x{uuid.uuid4().hex[:8]}",
                "status": "uploaded",
                "cid": "",
                "nft": None,
                "tokens": 0,
                "tokens_retired": 0,
            }
            st.session_state['projects'].append(project)
            st.success(f"Project saved: {pid}")
            st.info("Go to Analyze → Mint to continue the demo.")

# ---- Analyze Page
elif menu == "Analyze":
    st.header("2) Analyze (precomputed overlay simulation)")
    projects = st.session_state['projects']
    if not projects:
        st.info("No projects yet. Go to Upload page first.")
        st.stop()
    sel = st.selectbox("Select project", [p['id'] + " - " + p['title'] for p in projects])
    pid = sel.split(" - ")[0]
    project = next(p for p in projects if p['id'] == pid)
    st.subheader(project['title'])
    cols = st.columns(2)
    if os.path.exists(project['before']):
        cols[0].image(project['before'], caption="Before", use_column_width=True)
    else:
        cols[0].write("No before image")
    if project['after'] and os.path.exists(project['after']):
        cols[1].image(project['after'], caption="After", use_column_width=True)
    else:
        cols[1].write("No after image (demo overlay)")
    op = st.slider("Overlay intensity (simulation)", 0, 100, 50)
    st.write(f"Simulated carbon estimate: **{project['carbon']} tCO₂e** (fixed demo value)")

# ---- Mint Page
elif menu == "Mint":
    st.header("3) Mint (simulate IPFS + NFT + token issuance)")
    projects = st.session_state['projects']
    if not projects:
        st.info("No projects yet. Upload one first.")
        st.stop()
    sel = st.selectbox("Select project to mint", [p['id'] + " - " + p['title'] for p in projects])
    pid = sel.split(" - ")[0]
    project = next(p for p in projects if p['id'] == pid)
    st.write("Community wallet:", project['wallet'])
    st.write("Carbon estimate:", project['carbon'], "tCO₂e")
    if project['status'] == "minted":
        st.success("Already minted")
        st.write("CID:", project['cid'])
        st.write("NFT id:", project['nft'])
        st.write("Tokens issued:", project['tokens'])
    else:
        if st.button("Simulate pin to IPFS & Mint"):
            # simulate IPFS
            cid = generate_cid(project['title'])
            nft_id = generate_nft_id()
            tokens = int(project['carbon'] * 100)  # rule: 1 tCO2e => 100 tokens (demo)
            project['cid'] = cid
            project['nft'] = nft_id
            project['tokens'] = tokens
            project['status'] = "minted"
            # credit tokens to community wallet (simulated)
            addr = project['wallet']
            st.session_state['wallets'].setdefault(addr, 0)
            st.session_state['wallets'][addr] += tokens
            st.success(f"Minted NFT {nft_id} and issued {tokens} tokens to {addr}")
            st.write("Simulated CID:", cid)

# ---- Marketplace
elif menu == "Marketplace":
    st.header("4) Marketplace (simulate buy / retire)")
    projects = [p for p in st.session_state['projects'] if p.get('status') == 'minted']
    if not projects:
        st.info("No minted projects yet.")
        st.stop()
    for p in projects:
        st.subheader(f"{p['id']} — {p['title']}")
        col1, col2, col3 = st.columns([2,2,1])
        col1.write(f"Carbon: {p['carbon']} tCO₂e")
        col1.write(f"CID: {p['cid']}")
        col2.write(f"Tokens issued: {p['tokens']}")
        community = p['wallet']
        balance = st.session_state['wallets'].get(community, 0)
        col2.write(f"Community wallet ({community}) balance: {balance}")
        # Buy simulation
        with col3.form(f"buy_{p['id']}"):
            buyer = st.text_input("Buyer name/address", key=f"buyer_{p['id']}")
            amount = st.number_input("Amount", min_value=1, max_value=p['tokens'], value=1, key=f"amt_{p['id']}")
            buy_btn = st.form_submit_button("Buy (simulate)")
            if buy_btn:
                # simulate: reduce community balance and create buyer balance
                if st.session_state['wallets'].get(community, 0) >= amount:
                    st.session_state['wallets'][community] -= amount
                    st.session_state['wallets'].setdefault(buyer, 0)
                    st.session_state['wallets'][buyer] += amount
                    st.success(f"{buyer} bought {amount} tokens.")
                else:
                    st.error("Not enough tokens available in community wallet.")
        # Retire simulation
        with col3.form(f"retire_{p['id']}"):
            retire_addr = st.text_input("Retire from wallet", key=f"ret_{p['id']}")
            retire_amt = st.number_input("Retire amount", min_value=1, value=1, key=f"ret_amt_{p['id']}")
            retire_btn = st.form_submit_button("Retire")
            if retire_btn:
                if st.session_state['wallets'].get(retire_addr, 0) >= retire_amt:
                    st.session_state['wallets'][retire_addr] -= retire_amt
                    p['tokens_retired'] = p.get('tokens_retired', 0) + retire_amt
                    st.success(f"Retired {retire_amt} tokens from {retire_addr}.")
                else:
                    st.error("Insufficient tokens in that wallet.")

# ---- Dashboard
elif menu == "Dashboard":
    st.header("5) Dashboard & Map")
    projects = st.session_state['projects']
    if not projects:
        st.info("No projects yet.")
        st.stop()
    df_map = pd.DataFrame([{"lat": p['lat'], "lon": p['lng'], "title": p['title']} for p in projects])
    st.subheader("Map (project locations)")
    st.map(df_map.rename(columns={'lat':'lat','lon':'lon'}), zoom=6)

    # KPIs
    total_projects = len(projects)
    total_carbon = sum(p['carbon'] for p in projects)
    total_tokens = sum(p.get('tokens', 0) for p in projects)
    total_retired = sum(p.get('tokens_retired', 0) for p in projects)
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Projects", total_projects)
    k2.metric("Carbon (tCO₂e)", f"{total_carbon:.2f}")
    k3.metric("Tokens issued", total_tokens)
    k4.metric("Tokens retired", total_retired)

    st.subheader("Tokens per project")
    tbl = pd.DataFrame([{"project": p['id'], "title": p['title'], "tokens": p.get('tokens',0), "retired": p.get('tokens_retired',0)} for p in projects])
    st.dataframe(tbl)

# End of app
