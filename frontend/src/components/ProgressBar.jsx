function ProgressBar({ progress }) {
    return (
        <div
            style={{
                width: "100%",
                height: "40px",
                background: "#1E3A5F",
                borderRadius: "12px",
                overflow: "hidden",
                position: "relative",
                boxShadow: "0 4px 12px rgba(0,0,0,0.3)"
            }}
        >
            <div
                style={{
                    width: `${progress}%`,
                    height: "100%",
                    background: "#22C55E",
                    transition: "0.5s"
                }}
            />

            <div
                style={{
                    position: "absolute",
                    top: "50%",
                    left: "50%",
                    transform: "translate(-50%, -50%)",
                    color: "white",
                    fontWeight: "700",
                    fontSize: "20px",
                    textShadow: "0px 0px 6px black"
                }}
            >
                {progress}%
            </div>
        </div>
    );
}

export default ProgressBar;