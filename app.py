import numpy as np
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Plano mediador 3D", layout="wide")
st.title("Plano mediador de um segmento [AB] no espaço")
st.write(
    "O **plano mediador** de [AB] é o conjunto dos pontos do espaço que estão "
    "à mesma distância de A e de B. É perpendicular a [AB] e passa pelo seu ponto médio."
)


def fmt(x):
    """Formata um número sem casas decimais desnecessárias."""
    x = round(float(x), 4)
    return str(int(x)) if x.is_integer() else f"{x:g}"


def equacao(a, b, c, d):
    """Escreve ax + by + cz + d = 0 de forma legível."""
    partes = []
    for coef, var in ((a, "x"), (b, "y"), (c, "z"), (d, "")):
        if abs(coef) < 1e-12:
            continue
        sinal = "-" if coef < 0 else "+"
        valor = abs(coef)
        texto = fmt(valor) if (var == "" or abs(valor - 1) > 1e-12) else ""
        partes.append((sinal, f"{texto}{var}"))
    if not partes:
        return "0 = 0"
    s = ("-" if partes[0][0] == "-" else "") + partes[0][1]
    for sinal, termo in partes[1:]:
        s += f" {sinal} {termo}"
    return s + " = 0"


# --- Entrada dos pontos ---
st.sidebar.header("Pontos")
st.sidebar.subheader("A")
A = np.array([
    st.sidebar.number_input("x_A", value=1.0, step=1.0),
    st.sidebar.number_input("y_A", value=2.0, step=1.0),
    st.sidebar.number_input("z_A", value=0.0, step=1.0),
])
st.sidebar.subheader("B")
B = np.array([
    st.sidebar.number_input("x_B", value=3.0, step=1.0),
    st.sidebar.number_input("y_B", value=-2.0, step=1.0),
    st.sidebar.number_input("z_B", value=4.0, step=1.0),
])

if np.allclose(A, B):
    st.error("A e B têm de ser pontos diferentes.")
    st.stop()

# --- Cálculos ---
M = (A + B) / 2           # ponto médio
n = B - A                 # vetor normal ao plano
a, b, c = n
d = -float(n @ M)         # ax + by + cz + d = 0

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Cálculos")
    st.markdown(f"**Ponto médio** M = ({fmt(M[0])}, {fmt(M[1])}, {fmt(M[2])})")
    st.markdown(f"**Vetor normal** AB = ({fmt(a)}, {fmt(b)}, {fmt(c)})")
    st.markdown("**Equação do plano mediador:**")
    coefs = np.array([a, b, c, d])
    if np.allclose(coefs, np.round(coefs)):  # simplifica coeficientes inteiros
        g = np.gcd.reduce(np.round(coefs).astype(int))
        if g > 1:
            coefs = coefs / g
    st.latex(equacao(*coefs))

    with st.expander("Como se obtém?"):
        st.markdown(
            "1. O vetor $\\vec{AB} = B - A$ é perpendicular ao plano.\n"
            "2. O plano passa no ponto médio $M = \\frac{A+B}{2}$.\n"
            "3. Para qualquer ponto $P(x,y,z)$ do plano: $\\vec{AB} \\cdot \\vec{MP} = 0$.\n\n"
            "Em alternativa: $d(P,A) = d(P,B)$, elevando ao quadrado e simplificando."
        )

    st.subheader("Verificar um ponto P")
    px = st.number_input("x_P", value=float(M[0]))
    py = st.number_input("y_P", value=float(M[1]))
    pz = st.number_input("z_P", value=float(M[2]))
    P = np.array([px, py, pz])
    dA, dB = np.linalg.norm(P - A), np.linalg.norm(P - B)
    st.write(f"d(P, A) = {dA:.3f}  |  d(P, B) = {dB:.3f}")
    if abs(dA - dB) < 1e-6:
        st.success("P pertence ao plano mediador (é equidistante de A e B).")
    else:
        st.warning("P não pertence ao plano mediador.")

# --- Gráfico 3D ---
# Dois vetores unitários perpendiculares a n para desenhar o plano à volta de M
nu = n / np.linalg.norm(n)
aux = np.array([1.0, 0, 0]) if abs(nu[0]) < 0.9 else np.array([0, 1.0, 0])
u = np.cross(nu, aux); u /= np.linalg.norm(u)
v = np.cross(nu, u)
r = max(np.linalg.norm(n), 2.0)
s, t = np.meshgrid(np.linspace(-r, r, 2), np.linspace(-r, r, 2))
X = M[0] + s * u[0] + t * v[0]
Y = M[1] + s * u[1] + t * v[1]
Z = M[2] + s * u[2] + t * v[2]

fig = go.Figure()
fig.add_trace(go.Surface(x=X, y=Y, z=Z, opacity=0.5, showscale=False,
                         colorscale=[[0, "#4c9be8"], [1, "#4c9be8"]],
                         name="Plano mediador", hoverinfo="skip"))
fig.add_trace(go.Scatter3d(x=[A[0], B[0]], y=[A[1], B[1]], z=[A[2], B[2]],
                           mode="lines", line=dict(color="black", width=5),
                           name="[AB]"))
fig.add_trace(go.Scatter3d(x=[A[0], B[0], M[0]], y=[A[1], B[1], M[1]],
                           z=[A[2], B[2], M[2]], mode="markers+text",
                           text=["A", "B", "M"], textposition="top center",
                           marker=dict(size=6, color=["red", "green", "orange"]),
                           name="Pontos"))
fig.add_trace(go.Scatter3d(x=[P[0]], y=[P[1]], z=[P[2]], mode="markers+text",
                           text=["P"], textposition="top center",
                           marker=dict(size=5, color="purple"), name="P"))
fig.update_layout(scene=dict(aspectmode="data", xaxis_title="x",
                             yaxis_title="y", zaxis_title="z"),
                  margin=dict(l=0, r=0, t=0, b=0), height=600)

with col2:
    st.plotly_chart(fig, width="stretch")
