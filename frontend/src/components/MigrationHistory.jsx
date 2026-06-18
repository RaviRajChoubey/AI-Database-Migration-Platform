import { useEffect, useState } from "react";
import { FaHistory } from "react-icons/fa";

import { getHistory }
    from "../services/api";

function MigrationHistory() {

    const [history, setHistory] =
        useState([]);

    useEffect(() => {

        loadHistory();

    }, []);

    const loadHistory = async () => {

        try {

            const data =
                await getHistory();

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
                    fontSize: "28px",
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
                                    padding: "14px",
                                    fontSize: "28px"
                                }}
                            >
                                ID
                            </th>

                            <th
                                style={{
                                    padding: "14px",
                                    fontSize: "28px"
                                }}
                            >
                                Source
                            </th>

                            <th
                                style={{
                                    padding: "14px",
                                    fontSize: "28px"
                                }}
                            >
                                Target
                            </th>

                            <th
                                style={{
                                    padding: "14px",
                                    fontSize: "28px"
                                }}
                            >
                                Tables
                            </th>

                            <th
                                style={{
                                    padding: "14px",
                                    fontSize: "28px"
                                }}
                            >
                                Rows
                            </th>

                            <th
                                style={{
                                    padding: "14px",
                                    fontSize: "28px"
                                }}
                            >
                                Status
                            </th>

                            <th
                                style={{
                                    padding: "14px",
                                    fontSize: "28px"
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
                                        key={item.id}
                                        style={{
                                            borderBottom:
                                                "1px solid #1e3a5f"
                                        }}
                                    >

                                        <td
                                            style={{
                                                padding: "12px",
                                                textAlign: "center",
                                                fontSize: "24px"
                                            }}
                                        >
                                            {item.id}
                                        </td>

                                        <td
                                            style={{
                                                padding: "12px",
                                                textAlign: "center",
                                                fontSize: "24px"
                                            }}
                                        >
                                            {item.source_db}
                                        </td>

                                        <td
                                            style={{
                                                padding: "12px",
                                                textAlign: "center",
                                                fontSize: "24px"
                                            }}
                                        >
                                            {item.target_db}
                                        </td>

                                        <td
                                            style={{
                                                padding: "12px",
                                                textAlign: "center",
                                                fontSize: "24px"
                                            }}
                                        >
                                            {item.tables_count}
                                        </td>

                                        <td
                                            style={{
                                                padding: "12px",
                                                textAlign: "center",
                                                fontSize: "24px"
                                            }}
                                        >
                                            {item.rows_count}
                                        </td>

                                        <td
                                            style={{
                                                padding: "12px",
                                                textAlign: "center",
                                                fontWeight: "700",
                                                color:
                                                    item.status === "SUCCESS"
                                                        ? "#22c55e"
                                                        : "#ef4444",
                                                fontSize: "24px"
                                            }}
                                        >
                                            {item.status}
                                        </td>

                                        <td
                                            style={{
                                                padding: "12px",
                                                textAlign: "center",
                                                fontSize: "24px"
                                            }}
                                        >
                                            {item.migration_time}
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