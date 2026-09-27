import { useEffect, useState } from "react";
import { FaHistory } from "react-icons/fa";

import { getMigrationHistory } from "../services/api";

function MigrationHistory() {

    const [history, setHistory] =
        useState([]);

    useEffect(() => {

        loadHistory();

    }, []);

    const loadHistory = async () => {

        try {

            const data = await getMigrationHistory();

            console.log(data);

            setHistory(data);

        }

        catch (error) {

            console.error(error);

        }

    };

    return (

        <div
            style={{
                background: "#13294B",
                borderRadius: "12px",
                padding: "20px",
                height: "420px",
                boxShadow:
                    "0 4px 12px rgba(0,0,0,0.3)"
            }}
        >

            <h2
                style={{
                    color: "white",
                    textAlign: "center",
                    marginBottom: "15px",
                    fontSize: "clamp(1.1rem, 1.8vw, 1.5rem)",
                    fontWeight: "700",
                    display: "flex",
                    justifyContent: "center",
                    alignItems: "center",
                    gap: "10px"
                }}
            >
                <FaHistory color="#60A5FA" />
                Migration History
            </h2>

            <div
                className="table-wrapper"
                style={{
                    height: "330px",
                    overflowY: "auto"
                }}
            >

                <table
                    style={{
                        width: "100%",
                        borderCollapse: "collapse",
                        color: "white"
                    }}
                >

                    <thead>

                        <tr
                            style={{
                                background: "#1E3A5F",
                                position: "sticky",
                                top: 0
                            }}
                        >

                            <th
                                style={{
                                    padding: "10px",
                                    fontSize: "clamp(0.85rem, 1.1vw, 1rem)"
                                }}
                            >
                                ID
                            </th>

                            <th
                                style={{
                                    padding: "10px",
                                    fontSize: "clamp(0.85rem, 1.1vw, 1rem)"
                                }}
                            >
                                Source
                            </th>

                            <th
                                style={{
                                    padding: "10px",
                                    fontSize: "clamp(0.85rem, 1.1vw, 1rem)"
                                }}
                            >
                                Target
                            </th>

                            <th
                                style={{
                                    padding: "10px",
                                    fontSize: "clamp(0.85rem, 1.1vw, 1rem)"
                                }}
                            >
                                Tables
                            </th>

                            <th
                                style={{
                                    padding: "10px",
                                    fontSize: "clamp(0.85rem, 1.1vw, 1rem)"
                                }}
                            >
                                Rows
                            </th>

                            <th
                                style={{
                                    padding: "10px",
                                    fontSize: "clamp(0.85rem, 1.1vw, 1rem)"
                                }}
                            >
                                Status
                            </th>

                            <th
                                style={{
                                    padding: "10px",
                                    fontSize: "clamp(0.85rem, 1.1vw, 1rem)"
                                }}
                            >
                                Time
                            </th>

                        </tr>

                    </thead>

                    <tbody>

                        {

                            history.map(

                                (item) => (

                                    <tr
                                        key={item.audit_id}
                                        style={{
                                            borderBottom: "1px solid #1e3a5f"
                                        }}
                                    >

                                        <td style={{ padding: "10px", textAlign: "center", fontSize: "clamp(0.8rem, 1vw, 0.95rem)" }}>
                                            {item.audit_id}
                                        </td>

                                        <td style={{ padding: "10px", textAlign: "center", fontSize: "clamp(0.8rem, 1vw, 0.95rem)" }}>
                                            {item.source_db}
                                        </td>

                                        <td style={{ padding: "10px", textAlign: "center", fontSize: "clamp(0.8rem, 1vw, 0.95rem)" }}>
                                            {item.target_db}
                                        </td>

                                        <td style={{ padding: "10px", textAlign: "center", fontSize: "clamp(0.8rem, 1vw, 0.95rem)" }}>
                                            {item.tables_processed}
                                        </td>

                                        <td style={{ padding: "10px", textAlign: "center", fontSize: "clamp(0.8rem, 1vw, 0.95rem)" }}>
                                            {item.rows_processed}
                                        </td>

                                        <td
                                            style={{
                                                padding: "10px",
                                                textAlign: "center",
                                                fontWeight: "700",
                                                color:
                                                    item.validation_status === "PASSED"
                                                        ? "#22c55e"
                                                        : "#ef4444",
                                                fontSize: "clamp(0.8rem, 1vw, 0.95rem)"
                                            }}
                                        >
                                            {item.validation_status}
                                        </td>

                                        <td style={{ padding: "10px", textAlign: "center", fontSize: "clamp(0.8rem, 1vw, 0.95rem)" }}>
                                            {new Date(item.completed_at).toLocaleString()}
                                        </td>

                                    </tr>

                                )

                            )

                        }

                    </tbody>

                </table>

            </div>

        </div>

    );

}

export default MigrationHistory;