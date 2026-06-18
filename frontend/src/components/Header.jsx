import { useNavigate } from "react-router-dom";

function Header() {

    const navigate = useNavigate();

    return (

        <div
            style={{

                background:
                    "rgba(15,23,42,0.9)",

                padding: "20px",

                borderBottom:
                    "2px solid #FF9933",

                display: "flex",

                justifyContent:
                    "space-between",

                alignItems:
                    "center"

            }}
        >

            <div>

                <h2
                    style={{
                        margin: 0
                    }}
                >
                    🇮🇳 National Informatics Centre
                </h2>

                <p
                    style={{
                        margin: 0
                    }}
                >
                    AI Database Migration Platform
                </p>

            </div>

            <div
                style={{
                    display: "flex",
                    gap: "15px"
                }}
            >

                <button
                    onClick={() => navigate("/")}
                    style={{
                        background: "#2563EB",
                        color: "white",
                        border: "none",
                        padding: "10px 18px",
                        borderRadius: "8px",
                        cursor: "pointer",
                        fontWeight: "600",
                        fontSize: "25px"
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
                        padding: "10px 18px",
                        borderRadius: "8px",
                        cursor: "pointer",
                        fontWeight: "600",
                        fontSize: "25px"
                    }}
                >
                    📊 Dashboard
                </button>

            </div>

            <div>

                <span
                    style={{
                        color: "#22c55e"
                    }}
                >
                    ● System Online
                </span>

            </div>

        </div>

    );

}

export default Header;