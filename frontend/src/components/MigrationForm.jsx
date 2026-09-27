import { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
    testConnection,
    startMigration
}
    from "../services/api";

import { FaRobot } from "react-icons/fa";
import {
    FaDatabase,
    FaServer
} from "react-icons/fa";
import {
    FaPlay,
    FaPlug,
    FaRedo
} from "react-icons/fa";
import {
    FaBrain,
    FaExchangeAlt,
    FaClipboardCheck,
    FaChartLine
} from "react-icons/fa";

function MigrationForm() {

    const navigate = useNavigate();

    const [sourceType, setSourceType] =
        useState("mssql");

    const [sourceServer, setSourceServer] =
        useState("");

    const [sourceDatabase, setSourceDatabase] =
        useState("");

    const [sourceUser, setSourceUser] =
        useState("");

    const [sourcePassword, setSourcePassword] =
        useState("");

    const [targetHost, setTargetHost] =
        useState("");

    const [targetDatabase, setTargetDatabase] =
        useState("");

    const [targetUser, setTargetUser] =
        useState("");

    const [targetPassword, setTargetPassword] =
        useState("");

    const testButtonStyle = {
        background: "#1e40af",
        color: "white",
        border: "none",
        padding: "12px 24px",
        borderRadius: "8px",
        cursor: "pointer",
        fontWeight: "600",
        fontSize: "18px",
        boxShadow: "0 4px 10px rgba(0,0,0,0.3)"
    };

    const startButtonStyle = {
        background: "#15803d",
        color: "white",
        border: "none",
        padding: "12px 24px",
        borderRadius: "8px",
        cursor: "pointer",
        fontWeight: "600",
        fontSize: "18px",
        marginLeft: "12px",
        boxShadow: "0 4px 10px rgba(0,0,0,0.3)"
    };

    const inputStyle = {
        width: "100%",
        padding: "14px 18px",
        fontSize: "18px",
        borderRadius: "10px",
        border: "1px solid #334155",
        background: "#0F172A",
        color: "white",
        outline: "none",
        boxSizing: "border-box"
    };

    const handleStartMigration = async () => {

        try {

            const response =
                await startMigration({

                    sourceType,
                    sourceServer,
                    sourceDatabase,
                    sourceUser,
                    sourcePassword,

                    targetHost,
                    targetDatabase,
                    targetUser,
                    targetPassword

                });

            console.log(
                "Migration Response:",
                response
            );

            alert(
                "Migration Started Successfully"
            );

            navigate("/dashboard");

        }

        catch (error) {

            console.error(error);

            alert(
                "Migration Failed"
            );

        }

    };

    const featureCardStyle = {
        background: "#13294B",
        padding: "25px",
        borderRadius: "12px",
        textAlign: "center",
        color: "white",
        boxShadow: "0 4px 12px rgba(0,0,0,0.3)",
        fontSize: "20px",
        fontWeight: "600"
    };

    const statCardStyle = {

        background: "#13294B",

        padding: "20px",

        borderRadius: "12px",

        textAlign: "center",

        color: "white",

        boxShadow: "0 4px 12px rgba(0,0,0,0.3)"
    };

    const highlightCardStyle = {

        background: "#13294B",

        padding: "25px",

        borderRadius: "12px",

        color: "white",

        textAlign: "center",

        boxShadow: "0 4px 12px rgba(0,0,0,0.3)"
    };

    const handleTestConnection = async () => {

        console.log({

            sourceType,
            sourceServer,
            sourceDatabase,
            sourceUser,
            sourcePassword,

            targetHost,
            targetDatabase,
            targetUser,
            targetPassword

        });

        try {

            const result =
                await testConnection({

                    sourceType,
                    sourceServer,
                    sourceDatabase,
                    sourceUser,
                    sourcePassword,

                    targetHost,
                    targetDatabase,
                    targetUser,
                    targetPassword

                });

            alert(
                result.message
            );

        }

        catch (error) {

            console.error(error);

            alert(
                "Connection Failed"
            );

        }

    };

    const handleResumeMigration = async () => {

        try {

            const result =
                await resumeMigration();

            alert(
                result.message
            );

        }

        catch (error) {

            alert(
                "Resume failed"
            );

        }

    };

    return (

        <div
            style={{
                padding: "20px 40px",
                color: "white",
                textAlign: "center"
            }}
        >

            <div
                style={{
                    textAlign: "center",
                    marginBottom: "35px"
                }}
            >

                <h1
                    style={{
                        fontSize: "clamp(1.8rem, 4vw, 3.5rem)",
                        fontWeight: "800",
                        color: "#FFFFFF",
                        marginBottom: "10px"
                    }}
                >
                    <FaRobot
                        color="#38BDF8"
                        size={45}
                    />

                    {" "}

                    AI Database Migration Platform
                </h1>

                <h3
                    style={{
                        color: "#94A3B8",
                        fontSize: "clamp(1rem, 1.8vw, 1.35rem)",
                        fontWeight: "500"
                    }}
                >
                    Enterprise Database Migration,
                    Validation & AI-Powered Schema Analysis
                </h3>

                <h3
                    style={{
                        color: "#94a3b8",
                        marginTop: "5px",
                        fontSize: "clamp(0.9rem, 1.5vw, 1.1rem)"
                    }}
                >
                    National Informatics Centre (NIC)
                </h3>

            </div>

            <div
                style={{
                    display: "grid",
                    gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
                    gap: "15px",
                    marginBottom: "40px",
                    maxWidth: "1100px",
                    margin: "0 auto 40px auto"
                }}
            >

                <div className="hero-card">
                    🤖 AI Analysis
                </div>

                <div className="hero-card">
                    🔄 Auto Mapping
                </div>

                <div className="hero-card">
                    📊 Validation Engine
                </div>

                <div className="hero-card">
                    ⚡ Live Monitoring
                </div>

            </div>

            <div
                style={{
                    display: "grid",
                    gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
                    gap: "30px",
                    maxWidth: "1100px",
                    margin: "0 auto"
                }}
            >

                {/* Source Database */}

                <div
                    style={{
                        background: "rgba(30,41,59,0.8)",

                        backdropFilter: "blur(12px)",

                        boxShadow:
                            "0 8px 24px rgba(0,0,0,0.3)",

                        border:
                            "1px solid rgba(255,255,255,0.1)",

                        padding: "clamp(20px, 3vw, 40px)",
                        borderRadius: "12px",
                        width: "100%",
                        boxSizing: "border-box"
                    }}
                >

                    <h2
                        style={{
                            fontSize: "clamp(1.2rem, 2vw, 1.75rem)",
                            marginBottom: "20px",
                            color: "#60A5FA"
                        }}
                    >
                        <FaServer />
                        {" "}
                        Source Database
                    </h2>

                    <select

                        style={{

                            width: "100%",

                            padding: "14px",

                            fontSize: "16px",

                            borderRadius: "10px",

                            background: "#0F172A",

                            color: "white",

                            border: "1px solid #334155"

                        }}

                        value={sourceType}

                        onChange={(e) =>
                            setSourceType(e.target.value)
                        }

                    >
                        <option value="mssql">
                            MSSQL
                        </option>

                        <option value="mysql">
                            MySQL
                        </option>

                        <option value="oracle">
                            Oracle
                        </option>
                    </select>

                    <br /><br />

                    <input
                        style={inputStyle}
                        placeholder="Source Server"
                        value={sourceServer}
                        onChange={(e) =>
                            setSourceServer(e.target.value)
                        }
                    />

                    <br /><br />

                    <input
                        style={inputStyle}
                        placeholder="Source Database"
                        value={sourceDatabase}
                        onChange={(e) =>
                            setSourceDatabase(
                                e.target.value
                            )
                        }
                    />

                    <br /><br />

                    <input
                        style={inputStyle}
                        placeholder="Username"
                        value={sourceUser}
                        onChange={(e) =>
                            setSourceUser(
                                e.target.value
                            )
                        }
                    />

                    <br /><br />

                    <input
                        style={inputStyle}
                        type="password"
                        placeholder="Password"
                        value={sourcePassword}
                        onChange={(e) =>
                            setSourcePassword(
                                e.target.value
                            )
                        }
                    />

                </div>

                {/* Target Database */}

                <div
                    style={{

                        background: "rgba(30,41,59,0.8)",

                        backdropFilter: "blur(12px)",

                        boxShadow: "0 8px 24px rgba(0,0,0,0.3)",

                        border: "1px solid rgba(255,255,255,0.1)",

                        padding: "clamp(20px, 3vw, 40px)",
                        borderRadius: "12px",
                        width: "100%",
                        boxSizing: "border-box"
                    }}
                >

                    <h2
                        style={{
                            fontSize: "clamp(1.2rem, 2vw, 1.75rem)",
                            marginBottom: "20px",
                            color: "#22C55E"
                        }}
                    >
                        <FaDatabase />
                        {" "}
                        Target PostgreSQL
                    </h2>

                    <input
                        style={inputStyle}
                        placeholder="PostgreSQL Host"
                        value={targetHost}
                        onChange={(e) =>
                            setTargetHost(
                                e.target.value
                            )
                        }
                    />

                    <br /><br />

                    <input
                        style={inputStyle}
                        placeholder="Database"
                        value={targetDatabase}
                        onChange={(e) =>
                            setTargetDatabase(
                                e.target.value
                            )
                        }
                    />

                    <br /><br />

                    <input
                        style={inputStyle}
                        placeholder="Username"
                        value={targetUser}
                        onChange={(e) =>
                            setTargetUser(
                                e.target.value
                            )
                        }
                    />

                    <br /><br />

                    <input
                        style={inputStyle}
                        type="password"
                        placeholder="Password"
                        value={targetPassword}
                        onChange={(e) =>
                            setTargetPassword(
                                e.target.value
                            )
                        }
                    />

                </div>

            </div>

            <div
                style={{
                    display: "flex",
                    flexWrap: "wrap",
                    justifyContent: "center",
                    gap: "15px",
                    margin: "35px 0"
                }}
            >
                <button
                    onClick={handleTestConnection}
                    style={{
                        background: "#1e40af",
                        color: "white",
                        border: "none",
                        padding: "14px 28px",
                        borderRadius: "80px",
                        fontSize: "clamp(1rem, 1.4vw, 1.25rem)",
                        cursor: "pointer",
                        fontWeight: "600"
                    }}
                >
                    <FaPlug />
                    {" "}
                    Test Connection
                </button>

                <button
                    onClick={handleStartMigration}
                    style={{
                        background: "#15803d",
                        color: "white",
                        border: "none",
                        padding: "14px 28px",
                        borderRadius: "80px",
                        fontSize: "clamp(1rem, 1.4vw, 1.25rem)",
                        cursor: "pointer",
                        fontWeight: "600"
                    }}
                >
                    <FaPlay />
                    {" "}
                    Start Migration
                </button>

                <button
                    onClick={handleResumeMigration}
                    style={{
                        background: "#f59e0b",
                        color: "white",
                        border: "none",
                        padding: "14px 28px",
                        borderRadius: "80px",
                        fontSize: "clamp(1rem, 1.4vw, 1.25rem)",
                        cursor: "pointer",
                        fontWeight: "600"
                    }}
                >
                    <FaRedo />
                    {" "}
                    Resume Migration
                </button>
            </div>

            {/* FEATURE SECTION */}

            <div
                style={{
                    display: "grid",
                    gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))",
                    gap: "20px",
                    maxWidth: "1200px",
                    margin: "40px auto"
                }}
            >

                <div className="highlight-card">
                    <h3 style={{ fontSize: "clamp(1.1rem, 1.5vw, 1.4rem)", marginBottom: "8px" }}>🚀 Fast Migration</h3>

                    <p style={{ fontSize: "clamp(0.85rem, 1.1vw, 1rem)", margin: 0 }}>
                        Migrate millions of records efficiently.
                    </p>
                </div>

                <div className="highlight-card">
                    <h3 style={{ fontSize: "clamp(1.1rem, 1.5vw, 1.4rem)", marginBottom: "8px" }}>🛡 Data Validation</h3>

                    <p style={{ fontSize: "clamp(0.85rem, 1.1vw, 1rem)", margin: 0 }}>
                        Automatic validation and checksum reports.
                    </p>
                </div>

                <div className="highlight-card">
                    <h3 style={{ fontSize: "clamp(1.1rem, 1.5vw, 1.4rem)", marginBottom: "8px" }}>🤖 AI Recommendations</h3>

                    <p style={{ fontSize: "clamp(0.85rem, 1.1vw, 1rem)", margin: 0 }}>
                        Intelligent schema analysis and suggestions.
                    </p>
                </div>

            </div>

            <div
                style={{
                    display: "grid",
                    gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
                    gap: "20px",
                    marginTop: "40px",
                    maxWidth: "1200px",
                    marginLeft: "auto",
                    marginRight: "auto"
                }}
            >

                <div style={featureCardStyle}>
                    <FaBrain
                        size={36}
                        color="#A855F7"
                    />
                    <h3 style={{ fontSize: "clamp(1rem, 1.3vw, 1.2rem)", marginTop: "10px" }}>AI Schema Analysis</h3>
                </div>

                <div style={featureCardStyle}>
                    <FaExchangeAlt
                        size={36}
                        color="#22C55E"
                    />
                    <h3 style={{ fontSize: "clamp(1rem, 1.3vw, 1.2rem)", marginTop: "10px" }}>Auto Migration</h3>
                </div>

                <div style={featureCardStyle}>
                    <FaClipboardCheck
                        size={36}
                        color="#F59E0B"
                    />
                    <h3 style={{ fontSize: "clamp(1rem, 1.3vw, 1.2rem)", marginTop: "10px" }}>Validation Reports</h3>
                </div>

                <div style={featureCardStyle}>
                    <FaChartLine
                        size={36}
                        color="#38BDF8"
                    />
                    <h3 style={{ fontSize: "clamp(1rem, 1.3vw, 1.2rem)", marginTop: "10px" }}>Real-Time Monitoring</h3>
                </div>

            </div>

            <div
                style={{
                    textAlign: "center",
                    marginTop: "50px",
                    marginBottom: "60px"
                }}
            >

                <h2
                    style={{
                        color: "#38BDF8",
                        fontSize: "clamp(1.4rem, 2.5vw, 2.2rem)"
                    }}
                >
                    Migration Workflow
                </h2>

                <div
                    style={{
                        display: "flex",
                        flexWrap: "wrap",
                        justifyContent: "center",
                        gap: "15px",
                        marginTop: "25px",
                        fontSize: "clamp(1rem, 1.8vw, 1.5rem)",
                        color: "white"
                    }}
                >

                    <span>🔌 Connect</span>

                    <span>➜</span>

                    <span>🤖 Analyze</span>

                    <span>➜</span>

                    <span>🚀 Migrate</span>

                    <span>➜</span>

                    <span>✅ Validate</span>

                    <span>➜</span>

                    <span>📊 Reports</span>

                </div>

            </div>

        </div>

    );

}

export default MigrationForm;