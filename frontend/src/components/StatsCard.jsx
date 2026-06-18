function StatsCard({ title, value }) {
    return (
        <div
            style={{
                background: "#13294B",
                borderRadius: "12px",
                padding: "25px",
                width: "100%",
                minHeight: "140px",
                display: "flex",
                flexDirection: "column",
                justifyContent: "center",
                alignItems: "center",
                boxShadow: "0 4px 12px rgba(0,0,0,0.3)"
            }}
        >
            <h2
                style={{
                    fontSize: "30px",
                    fontWeight: "600",
                    color: "#E2E8F0",
                    marginBottom: "12px",
                    display: "flex",
                    alignItems: "center",
                    gap: "8px"
                }}
            >
                {title}
            </h2>

            <h1
                style={{
                    fontSize: "54px",
                    fontWeight: "700",
                    color: "white",
                    margin: 0
                }}
            >
                {value}
            </h1>
        </div>
    );
}

export default StatsCard;