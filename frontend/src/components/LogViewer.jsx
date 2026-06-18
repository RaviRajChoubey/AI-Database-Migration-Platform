import { FaClipboardList } from "react-icons/fa";

function LogViewer({ logs }) {

    return (

        <div
            style={{
                background: "#13294B",
                borderRadius: "12px",
                padding: "20px",
                height: "420px",
                boxShadow: "0 4px 12px rgba(0,0,0,0.3)"
            }}
        >

            <h2
                style={{
                    color: "white",
                    textAlign: "center",
                    marginBottom: "15px",
                    fontSize: "36px",
                    fontWeight: "700",
                    display: "flex",
                    justifyContent: "center",
                    alignItems: "center",
                    gap: "10px"
                }}
            >
                <FaClipboardList color="#22c55e" />
                Logs
            </h2>

            <div
                style={{
                    background: "#001233",
                    color: "#00ff7f",
                    padding: "15px",
                    height: "340px",
                    overflowY: "auto",
                    borderRadius: "10px",
                    border: "1px solid #1e3a5f"
                }}
            >

                {
                    logs.length === 0
                        ? (
                            <p
                                style={{
                                    color: "#9CA3AF",
                                    fontSize: "16px",
                                    textAlign: "center"
                                }}
                            >
                                No logs available
                            </p>
                        )
                        : (
                            logs.map((log, index) => (

                                <p
                                    key={index}
                                    style={{
                                        margin: "8px 0",
                                        fontSize: "24px",
                                        fontFamily: "monospace",
                                        lineHeight: "1.6",
                                        textAlign: "left"
                                    }}
                                >
                                    {log}
                                </p>

                            ))
                        )
                }

            </div>

        </div>

    );

}

export default LogViewer;