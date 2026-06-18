import axios from "axios";

const API_URL = "http://127.0.0.1:8000";

export const getReport = async () => {

    const response = await axios.get(
        `${API_URL}/migration/report`
    );

    return response.data;
};

export const getLogs = async () => {

    const response = await axios.get(
        `${API_URL}/migration/logs`
    );

    return response.data;
};

export const testConnection = async (
    connectionData
) => {

    const response =
        await axios.post(
            `${API_URL}/migration/test-connection`,
            connectionData
        );

    return response.data;
};

export const startMigration = async (
    connectionData
) => {

    const response =
        await axios.post(
            `${API_URL}/migration/start`,
            connectionData
        );

    return response.data;
};

export const getProgress = async () => {

    const response =
        await axios.get(
            `${API_URL}/migration/progress`
        );

    return response.data;
};

export const resumeMigration = async () => {

    const response =
        await axios.post(
            `${API_URL}/migration/resume`
        );

    return response.data;
};

export const resetTable = async (tableName) => {

    const response = await axios.post(
        `${API_URL}/migration/reset-table/${tableName}`
    );

    return response.data;
};

export const getSchemaMapping = async () => {

    const response = await axios.get(
        `${API_URL}/migration/schema-mapping`
    );

    return response.data;
};

export const getSchemaAnalysis =
    async () => {

        const response =
            await axios.get(
                `${API_URL}/migration/schema-analysis`
            );

        return response.data;
    };

export const getHistory = async () => {

    const response = await axios.get(
        `${API_URL}/migration/history`
    );

    return response.data;
};

export const getValidationReport = async () => {
    const response = await fetch(
        "http://localhost:8000/migration/validation-report"
    );

    return response.json();
};

export const getAuditReport = async () => {
    const response = await fetch(
        "http://localhost:8000/migration/audit-report"
    );

    return response.json();
};

export const getChecksumReport = async () => {
    const response = await fetch(
        "http://localhost:8000/migration/checksum-report"
    );

    return response.json();
};

export const getReconciliationReport = async () => {
    const response = await fetch(
        "http://localhost:8000/migration/reconciliation-report"
    );

    return response.json();
};

export const getMetricsReport = async () => {
    const response = await fetch(
        "http://localhost:8000/migration/metrics-report"
    );

    return response.json();
};

export const getAuditTrail = async () => {
    const response = await fetch(
        "http://localhost:8000/migration/audit-trail"
    );

    return response.json();
};

export const getMigrationHistory =
    async () => {

        const response = await axios.get(

            "http://localhost:8000/migration/migration-history"

        );

        return response.data;

    };

export const createSchedule =
    async (scheduleData) => {

        const response = await axios.post(

            "http://localhost:8000/migration/schedule",

            scheduleData

        );

        return response.data;

    };

export const getSchedulerLogs =
    async () => {

        const response =
            await axios.get(

                "http://localhost:8000/migration/scheduler/logs"

            );

        return response.data;

    };

export const getProfiles = async () => {

    const response = await axios.get(
        "http://localhost:8000/migration/profiles"
    );

    return response.data;
};