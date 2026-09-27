import { useNavigate } from "react-router-dom";

function Header() {
    const navigate = useNavigate();

    return (
        <div
            className="header-bar"
            style={{
                background: "rgba(15,23,42,0.95)",
                padding: "16px clamp(16px, 3vw, 32px)",
                borderBottom: "2px solid #FF9933",
                display: "grid",
                gridTemplateColumns: "1fr auto 1fr",
                alignItems: "center",
                gap: "12px 20px",
                width: "100%",
                boxSizing: "border-box"
            }}
        >
            <div style={{ minWidth: 0, justifySelf: "start" }}>
                <h2
                    style={{
                        margin: 0,
                        fontSize: "clamp(1.1rem, 2vw, 1.4rem)",
                        fontWeight: "600",
                        color: "white"
                    }}
                >
                    🇮🇳 National Informatics Centre
                </h2>
                <p
                    style={{
                        margin: 0,
                        fontSize: "clamp(0.85rem, 1.2vw, 0.95rem)",
                        color: "#94A3B8"
                    }}
                >
                    AI Database Migration Platform
                </p>
            </div>

            <div
                style={{
                    display: "flex",
                    flexWrap: "wrap",
                    gap: "10px",
                    alignItems: "center",
                    justifyContent: "center",
                    justifySelf: "center"
                }}
            >
                <button
                    onClick={() => navigate("/")}
                    style={{
                        background: "#2563EB",
                        color: "white",
                        border: "none",
                        padding: "8px clamp(12px, 1.5vw, 18px)",
                        borderRadius: "8px",
                        cursor: "pointer",
                        fontWeight: "600",
                        fontSize: "clamp(0.9rem, 1.2vw, 1.1rem)"
                    }}
                >
                    🏠 Migration Form
                </button>

                <button
                    onClick={() => navigate("/dashboard")}
                    style={{
                        background: "#059669",
                        color: "white",
                        border: "none",
                        padding: "8px clamp(12px, 1.5vw, 18px)",
                        borderRadius: "8px",
                        cursor: "pointer",
                        fontWeight: "600",
                        fontSize: "clamp(0.9rem, 1.2vw, 1.1rem)"
                    }}
                >
                    📊 Dashboard
                </button>
            </div>

            <div style={{ justifySelf: "end" }}>
                <span
                    style={{
                        color: "#22c55e",
                        fontWeight: "600",
                        fontSize: "clamp(0.85rem, 1vw, 1rem)",
                        whiteSpace: "nowrap"
                    }}
                >
                    ● System Online
                </span>
            </div>
        </div>
    );
}

export default Header;