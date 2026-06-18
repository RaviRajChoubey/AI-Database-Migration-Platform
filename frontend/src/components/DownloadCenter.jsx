import {
    FaFileAlt,
    FaClipboardCheck,
    FaHistory,
    FaDatabase,
    FaUndo,
    FaCogs,
    FaPuzzlePiece
} from "react-icons/fa";

function DownloadCenter() {

    const cardStyle = {
        background: "#182845",
        color: "white",
        border: "none",
        borderRadius: "12px",
        padding: "20px",
        cursor: "pointer",
        fontSize: "28px",
        fontWeight: "600",
        width: "100%",
        minHeight: "90px",
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        alignItems: "center",
        gap: "10px",
        boxShadow: "0 4px 12px rgba(0,0,0,0.35)",
        transition: "0.3s"
    };

    return (

        <div
            style={{
                background: "#13294B",
                padding: "25px",
                borderRadius: "12px",
                marginTop: "38px",
                boxShadow: "0 4px 12px rgba(0,0,0,0.3)"
            }}
        >

            <h2
                style={{
                    textAlign: "center",
                    marginBottom: "25px",
                    fontSize: "38px",
                    fontWeight: "700",
                    color: "white"
                }}
            >
                📥 Download Center
            </h2>

            <div
                style={{
                    display: "grid",
                    gridTemplateColumns:
                        "repeat(auto-fit,minmax(220px,1fr))",
                    gap: "20px"
                }}
            >

                <a
                    href="http://localhost:8000/migration/download/validation"
                    target="_blank"
                    style={{ textDecoration: "none" }}
                >
                    <button style={cardStyle}>
                        <FaClipboardCheck
                            size={38}
                            color="#22c55e"
                        />
                        Validation Report
                    </button>
                </a>

                <a
                    href="http://localhost:8000/migration/download/audit"
                    target="_blank"
                    style={{ textDecoration: "none" }}
                >
                    <button style={cardStyle}>
                        <FaHistory
                            size={38}
                            color="#60a5fa"
                        />
                        Audit Report
                    </button>
                </a>

                <a
                    href="http://localhost:8000/migration/download/checksum"
                    target="_blank"
                    style={{ textDecoration: "none" }}
                >
                    <button style={cardStyle}>
                        <FaDatabase
                            size={38}
                            color="#f59e0b"
                        />
                        Checksum Report
                    </button>
                </a>

                <a
                    href="http://localhost:8000/migration/download/reconciliation"
                    target="_blank"
                    style={{ textDecoration: "none" }}
                >
                    <button style={cardStyle}>
                        <FaFileAlt
                            size={38}
                            color="#a855f7"
                        />
                        Reconciliation Report
                    </button>
                </a>

                <a
                    href="http://127.0.0.1:8000/migration/download-report"
                    style={{ textDecoration: "none" }}
                >
                    <button style={cardStyle}>
                        <FaFileAlt
                            size={38}
                            color="#38bdf8"
                        />
                        Migration Report
                    </button>
                </a>

                <a
                    href="http://127.0.0.1:8000/migration/download-rollback"
                    style={{ textDecoration: "none" }}
                >
                    <button style={cardStyle}>
                        <FaUndo
                            size={38}
                            color="#ef4444"
                        />
                        Rollback Script
                    </button>
                </a>

                <a
                    href="http://127.0.0.1:8000/migration/download-procedures"
                    style={{ textDecoration: "none" }}
                >
                    <button style={cardStyle}>
                        <FaCogs
                            size={38}
                            color="#eab308"
                        />
                        Procedure Report
                    </button>
                </a>

                <a
                    href="http://127.0.0.1:8000/migration/download-functions"
                    style={{ textDecoration: "none" }}
                >
                    <button style={cardStyle}>
                        <FaPuzzlePiece
                            size={38}
                            color="#10b981"
                        />
                        Function Report
                    </button>
                </a>

            </div>

        </div>

    );

}

export default DownloadCenter;