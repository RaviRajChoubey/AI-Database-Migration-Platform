import { useEffect, useState } from "react";
import "./Dashboard.css";
import StatsCard from "./StatsCard";
import ProgressBar from "./ProgressBar";
import LogViewer from "./LogViewer";
import MigrationHistory from "./MigrationHistory";
import DownloadCenter from "./DownloadCenter";
import { useNavigate } from "react-router-dom";
import { FaArrowLeft } from "react-icons/fa";

import {
    FaCalendarAlt,
    FaClock,
    FaTasks,
    FaCheckCircle,
    FaTimesCircle,
    FaDatabase,
    FaRobot,
    FaHistory,
    FaDownload,
    FaShieldAlt,
    FaChartLine,
    FaBrain,
    FaLink,
    FaEdit,
    FaClipboardList,
    FaBalanceScale,
    FaFingerprint,
    FaChartPie,
    FaTable,
    FaEye,
    FaCogs,
    FaCode,
    FaExchangeAlt
}
    from "react-icons/fa";

import {
    MdDeleteForever,
    MdPauseCircleFilled
} from "react-icons/md";

import {
    getReport,
    getLogs,
    getProgress,
    getSchemaAnalysis,
    getValidationReport,
    getProfiles
} from "../services/api";

import {
    getChecksumReport
}
    from "../services/api";

import {
    getReconciliationReport
}
    from "../services/api";

import {
    getMetricsReport,
    getAuditTrail
} from "../services/api";

import {

    getMigrationHistory

} from "../services/api";

import {
    createSchedule
} from "../services/api";

import {
    getSchedulerLogs
} from "../services/api";

function Dashboard() {

    const [progressData, setProgressData] =
        useState(null);

    const [report, setReport] =
        useState(null);

    const [validationReport, setValidationReport] =
        useState(null);

    const [checksumReport, setChecksumReport] =
        useState(null);

    const [migrationHistory, setMigrationHistory] =
        useState([]);

    const [
        reconciliationReport,
        setReconciliationReport
    ] = useState(null);

    const [logs, setLogs] =
        useState([]);

    const [analysis, setAnalysis] =
        useState(null);

    const [metrics, setMetrics] =
        useState(null);

    const [auditTrail, setAuditTrail] =
        useState([]);

    const [scheduleName, setScheduleName] =
        useState("");

    const [scheduleType, setScheduleType] =
        useState("Daily");

    const [schedules, setSchedules] =
        useState([]);

    const [scheduledDate, setScheduledDate] =
        useState("");

    const [scheduledTime, setScheduledTime] =
        useState("");

    const [weekday, setWeekday] =
        useState("Sunday");

    const [profiles, setProfiles] =
        useState([]);

    const [selectedProfile, setSelectedProfile] =
        useState(null);

    const [retryCount, setRetryCount] =
        useState(0);

    console.log(
        "PROFILES:",
        profiles
    );

    useEffect(() => {

        console.log(
            "PROFILES UPDATED:",
            profiles
        );

    }, [profiles]);

    useEffect(() => {

        console.log(
            "SELECTED PROFILE:",
            selectedProfile
        );

    }, [selectedProfile]);

    const [schedulerLogs, setSchedulerLogs] =
        useState([]);

    console.log(
        "SCHEDULER LOGS:",
        schedulerLogs
    );

    const loadDashboardData = async () => {

        try {

            const metricsData =
                await getMetricsReport();

            const auditData =
                await getAuditTrail();

            setMetrics(metricsData);

            setAuditTrail(auditData);

        }

        catch (error) {

            console.error(error);

        }

    };

    const loadReconciliationReport =
        async () => {

            try {

                const data =
                    await getReconciliationReport();

                setReconciliationReport(data);

            }

            catch (error) {

                console.error(error);

            }

        };

    const loadChecksumReport = async () => {

        try {

            const data =
                await getChecksumReport();

            setChecksumReport(data);

        }

        catch (error) {

            console.error(error);

        }

    };

    const loadValidationReport = async () => {

        try {

            const data =
                await getValidationReport();

            setValidationReport(data);

        }

        catch (error) {

            console.error(error);

        }

    };

    const loadMigrationHistory =
        async () => {

            try {

                const data =

                    await getMigrationHistory();

                setMigrationHistory(data);

            }

            catch (error) {

                console.error(error);

            }

        };

    const loadSchedules = async () => {

        const response = await fetch(
            "http://localhost:8000/migration/schedules"
        );

        const data = await response.json();

        setSchedules(data);

    };

    const handleScheduleMigration = async () => {

        console.log({
            schedule_name: scheduleName,
            schedule_type: scheduleType,
            scheduled_date: scheduledDate,
            scheduled_time: scheduledTime,
            weekday: weekday,
            retry_count: retryCount,
            profile_id: selectedProfile
        });

        if (!selectedProfile) {

            alert(
                "Please select a Migration Profile"
            );

            console.log(
                "PROFILE NOT SELECTED:",
                selectedProfile
            );

            return;
        }

        try {

            const payload = {

                schedule_name: scheduleName,

                schedule_type: scheduleType,

                scheduled_date:
                    scheduledDate || null,

                scheduled_time:
                    scheduledTime,

                weekday:
                    weekday,

                retry_count:
                    retryCount,

                profile_id:
                    selectedProfile

            };

            console.log(
                "SENDING PAYLOAD:",
                payload
            );

            const response =
                await createSchedule(
                    payload
                );

            console.log(
                "SUCCESS RESPONSE:",
                response
            );

            alert(
                "Migration Scheduled Successfully"
            );

            loadSchedules();

        }

        catch (error) {

            console.error(
                "ERROR RESPONSE:",
                error.response
            );

            console.log(
                JSON.stringify(
                    error.response?.data,
                    null,
                    2
                )
            );

            alert(
                "Failed To Create Schedule"
            );

        }

    };

    const loadSchedulerLogs =
        async () => {

            try {

                const data =
                    await getSchedulerLogs();

                console.log(
                    "API DATA:",
                    data
                );

                setSchedulerLogs(
                    data
                );

            }

            catch (error) {

                console.error(
                    "SCHEDULER ERROR:",
                    error
                );

            }

        };

    const loadProfiles = async () => {

        try {

            const response =
                await getProfiles();

            console.log(
                "PROFILE API:",
                response
            );

            console.log(
                "IS ARRAY:",
                Array.isArray(response)
            );

            console.log(
                "PROFILE LENGTH:",
                response?.length
            );

            setProfiles(response);

            console.log(
                "SET PROFILES CALLED"
            );

        }

        catch (error) {

            console.error(
                "LOAD PROFILES ERROR:",
                error
            );

        }

    };

    useEffect(() => {
        loadReport();
        loadProgress();
        loadAnalysis();
        loadDashboardData();
        loadValidationReport();
        loadChecksumReport();
        loadReconciliationReport();
        loadMigrationHistory();
        loadSchedules();
        loadProfiles();
        loadSchedulerLogs();
    }, []);

    useEffect(() => {

        const interval = setInterval(() => {

            loadProgress();

        }, 2000);

        return () =>
            clearInterval(interval);

    }, []);

    const loadReport = async () => {

        try {

            const data =
                await getReport();

            setReport(data);

            const logData =
                await getLogs();

            setLogs(
                logData.logs
            );

        }

        catch (error) {

            console.error(error);

        }

    };

    const loadAnalysis = async () => {

        try {

            const data =
                await getSchemaAnalysis();

            setAnalysis(
                data
            );

        }

        catch (error) {

            console.error(error);

        }

    };

    const toggleSchedule = async (id) => {

        await fetch(

            `http://localhost:8000/migration/schedule/toggle/${id}`,

            {
                method: "PUT"
            }

        );

        loadSchedules();

    };

    const disableSchedule = async (id) => {

        try {

            await fetch(
                `http://localhost:8000/migration/schedule/toggle/${id}`,
                {
                    method: "PUT"
                }
            );

            loadSchedules();

        }

        catch (error) {

            console.error(error);

        }

    };

    const deleteSchedule = async (id) => {

        try {

            await fetch(
                `http://localhost:8000/migration/schedule/${id}`,
                {
                    method: "DELETE"
                }
            );

            loadSchedules();

        }

        catch (error) {

            console.error(error);

        }

    };

    const loadProgress = async () => {

        try {

            const data =
                await getProgress();

            console.log(
                "PROGRESS DATA:",
                data
            );

            setProgressData(
                data
            );

        }

        catch (error) {

            console.error(error);

        }

    };

    if (!report || !analysis) {
        return <h2>Loading...</h2>;
    }

    return (

        <div
            style={{
                background: "#0B1628",
                // background: "black",
                minHeight: "100vh",
                width: "100%",
                padding: "20px",
                boxSizing: "border-box"
            }}
        >

            <div
                style={{
                    display: "grid",
                    gridTemplateColumns: "repeat(4, 1fr)",
                    gap: "20px",
                    marginBottom: "30px"
                }}
            >

                <div className="kpi-card">
                    <h3
                        style={{
                            fontSize: "32px",
                            display: "flex",
                            alignItems: "center",
                            gap: "10px",
                            color: "#E2E8F0"
                        }}
                    >
                        <FaExchangeAlt color="#38BDF8" size={24} />
                        Total Migrations
                    </h3>

                    <h1
                        style={{
                            fontSize: "52px",
                            marginTop: "10px",
                            color: "white"
                        }}
                    >
                        {migrationHistory.length}
                    </h1>
                </div>

                <div className="kpi-card">
                    <h3
                        style={{
                            fontSize: "32px",
                            display: "flex",
                            alignItems: "center",
                            gap: "10px",
                            color: "#E2E8F0"
                        }}
                    >
                        <FaDatabase color="#22C55E" size={24} />
                        Rows Migrated
                    </h3>

                    <h1
                        style={{
                            fontSize: "52px",
                            marginTop: "10px",
                            color: "white"
                        }}
                    >
                        {
                            migrationHistory.reduce(
                                (sum, row) =>
                                    sum + (row.rows_count || 0),
                                0
                            )
                        }
                    </h1>
                </div>

                <div className="kpi-card">
                    <h3
                        style={{
                            fontSize: "32px",
                            display: "flex",
                            alignItems: "center",
                            gap: "10px",
                            color: "#E2E8F0"
                        }}
                    >
                        <FaCheckCircle color="#10B981" size={24} />
                        Validation
                    </h3>

                    <h1
                        style={{
                            fontSize: "38px",
                            marginTop: "10px",
                            color: "#22C55E"
                        }}
                    >
                        SUCCESS
                    </h1>
                </div>

                <div className="kpi-card">
                    <h3
                        style={{
                            fontSize: "32px",
                            display: "flex",
                            alignItems: "center",
                            gap: "10px",
                            color: "#E2E8F0"
                        }}
                    >
                        <FaCalendarAlt color="#F59E0B" size={24} />
                        Schedules
                    </h3>

                    <h1
                        style={{
                            fontSize: "52px",
                            marginTop: "10px",
                            color: "white"
                        }}
                    >
                        {schedules.length}
                    </h1>
                </div>

            </div>

            <div
                style={{
                    padding: "20px",
                    color: "white"
                }}
            >

                <h1
                    style={{
                        textAlign: "center",
                        fontSize: "52px",
                        fontWeight: "800",
                        color: "white",
                        marginBottom: "30px",
                        display: "flex",
                        justifyContent: "center",
                        alignItems: "center",
                        gap: "15px"
                    }}
                >
                    <FaChartLine
                        color="#38BDF8"
                        size={42}
                    />
                    Migration Dashboard
                </h1>

                <div
                    style={{
                        display: "grid",
                        gridTemplateColumns: "repeat(6, 1fr)",
                        gap: "0px",
                        background: "#13294B",
                        borderRadius: "14px",
                        overflow: "hidden",
                        boxShadow:
                            "0 4px 12px rgba(0,0,0,0.3)",
                        marginBottom: "40px",
                    }}
                >

                    <StatsCard
                        title={
                            <>
                                <FaTable
                                    color="#60A5FA"
                                    size={22}
                                />
                                {" "}
                                Tables
                            </>
                        }
                        value={report.tables}
                    />

                    <StatsCard
                        title={
                            <>
                                <FaDatabase
                                    color="#22C55E"
                                    size={22}
                                />
                                {" "}
                                Rows
                            </>
                        }
                        value={report.rows}
                    />

                    <StatsCard
                        title={
                            <>
                                <FaEye
                                    color="#F59E0B"
                                    size={22}
                                />
                                {" "}
                                Views
                            </>
                        }
                        value={report.views}
                    />

                    <StatsCard
                        title={
                            <>
                                <FaCogs
                                    color="#A855F7"
                                    size={22}
                                />
                                {" "}
                                Procedures
                            </>
                        }
                        value={report.procedures}
                    />

                    <StatsCard
                        title={
                            <>
                                <FaCode
                                    color="#EC4899"
                                    size={22}
                                />
                                {" "}
                                Functions
                            </>
                        }
                        value={report.functions}
                    />

                    <StatsCard
                        title={
                            <>
                                <FaShieldAlt
                                    color="#14B8A6"
                                    size={22}
                                />
                                {" "}
                                AI Risk
                            </>
                        }
                        value={
                            analysis?.risk_analysis
                                ?.overall_risk || "LOW"
                        }
                    />

                </div>

                <h2
                    style={{
                        textAlign: "center",
                        fontSize: "42px",
                        fontWeight: "700",
                        marginBottom: "20px",
                        color: "white",
                        display: "flex",
                        justifyContent: "center",
                        alignItems: "center",
                        gap: "12px"
                    }}
                >
                    📈 Migration Progress
                </h2>

                <ProgressBar
                    progress={progressData?.progress || 0}
                />

                <div
                    style={{
                        display: "grid",
                        gridTemplateColumns: "2fr 1fr",
                        gap: "20px",
                        marginTop: "38px",
                        alignItems: "stretch"
                    }}
                >

                    {/* LEFT SIDE */}

                    <div
                        style={{
                            background: "#13294B",
                            padding: "20px",
                            borderRadius: "12px",
                            minHeight: "420px"
                        }}
                    >

                        <h2
                            style={{
                                textAlign: "center",
                                marginBottom: "20px",
                                fontSize: "38px",
                                fontWeight: "700",
                                color: "white",
                                display: "flex",
                                justifyContent: "center",
                                alignItems: "center",
                                gap: "10px"
                            }}
                        >
                            <FaClipboardList
                                style={{
                                    marginRight: "10px",
                                    color: "#60A5FA"
                                }}
                            />
                            Audit Trail
                        </h2>

                        <div
                            style={{
                                maxHeight: "320px",
                                overflowY: "auto",
                                marginTop: "20px"
                            }}
                        >

                            <table
                                style={{
                                    width: "100%",
                                    color: "white",
                                    borderCollapse: "collapse"
                                }}
                            >

                                <thead>

                                    <tr
                                        style={{
                                            background: "#1E3A5F"
                                        }}
                                    >

                                        <th
                                            style={{
                                                padding: "16px",
                                                fontSize: "32px",
                                                fontWeight: "700"
                                            }}
                                        >
                                            ID
                                        </th>

                                        <th
                                            style={{
                                                padding: "16px",
                                                fontSize: "32px",
                                                fontWeight: "700"
                                            }}
                                        >
                                            Source
                                        </th>

                                        <th
                                            style={{
                                                padding: "16px",
                                                fontSize: "32px",
                                                fontWeight: "700"
                                            }}
                                        >
                                            Target
                                        </th>

                                        <th
                                            style={{
                                                padding: "16px",
                                                fontSize: "32px",
                                                fontWeight: "700"
                                            }}
                                        >
                                            Status
                                        </th>

                                    </tr>

                                </thead>

                                <tbody>

                                    {

                                        auditTrail.map(item => (

                                            <tr
                                                key={item.audit_id}
                                                style={{
                                                    textAlign: "center"
                                                }}
                                            >

                                                <td
                                                    style={{
                                                        padding: "16px",
                                                        fontSize: "28px",
                                                        fontWeight: "500"
                                                    }}
                                                >
                                                    {item.audit_id}
                                                </td>

                                                <td
                                                    style={{
                                                        padding: "16px",
                                                        fontSize: "28px",
                                                        fontWeight: "500"
                                                    }}
                                                >
                                                    {item.source_db}
                                                </td>

                                                <td
                                                    style={{
                                                        padding: "16px",
                                                        fontSize: "28px",
                                                        fontWeight: "500"
                                                    }}
                                                >
                                                    {item.target_db}
                                                </td>

                                                <td
                                                    style={{
                                                        padding: "16px",
                                                        fontSize: "28px",
                                                        fontWeight: "500",
                                                        color:
                                                            item.validation_status ===
                                                                "PASSED"
                                                                ? "#22c55e"
                                                                : "#ef4444",
                                                        fontWeight: "bold"
                                                    }}
                                                >
                                                    {
                                                        item.validation_status
                                                    }
                                                </td>

                                            </tr>

                                        ))

                                    }

                                </tbody>

                            </table>

                        </div>

                    </div>

                    {/* RIGHT SIDE */}

                    <div
                        style={{
                            background: "#13294B",
                            padding: "25px",
                            borderRadius: "12px",
                            minHeight: "420px",
                            boxShadow: "0 4px 12px rgba(0,0,0,0.3)"
                        }}
                    >

                        <h2
                            style={{
                                textAlign: "center",
                                marginBottom: "20px",
                                fontSize: "38px",
                                fontWeight: "700",
                                color: "white",
                                display: "flex",
                                justifyContent: "center",
                                alignItems: "center",
                                gap: "10px"
                            }}
                        >
                            <FaChartPie
                                style={{
                                    marginRight: "10px",
                                    color: "#22C55E"
                                }}
                            />
                            Migration Summary
                        </h2>

                        <div
                            style={{
                                display: "grid",
                                gap: "18px"
                            }}
                        >

                            <div
                                style={{
                                    display: "flex",
                                    justifyContent: "space-between",
                                    fontSize: "18px"
                                }}
                            >
                                <span
                                    style={{
                                        fontSize: "32px",
                                        fontWeight: "600",
                                        marginBottom: "10px"
                                    }} Migration >Total Migrations</span>
                                <strong
                                    style={{ fontSize: "32px" }}>{migrationHistory.length}</strong>
                            </div>

                            <div
                                style={{
                                    display: "flex",
                                    justifyContent: "space-between",
                                    fontSize: "18px"
                                }}
                            >
                                <span
                                    style={{
                                        fontSize: "32px",
                                        fontWeight: "600",
                                        marginBottom: "10px"
                                    }}>Rows Migrated</span>

                                <strong
                                    style={{ fontSize: "32px" }}
                                >
                                    {
                                        migrationHistory.reduce(
                                            (sum, row) =>
                                                sum + (row.rows_count || 0),
                                            0
                                        )
                                    }
                                </strong>
                            </div>

                            <div
                                style={{
                                    display: "flex",
                                    justifyContent: "space-between",
                                    fontSize: "18px"
                                }}
                            >
                                <span
                                    style={{
                                        fontSize: "32px",
                                        fontWeight: "600",
                                        marginBottom: "10px"
                                    }}>Validation</span>

                                <strong
                                    style={{
                                        color: "#22c55e",
                                        fontSize: "32px"
                                    }}
                                >
                                    SUCCESS
                                </strong>
                            </div>

                            <div
                                style={{
                                    display: "flex",
                                    justifyContent: "space-between",
                                    fontSize: "18px"
                                }}
                            >
                                <span
                                    style={{
                                        fontSize: "32px",
                                        fontWeight: "600",
                                        marginBottom: "10px"
                                    }}> AI Risk</span>

                                <strong
                                    style={{
                                        fontSize: "32px",
                                        color:
                                            analysis?.risk_analysis?.overall_risk === "HIGH"
                                                ? "#ef4444"
                                                : analysis?.risk_analysis?.overall_risk === "MEDIUM"
                                                    ? "#f59e0b"
                                                    : "#22c55e"

                                    }}
                                >
                                    {
                                        analysis?.risk_analysis?.overall_risk || "LOW"
                                    }
                                </strong>
                            </div>

                            <div
                                style={{
                                    display: "flex",
                                    justifyContent: "space-between",
                                    fontSize: "18px"
                                }}
                            >
                                <span
                                    style={{
                                        fontSize: "32px",
                                        fontWeight: "600",
                                        marginBottom: "10px"
                                    }}>Schedules</span>

                                <strong
                                    style={{ fontSize: "32px" }}>
                                    {schedules.length}
                                </strong>
                            </div>

                            <div
                                style={{
                                    display: "flex",
                                    justifyContent: "space-between",
                                    fontSize: "18px"
                                }}
                            >
                                <span
                                    style={{
                                        fontSize: "32px",
                                        fontWeight: "600",
                                        marginBottom: "10px"
                                    }}>Status</span>

                                <strong
                                    style={{
                                        fontSize: "32px",
                                        color:
                                            progressData?.status === "COMPLETED"
                                                ? "#22c55e"
                                                : "#f59e0b"
                                    }}
                                >
                                    {
                                        progressData?.status ||
                                        "IDLE"
                                    }
                                </strong>
                            </div>

                        </div>

                    </div>

                </div>

                <div
                    style={{
                        display: "grid",
                        gridTemplateColumns: "1fr 1fr 1fr",
                        gap: "20px",
                        marginTop: "38px",
                        alignItems: "start"
                    }}
                >

                    {/* VALIDATION */}

                    {
                        validationReport && (

                            <div
                                style={{
                                    background: "#13294B",
                                    padding: "20px",
                                    borderRadius: "12px",
                                    boxShadow: "0 4px 12px rgba(0,0,0,0.3)",
                                    height: "100%"
                                }}
                            >

                                <h2
                                    style={{
                                        textAlign: "center",
                                        marginBottom: "20px",
                                        fontSize: "38px",
                                        fontWeight: "700",
                                        color: "white",
                                        display: "flex",
                                        justifyContent: "center",
                                        alignItems: "center",
                                        gap: "10px"
                                    }}
                                >
                                    <FaCheckCircle
                                        style={{
                                            marginRight: "10px",
                                            color: "#22C55E"
                                        }}
                                    />
                                    Validation Summary
                                </h2>

                                <div
                                    style={{
                                        textAlign: "center",
                                        marginBottom: "15px",
                                        fontSize: "28px"
                                    }}
                                >
                                    Overall Status:

                                    <span
                                        style={{
                                            marginLeft: "8px",
                                            fontSize: "28px",
                                            color:
                                                validationReport.overall_status === "PASSED"
                                                    ? "#22c55e"
                                                    : "#ef4444",
                                            fontWeight: "bold"
                                        }}
                                    >
                                        {validationReport.overall_status}
                                    </span>

                                </div>

                                <table
                                    style={{
                                        width: "100%",
                                        color: "white",
                                        borderCollapse: "collapse"
                                    }}
                                >

                                    <thead>

                                        <tr
                                            style={{
                                                background: "#1E3A5F"
                                            }}
                                        >

                                            <th
                                                style={{
                                                    padding: "16px",
                                                    fontSize: "32px",
                                                    fontWeight: "700"
                                                }}
                                            >
                                                Table
                                            </th>
                                            <th
                                                style={{
                                                    padding: "16px",
                                                    fontSize: "32px",
                                                    fontWeight: "700"
                                                }}
                                            >
                                                Source
                                            </th>
                                            <th
                                                style={{
                                                    padding: "16px",
                                                    fontSize: "32px",
                                                    fontWeight: "700"
                                                }}
                                            >
                                                Target
                                            </th>
                                            <th
                                                style={{
                                                    padding: "16px",
                                                    fontSize: "32px",
                                                    fontWeight: "700"
                                                }}
                                            >
                                                Status
                                            </th>

                                        </tr>

                                    </thead>

                                    <tbody>

                                        {
                                            validationReport.tables.map(row => (

                                                <tr
                                                    key={row.table}
                                                    style={{
                                                        textAlign: "center"
                                                    }}
                                                >

                                                    <td
                                                        style={{
                                                            padding: "16px",
                                                            fontSize: "28px",
                                                            fontWeight: "500"
                                                        }}
                                                    >{row.table}</td>

                                                    <td
                                                        style={{
                                                            padding: "16px",
                                                            fontSize: "28px",
                                                            fontWeight: "500"
                                                        }}
                                                    >{row.source_rows}</td>

                                                    <td
                                                        style={{
                                                            padding: "16px",
                                                            fontSize: "28px",
                                                            fontWeight: "500"
                                                        }}
                                                    >{row.target_rows}</td>

                                                    <td
                                                        style={{
                                                            padding: "16px",
                                                            fontSize: "28px",
                                                            fontWeight: "500",
                                                            color:
                                                                row.status === "PASSED"
                                                                    ? "#22c55e"
                                                                    : "#ef4444",
                                                            fontWeight: "bold"
                                                        }}
                                                    >
                                                        {row.status}
                                                    </td>

                                                </tr>

                                            ))
                                        }

                                    </tbody>

                                </table>

                            </div>

                        )
                    }

                    {/* CHECKSUM */}

                    {
                        checksumReport && (

                            <div
                                style={{
                                    background: "#13294B",
                                    padding: "20px",
                                    borderRadius: "12px",
                                    boxShadow: "0 4px 12px rgba(0,0,0,0.3)",
                                    height: "100%"
                                }}
                            >

                                <h2
                                    style={{
                                        textAlign: "center",
                                        marginBottom: "20px",
                                        fontSize: "38px",
                                        fontWeight: "700",
                                        color: "white",
                                        display: "flex",
                                        justifyContent: "center",
                                        alignItems: "center",
                                        gap: "10px"
                                    }}
                                >
                                    <FaFingerprint
                                        style={{
                                            marginRight: "10px",
                                            color: "#F59E0B"
                                        }}
                                    />
                                    Checksum Validation
                                </h2>

                                <table
                                    style={{
                                        width: "100%",
                                        color: "white",
                                        borderCollapse: "collapse"
                                    }}
                                >

                                    <thead>

                                        <tr
                                            style={{
                                                background: "#1E3A5F"
                                            }}
                                        >

                                            <th
                                                style={{
                                                    padding: "16px",
                                                    fontSize: "32px",
                                                    fontWeight: "700"
                                                }}
                                            >Table</th>
                                            <th
                                                style={{
                                                    padding: "16px",
                                                    fontSize: "32px",
                                                    fontWeight: "700"
                                                }}
                                            >Status</th>

                                        </tr>

                                    </thead>

                                    <tbody>

                                        {
                                            checksumReport.map(row => (

                                                <tr
                                                    key={row.table}
                                                    style={{
                                                        textAlign: "center"
                                                    }}
                                                >

                                                    <td
                                                        style={{
                                                            padding: "16px",
                                                            fontSize: "28px",
                                                            fontWeight: "500"
                                                        }}
                                                    >{row.table}</td>

                                                    <td
                                                        style={{
                                                            padding: "16px",
                                                            fontSize: "28px",
                                                            fontWeight: "500",
                                                            color:
                                                                row.status === "PASS"
                                                                    ? "#22c55e"
                                                                    : "#ef4444",
                                                            fontWeight: "bold"
                                                        }}
                                                    >
                                                        {row.status}
                                                    </td>

                                                </tr>

                                            ))
                                        }

                                    </tbody>

                                </table>

                            </div>

                        )
                    }

                    {/* RECONCILIATION */}

                    {
                        reconciliationReport && (

                            <div
                                style={{
                                    background: "#13294B",
                                    padding: "20px",
                                    borderRadius: "12px",
                                    boxShadow: "0 4px 12px rgba(0,0,0,0.3)",
                                    height: "100%"
                                }}
                            >

                                <h2
                                    style={{
                                        textAlign: "center",
                                        marginBottom: "20px",
                                        fontSize: "38px",
                                        fontWeight: "700",
                                        color: "white",
                                        display: "flex",
                                        justifyContent: "center",
                                        alignItems: "center",
                                        gap: "10px"
                                    }}
                                >
                                    <FaBalanceScale
                                        style={{
                                            marginRight: "10px",
                                            color: "#A855F7"
                                        }}
                                    />
                                    Reconciliation Report
                                </h2>

                                {
                                    reconciliationReport.length === 1 &&
                                        reconciliationReport[0].status === "PASS"

                                        ? (

                                            <div
                                                style={{
                                                    textAlign: "center",
                                                    color: "#22c55e",
                                                    fontSize: "34px",
                                                    fontWeight: "bold",
                                                    marginTop: "150px"
                                                }}
                                            >
                                                ✓ No Issues Found
                                            </div>

                                        )

                                        : (

                                            <table
                                                style={{
                                                    width: "100%",
                                                    color: "white",
                                                    borderCollapse: "collapse"
                                                }}
                                            >

                                                <thead>

                                                    <tr
                                                        style={{
                                                            background: "#1E3A5F"
                                                        }}
                                                    >

                                                        <th
                                                            style={{
                                                                padding: "16px",
                                                                fontSize: "32px",
                                                                fontWeight: "700"
                                                            }}
                                                        >Table</th>
                                                        <th
                                                            style={{
                                                                padding: "16px",
                                                                fontSize: "32px",
                                                                fontWeight: "700"
                                                            }}
                                                        >Issue</th>

                                                    </tr>

                                                </thead>

                                                <tbody>

                                                    {
                                                        reconciliationReport.map(row => (

                                                            <tr
                                                                key={row.primary_key}
                                                            >

                                                                <td
                                                                    style={{
                                                                        padding: "16px",
                                                                        fontSize: "28px",
                                                                        fontWeight: "500"
                                                                    }}
                                                                >{row.table}</td>

                                                                <td
                                                                    style={{
                                                                        padding: "16px",
                                                                        fontSize: "28px",
                                                                        fontWeight: "500",
                                                                        color: "#ef4444"
                                                                    }}
                                                                >
                                                                    {row.issue}
                                                                </td>

                                                            </tr>

                                                        ))
                                                    }

                                                </tbody>

                                            </table>

                                        )
                                }

                            </div>

                        )
                    }

                </div>

                <br />

                <div
                    style={{
                        display: "grid",
                        gridTemplateColumns: "1fr 1fr 1fr",
                        gap: "20px",
                        marginTop: "38px",
                        alignItems: "start"
                    }}
                >

                    {/* Scheduler */}
                    <div
                        style={{
                            background: "#13294B",
                            padding: "30px",
                            borderRadius: "12px",
                            minHeight: "520px",
                            boxShadow: "0 4px 12px rgba(0,0,0,0.3)"
                        }}
                    >
                        <h2
                            style={{
                                display: "flex",
                                justifyContent: "center",
                                alignItems: "center",
                                gap: "10px",
                                marginBottom: "25px",
                                color: "white",
                                fontSize: "38px",
                                fontWeight: "700"
                            }}
                        >
                            <FaCalendarAlt
                                size={38}
                                color="#60a5fa" />
                            Migration Scheduler
                        </h2>

                        <div
                            style={{
                                display: "grid",
                                gap: "18px"
                            }}
                        >

                            <input
                                type="text"
                                placeholder="Schedule Name"
                                value={scheduleName}
                                onChange={(e) =>
                                    setScheduleName(e.target.value)
                                }
                                style={{
                                    padding: "16px",
                                    fontSize: "20px",
                                    borderRadius: "8px",
                                    border: "none",
                                    background: "#1E3A5F",
                                    color: "white"
                                }}
                            />

                            <select
                                value={scheduleType}
                                onChange={(e) =>
                                    setScheduleType(e.target.value)
                                }
                                style={{
                                    padding: "16px",
                                    fontSize: "20px",
                                    borderRadius: "8px",
                                    background: "#1E3A5F",
                                    color: "white"
                                }}
                            >
                                <option>One Time</option>
                                <option>Daily</option>
                                <option>Weekly</option>
                                <option>Monthly</option>
                                <option>Yearly</option>
                            </select>

                            {(scheduleType === "One Time" ||
                                scheduleType === "Monthly" ||
                                scheduleType === "Yearly") && (

                                    <input
                                        type="date"
                                        value={scheduledDate}
                                        onChange={(e) =>
                                            setScheduledDate(e.target.value)
                                        }
                                        style={{
                                            padding: "16px",
                                            fontSize: "20px",
                                            fontWeight: "600",
                                            borderRadius: "8px",
                                            background: "#1E3A5F",
                                            color: "white"
                                        }}
                                    />

                                )}

                            {scheduleType === "Weekly" && (

                                <select
                                    value={weekday}
                                    onChange={(e) =>
                                        setWeekday(e.target.value)
                                    }
                                    style={{
                                        padding: "16px",
                                        fontSize: "20px",
                                        borderRadius: "8px",
                                        background: "#1E3A5F",
                                        color: "white"
                                    }}
                                >
                                    <option>Sunday</option>
                                    <option>Monday</option>
                                    <option>Tuesday</option>
                                    <option>Wednesday</option>
                                    <option>Thursday</option>
                                    <option>Friday</option>
                                    <option>Saturday</option>
                                </select>

                            )}

                            <input
                                type="time"
                                value={scheduledTime}
                                onChange={(e) =>
                                    setScheduledTime(e.target.value)
                                }
                                style={{
                                    padding: "16px",
                                    fontSize: "20px",
                                    fontWeight: "600",
                                    borderRadius: "8px",
                                    background: "#1E3A5F",
                                    color: "white"
                                }}
                            />

                            <select
                                value={selectedProfile || ""}
                                onChange={(e) =>
                                    setSelectedProfile(
                                        e.target.value
                                            ? parseInt(e.target.value)
                                            : null
                                    )
                                }
                                style={{
                                    padding: "16px",
                                    fontSize: "20px",
                                    borderRadius: "8px",
                                    background: "#1E3A5F",
                                    color: "white"
                                }}
                            >
                                <option value="">
                                    Select Migration Profile
                                </option>

                                {profiles.map(profile => (
                                    <option
                                        key={profile.profile_id}
                                        value={profile.profile_id}
                                    >
                                        {profile.profile_name}
                                    </option>
                                ))}
                            </select>

                            <select
                                value={retryCount}
                                onChange={(e) =>
                                    setRetryCount(
                                        Number(e.target.value)
                                    )
                                }
                                style={{
                                    padding: "16px",
                                    fontSize: "20px",
                                    borderRadius: "8px",
                                    background: "#1E3A5F",
                                    color: "white"
                                }}
                            >
                                <option value={0}>No Retry</option>
                                <option value={1}>1 Retry</option>
                                <option value={3}>3 Retries</option>
                                <option value={5}>5 Retries</option>
                            </select>

                            <button
                                onClick={handleScheduleMigration}
                                style={{
                                    padding: "18px",
                                    border: "none",
                                    borderRadius: "8px",
                                    background: "#22c55e",
                                    color: "white",
                                    fontWeight: "700",
                                    fontSize: "30px",
                                    cursor: "pointer"
                                }}
                            >
                                Schedule Migration
                            </button>

                        </div>
                    </div>

                    {/* Monitoring */}
                    <div
                        style={{
                            background: "#13294B",
                            padding: "25px",
                            borderRadius: "12px",
                            minHeight: "520px"
                        }}
                    >

                        <h2
                            style={{
                                display: "flex",
                                justifyContent: "center",
                                alignItems: "center",
                                gap: "10px",
                                color: "white",
                                fontSize: "38px",
                                marginBottom: "20px"
                            }}
                        >
                            <FaClock
                                size={38}
                                color="#60a5fa" />
                            Scheduler Monitoring
                        </h2>

                        <div
                            style={{
                                height: "420px",
                                overflowY: "auto"
                            }}
                        >

                            <table
                                style={{
                                    width: "100%",
                                    color: "white",
                                    borderCollapse: "collapse",
                                    fontSize: "30px"
                                }}
                            >

                                <thead>

                                    <tr
                                        style={{
                                            background: "#1E3A5F"
                                        }}
                                    >
                                        <th style={{ padding: "16px" }}>ID</th>
                                        <th style={{ padding: "16px" }}>Schedule</th>
                                        <th style={{ padding: "16px" }}>Status</th>
                                        <th style={{ padding: "16px" }}>Duration</th>
                                    </tr>

                                </thead>

                                <tbody>

                                    {
                                        schedulerLogs.map(log => (

                                            <tr key={log[0]}>

                                                <td
                                                    style={{
                                                        padding: "16px",
                                                        textAlign: "center"
                                                    }}
                                                >
                                                    {log[0]}
                                                </td>

                                                <td
                                                    style={{
                                                        padding: "16px",
                                                        textAlign: "center"
                                                    }}
                                                >
                                                    {log[1]}
                                                </td>

                                                <td
                                                    style={{
                                                        padding: "16px",
                                                        textAlign: "center",
                                                        color:
                                                            log[3] === "SUCCESS"
                                                                ? "#22c55e"
                                                                : "#ef4444",
                                                        fontWeight: "bold"
                                                    }}
                                                >
                                                    {log[3]}
                                                </td>

                                                <td
                                                    style={{
                                                        padding: "16px",
                                                        textAlign: "center"
                                                    }}
                                                >
                                                    {log[4]} sec
                                                </td>

                                            </tr>

                                        ))
                                    }

                                </tbody>

                            </table>

                        </div>

                    </div>

                    {/* Jobs */}
                    <div
                        style={{
                            background: "#13294B",
                            padding: "25px",
                            borderRadius: "12px",
                            minHeight: "520px"
                        }}
                    >

                        <h2
                            style={{
                                display: "flex",
                                justifyContent: "center",
                                alignItems: "center",
                                gap: "10px",
                                color: "white",
                                fontSize: "38px",
                                marginBottom: "20px"
                            }}
                        >
                            <FaTasks
                                size={38}
                                color="#60a5fa" />
                            Scheduled Jobs
                        </h2>

                        <div
                            style={{
                                height: "420px",
                                overflowY: "auto"
                            }}
                        >

                            <table
                                style={{
                                    width: "100%",
                                    borderCollapse: "collapse",
                                    color: "white",
                                    fontSize: "30px"
                                }}
                            >

                                <thead>

                                    <tr
                                        style={{
                                            background: "#1E3A5F"
                                        }}
                                    >
                                        <th style={{ padding: "16px" }}>ID</th>
                                        <th style={{ padding: "16px" }}>Name</th>
                                        <th style={{ padding: "16px" }}>Type</th>
                                        <th style={{ padding: "16px" }}>Time</th>
                                        <th style={{ padding: "16px" }}>Status</th>
                                        <th style={{ padding: "16px" }}>Actions</th>
                                    </tr>

                                </thead>

                                <tbody>

                                    {
                                        schedules.map(schedule => (

                                            <tr key={schedule.schedule_id}>

                                                <td
                                                    style={{
                                                        padding: "16px",
                                                        textAlign: "center"
                                                    }}
                                                >
                                                    {schedule.schedule_id}
                                                </td>

                                                <td
                                                    style={{
                                                        padding: "16px",
                                                        textAlign: "center"
                                                    }}
                                                >
                                                    {schedule.schedule_name}
                                                </td>

                                                <td
                                                    style={{
                                                        padding: "16px",
                                                        textAlign: "center"
                                                    }}
                                                >
                                                    {schedule.schedule_type}
                                                </td>

                                                <td
                                                    style={{
                                                        padding: "16px",
                                                        textAlign: "center"
                                                    }}
                                                >
                                                    {schedule.scheduled_time}
                                                </td>

                                                <td
                                                    style={{
                                                        padding: "16px",
                                                        textAlign: "center",
                                                        color:
                                                            schedule.is_active
                                                                ? "#22c55e"
                                                                : "#ef4444",
                                                        fontWeight: "bold"
                                                    }}
                                                >
                                                    {
                                                        schedule.is_active
                                                            ? "ACTIVE"
                                                            : "DISABLED"
                                                    }
                                                </td>

                                                <td
                                                    style={{
                                                        textAlign: "center"
                                                    }}
                                                >

                                                    <div
                                                        style={{
                                                            display: "flex",
                                                            justifyContent: "center",
                                                            gap: "8px"
                                                        }}
                                                    >

                                                        <div
                                                            style={{
                                                                display: "flex",
                                                                justifyContent: "center",
                                                                gap: "10px"
                                                            }}
                                                        >

                                                            <button
                                                                onClick={() => disableSchedule(schedule.schedule_id)}
                                                                title="Disable Schedule"
                                                                style={{
                                                                    background: "#F59E0B",
                                                                    border: "none",
                                                                    color: "white",
                                                                    width: "40px",
                                                                    height: "40px",
                                                                    borderRadius: "8px",
                                                                    cursor: "pointer",
                                                                    display: "flex",
                                                                    alignItems: "center",
                                                                    justifyContent: "center",
                                                                    fontSize: "18px",
                                                                    boxShadow: "0 2px 8px rgba(0,0,0,0.3)"
                                                                }}
                                                            >
                                                                <MdPauseCircleFilled size={40} />
                                                            </button>

                                                            <button
                                                                onClick={() => deleteSchedule(schedule.schedule_id)}
                                                                title="Delete Schedule"
                                                                style={{
                                                                    background: "#EF4444",
                                                                    border: "none",
                                                                    color: "white",
                                                                    width: "40px",
                                                                    height: "40px",
                                                                    borderRadius: "8px",
                                                                    cursor: "pointer",
                                                                    display: "flex",
                                                                    alignItems: "center",
                                                                    justifyContent: "center",
                                                                    fontSize: "18px",
                                                                    boxShadow: "0 2px 8px rgba(0,0,0,0.3)"
                                                                }}
                                                            >
                                                                <MdDeleteForever size={40} />
                                                            </button>

                                                        </div>

                                                    </div>

                                                </td>

                                            </tr>

                                        ))
                                    }

                                </tbody>

                            </table>

                        </div>

                    </div>

                </div>

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
                            display: "flex",
                            justifyContent: "center",
                            alignItems: "center",
                            gap: "12px",
                            fontSize: "38px",
                            fontWeight: "700",
                            color: "white",
                            marginBottom: "20px"
                        }}
                    >
                        <FaBrain color="#38BDF8" />
                        AI Summary
                    </h2>

                    <div
                        style={{
                            display: "grid",
                            gridTemplateColumns: "repeat(4,1fr)",
                            gap: "20px",
                            textAlign: "center"
                        }}
                    >

                        <div>
                            <div style={{ fontSize: "32px" }}>🔗</div>
                            <div style={{ fontSize: "30px", marginTop: "8px" }}>
                                Foreign Keys Detected
                            </div>
                        </div>

                        <div>
                            <div style={{ fontSize: "32px" }}>✏️</div>
                            <div style={{ fontSize: "30px", marginTop: "8px" }}>
                                Rename Suggestions
                            </div>
                        </div>

                        <div>
                            <div style={{ fontSize: "32px" }}>✅</div>
                            <div style={{ fontSize: "30px", marginTop: "8px" }}>
                                Schema Safe
                            </div>
                        </div>

                        <div>
                            <div style={{ fontSize: "32px" }}>🚀</div>
                            <div style={{ fontSize: "30px", marginTop: "8px" }}>
                                Ready For Migration
                            </div>
                        </div>

                    </div>

                </div>

                {/* FOREIGN KEY + RENAME GRID */}

                <div
                    style={{
                        display: "grid",
                        gridTemplateColumns: "1fr 1fr",
                        gap: "20px",
                        marginTop: "38px"
                    }}
                >

                    {/* FOREIGN KEYS */}

                    <div
                        style={{
                            background: "#13294B",
                            padding: "25px",
                            borderRadius: "12px",
                            minHeight: "220px"
                        }}
                    >

                        <h2
                            style={{
                                display: "flex",
                                alignItems: "center",
                                gap: "10px",
                                fontSize: "38px",
                                fontWeight: "700",
                                color: "white",
                                marginBottom: "20px"
                            }}
                        >
                            <FaLink color="#60A5FA" />
                            Foreign Keys
                        </h2>

                        {
                            analysis?.foreign_keys?.length === 0
                                ? (
                                    <p
                                        style={{
                                            fontSize: "30px"
                                        }}
                                    >
                                        No foreign keys detected
                                    </p>
                                )
                                : (
                                    analysis?.foreign_keys?.map(
                                        (fk, index) => (

                                            <p
                                                key={index}
                                                style={{
                                                    fontSize: "30px",
                                                    marginBottom: "12px",
                                                    lineHeight: "1.7"
                                                }}
                                            >

                                                🔗 {fk.suggestion}

                                            </p>

                                        )
                                    )
                                )
                        }

                    </div>

                    {/* RENAME SUGGESTIONS */}

                    <div
                        style={{
                            background: "#13294B",
                            padding: "25px",
                            borderRadius: "12px",
                            minHeight: "220px"
                        }}
                    >

                        <h2
                            style={{
                                display: "flex",
                                alignItems: "center",
                                gap: "10px",
                                fontSize: "38px",
                                fontWeight: "700",
                                color: "white",
                                marginBottom: "20px"
                            }}
                        >
                            <FaEdit color="#F59E0B" />
                            Rename Suggestions
                        </h2>

                        {
                            analysis?.rename_suggestions?.length === 0
                                ? (
                                    <p
                                        style={{
                                            fontSize: "30px"
                                        }}
                                    >
                                        No rename suggestions
                                    </p>
                                )
                                : (
                                    analysis?.rename_suggestions?.map(
                                        (item, index) => (

                                            <p
                                                key={index}
                                                style={{
                                                    fontSize: "30px",
                                                    marginBottom: "12px",
                                                    lineHeight: "1.7"
                                                }}
                                            >

                                                ✏️ {item.column}
                                                {" → "}
                                                {item.suggested_name}

                                            </p>

                                        )
                                    )
                                )
                        }

                    </div>

                </div>

                <DownloadCenter />

                <div
                    style={{
                        display: "grid",
                        gridTemplateColumns: "1fr 1fr",
                        gap: "20px",
                        marginTop: "38px"
                    }}
                >

                    <LogViewer logs={logs} />

                    <MigrationHistory />

                </div>

            </div>

        </div >

    );

}

export default Dashboard;

